<script lang="ts">
  import {
    AnnotationLine,
    AnnotationRange,
    Area,
    AreaChart,
    Axis,
    Grid,
    RectClipPath,
    Tooltip,
    type AreaProps,
    type SeriesData,
  } from "layerchart";
  import { BanknoteXIcon, PercentIcon, TrendingDownIcon, TrendingUpIcon } from "@lucide/svelte";
  import type { Component } from "svelte";

  import { cn } from "$lib/utils";
  import { format } from "$lib/shared.svelte";
  import { Separator } from "$lib/components/shadcn/separator";

  interface Props {
    months: MonthData[];
    errorRange: Pick<MonthData, "idx"> | undefined;
  }

  const { months, errorRange }: Props = $props();

  const CHART_ROUNDED = 8; // theme(radius.lg)

  const series = {
    invested: { key: "invested", value: (d) => d.total.invested, label: "Total Invested", color: "#00B5FF" },
    balance: { key: "balance", value: (d) => d.total.interest, label: "Total Balance", color: "#FFBE00" },
  } satisfies Record<string, SeriesData<MonthData, Component<AreaProps>>>;

  const monthsToDuration = (months: number) => ({ years: Math.trunc(months / 12), months: months % 12 });

  function formatMonthTick(v: unknown) {
    if (typeof v !== "number" || !Number.isInteger(v) || v === 0) return "";
    return format.time
      .formatToParts(monthsToDuration(v))
      .reduce(
        (acc: string, cur: { value: string; type: "group" | "literal" }) =>
          acc + (cur.type === "literal" && cur.value.trim() === "," ? "\n" : cur.value),
        "",
      );
  }
</script>

<div class="size-full" style:border-radius={`${CHART_ROUNDED}px`}>
  <AreaChart x="idx" padding={0} rule={false} data={months} seriesLayout="stack" series={Object.values(series)}>
    {#snippet axis()}
      <Axis tickMarks={false} tickSpacing={100} placement="bottom" format={formatMonthTick} />
    {/snippet}
    {#snippet grid()}
      <Grid
        x={{ class: "stroke-foreground/20 [stroke-dasharray:1,3]" }}
        xTicks={(scale) => {
          const domain = scale.domain();
          return scale.ticks?.().filter((tick) => Number.isInteger(tick) && !domain.includes(tick));
        }}
      />
    {/snippet}
    {#snippet marks({ series, getAreaProps, context })}
      <RectClipPath width={context.width} height={context.height} rx={CHART_ROUNDED} ry={CHART_ROUNDED}>
        {#each series as s, i (s.key)}
          <Area {...getAreaProps(s, i)} />
        {/each}
      </RectClipPath>
    {/snippet}
    {#snippet aboveMarks()}
      {#if errorRange != null}
        <AnnotationRange x={[errorRange.idx, null]} class="fill-[#cc2936]/50" />
        <AnnotationLine x={errorRange.idx} props={{ line: { class: "[stroke-dasharray:2,2] stroke-[#cc2936]" } }} />
      {/if}
    {/snippet}
    {#snippet tooltip({ context })}
      <Tooltip.Root variant="none" anchor="top" contained="window">
        {#snippet children()}
          {@const data = context.tooltip.data!}
          {@const isDepleted = errorRange != null && data.idx >= errorRange.idx}
          {@const netChange = data.endingBalance - data.startingBalance}
          {@const growthRate =
            data.endingBalance === 0 ? 0
            : data.startingBalance === 0 ? 1
            : netChange / data.startingBalance}
          <div
            class={cn(
              "w-max max-w-sm min-w-xs space-y-3 rounded-lg bg-background/80 p-3 text-foreground shadow backdrop-blur-xs",
              { "border border-red-700 bg-red-100/80": isDepleted },
            )}
          >
            {#if isDepleted}
              <p class="flex gap-2 rounded-md bg-red-200/75 p-2 text-xs font-medium text-red-700">
                <BanknoteXIcon class="size-4" /> Account Depleted - No funds available for interest growth
              </p>
            {/if}
            <div class="flex items-center justify-between">
              <span class={cn("text-sm font-semibold", { "text-red-700": isDepleted })}>
                {#if data.idx === 0}
                  After 1 Day
                {:else}
                  After {format.time.format(monthsToDuration(data.idx))}
                {/if}
              </span>
              <span
                class={cn("flex items-center gap-2 text-xs [&_svg]:size-4", {
                  "text-red-700": netChange < 0,
                  "text-green-600": netChange > 0,
                })}
              >
                {#if netChange > 0}
                  <TrendingUpIcon /> +
                {:else if netChange < 0}
                  <TrendingDownIcon />
                {/if}
                {format.percent.format(growthRate)}
              </span>
            </div>
            <Separator class={cn({ "bg-red-700": isDepleted })} />
            <div class="grid grid-cols-[max-content_minmax(0,1fr)_max-content] items-center gap-3">
              <div class="col-span-full grid grid-cols-subgrid items-center">
                <div class="grid place-items-center">
                  <div style:background-color={series.balance.color} class="size-3 rounded-full"></div>
                </div>
                <span class="min-w-max text-sm font-medium text-muted-foreground">{series.balance.label}</span>
                <span class="text-right text-xs">
                  {format.currency.format(data.endingBalance)} @ {format.percent.format(data.inMonth.rate)}
                </span>
              </div>
              <div class="col-span-full grid grid-cols-subgrid items-center">
                <div class="grid place-items-center">
                  <div style:background-color={series.invested.color} class="size-3 rounded-full"></div>
                </div>
                <span class="min-w-max text-sm font-medium text-muted-foreground">{series.invested.label}</span>
                <span class="text-right text-xs">
                  {format.currency.format(data.total.invested)}
                </span>
              </div>
              <div class="col-span-full grid grid-cols-subgrid items-center">
                <div class="grid place-items-center">
                  <PercentIcon class="size-4 text-green-600" />
                </div>
                <span class="min-w-max text-sm font-medium text-muted-foreground">Total Interest Earned</span>
                <span class={cn("text-right text-xs", { "text-green-600": data.total.interest > 0 })}>
                  {data.total.interest > 0 ? "+" : ""}{format.currency.format(data.total.interest)}
                </span>
              </div>
            </div>
            <Separator class={cn({ "bg-red-700": isDepleted })} />
            <div class="flex items-center justify-between">
              <span class="text-sm text-muted-foreground">Net Change</span>
              <span
                class={cn("text-right text-xs font-medium", {
                  "text-red-700": netChange < 0,
                  "text-green-600": netChange > 0,
                })}
              >
                {netChange > 0 ? "+" : ""}{format.currency.format(netChange)}
              </span>
            </div>
          </div>
        {/snippet}
      </Tooltip.Root>
    {/snippet}
  </AreaChart>
</div>
