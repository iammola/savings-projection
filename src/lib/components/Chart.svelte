<script lang="ts">
  import { AnnotationLine, AnnotationRange, Area, Axis, Chart, Grid, Layer, LinearGradient } from "layerchart";

  interface Props {
    months: MonthData[];
    errorRange: Pick<MonthData, "idx"> | undefined;
    currencyFormatter: Intl.NumberFormat;
  }

  const { months, errorRange }: Props = $props();

  const data = $derived.by(() => {
    const createAccessor = (path: string): ((obj: unknown) => number | undefined) => {
      const keys = path.split(".");

      return (obj: unknown) => {
        for (const key of keys) {
          if (obj == null || typeof obj !== "object") break;
          obj = obj[key as keyof typeof obj];
        }

        return typeof obj === "number" ? obj : undefined;
      };
    };

    const accessors = (["endingBalance", "total.invested"] satisfies MonthDataPath[]).map(createAccessor);

    return months.reduce<Array<Array<Record<"index" | "value", number>>>>(
      (acc, month, index) => {
        accessors.forEach((access, i) => {
          const value = access(month);
          if (typeof value === "number") acc[i].push({ index: index, value });
        });
        return acc;
      },
      Array.from({ length: accessors.length }, () => []),
    );
  });

  const flatData = $derived(data.flat());

  const x = "index" satisfies keyof (typeof flatData)[number];
  const y = "value" satisfies keyof (typeof flatData)[number];

  // @ts-expect-error Intl.DurationFormat (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat) not typed
  const timeFormatter = new Intl.DurationFormat();

  function formatMonthTick(v: unknown) {
    if (typeof v !== "number" || !Number.isInteger(v) || v === 0) return "";
    return timeFormatter
      .formatToParts({ years: Math.trunc(v / 12), months: v % 12 })
      .reduce((acc: string, cur: { value: string }) => acc + (cur.value.trim() === "," ? "\n" : cur.value), "");
  }
</script>

<div class="w-full flex-1 rounded-t-lg bg-linear-to-b from-[#3b6978] to-[#204051]">
  <Chart {data} {flatData} {x} {y} yNice>
    <Layer type="svg">
      <Axis
        tickMarks={false}
        tickSpacing={125}
        placement="bottom"
        tickLabelProps={{ dx: -10, verticalAnchor: "start" }}
        format={formatMonthTick}
      />
      <Grid
        x={{ class: "stroke-[#edffea]/20 [stroke-dasharray:1,3]" }}
        xTicks={(scale) => {
          const ticks = scale.ticks?.() ?? [];
          return ticks.filter((tick) => tick !== ticks[0] && tick !== ticks[ticks.length - 1]);
        }}
      />
      {@const gradients = ["from-[#edffea]/80 to-[#edffea]/5", "from-[#edffea]/80 to-[#edffea]/5"]}
      {#each data as area, index}
        <LinearGradient class={gradients[index]} vertical>
          {#snippet children({ gradient })}
            <Area data={area} line={{ stroke: gradient, class: "stroke-1" }} fill={gradient} fillOpacity={0.4} />
          {/snippet}
        </LinearGradient>
      {/each}
      {#if errorRange != null}
        <AnnotationRange x={[errorRange.idx, null]} class="fill-[#cc2936]/50" />
        <AnnotationLine x={errorRange.idx} props={{ line: { class: "[stroke-dasharray:2,2] stroke-[#cc2936]" } }} />
      {/if}
    </Layer>
  </Chart>
</div>
