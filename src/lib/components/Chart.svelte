<script lang="ts">
  import { AnnotationLine, AnnotationRange, AreaChart, Axis, Grid } from "layerchart";

  interface Props {
    months: MonthData[];
    errorRange: Pick<MonthData, "idx"> | undefined;
    currencyFormatter: Intl.NumberFormat;
  }

  const { months, errorRange }: Props = $props();

  // @ts-expect-error Intl.DurationFormat (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat) not typed
  const timeFormatter = new Intl.DurationFormat(undefined, { style: "long" });
  const monthsToDuration = (months: number) => ({ years: Math.trunc(months / 12), months: months % 12 });

  function formatMonthTick(v: unknown) {
    if (typeof v !== "number" || !Number.isInteger(v) || v === 0) return "";
    return timeFormatter
      .formatToParts(monthsToDuration(v))
      .reduce((acc: string, cur: { value: string }) => acc + (cur.value.trim() === "," ? "\n" : cur.value), "");
  }
</script>

<div class="size-full rounded-t-lg bg-gray-50/50">
  <AreaChart
    x="idx"
    padding={0}
    rule={false}
    data={months}
    seriesLayout="stack"
    series={[
      { key: "invested", value: (d) => d.total.invested, label: "Total Invested", color: "#00B5FF" },
      { key: "balance", value: (d) => d.total.interest, label: "Total Balance", color: "#FFBE00" },
    ]}
  >
    {#snippet axis()}
      <Axis tickMarks={false} tickSpacing={100} placement="bottom" format={formatMonthTick} />
    {/snippet}
    {#snippet grid()}
      <Grid
        x={{ class: "stroke-black/20 [stroke-dasharray:1,3]" }}
        xTicks={(scale) => {
          const ticks = scale.ticks?.() ?? [];
          return ticks.filter((tick) => tick !== ticks[0] && tick !== ticks[ticks.length - 1]);
        }}
      />
    {/snippet}
    {#snippet aboveMarks()}
      {#if errorRange != null}
        <AnnotationRange x={[errorRange.idx, null]} class="fill-[#cc2936]/50" />
        <AnnotationLine x={errorRange.idx} props={{ line: { class: "[stroke-dasharray:2,2] stroke-[#cc2936]" } }} />
      {/if}
    {/snippet}
  </AreaChart>
</div>
