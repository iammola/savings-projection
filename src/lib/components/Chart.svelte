<script lang="ts" generics="Data">
  import { Area, Axis, Chart, Layer, LinearGradient, Text } from "layerchart";

  interface Props {
    data: Data[];
  }

  const { data }: Props = $props();

  // @ts-expect-error Intl.DurationFormat (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat) not typed
  const timeFormatter = new Intl.DurationFormat(undefined);

  function formatMonthTick(v: unknown) {
    if (typeof v !== "number" || !Number.isInteger(v) || v === 0) return "";
    return timeFormatter
      .formatToParts({ years: Math.trunc(v / 12), months: v % 12 })
      .reduce((acc: string, cur: { value: string }) => acc + (cur.value.trim() === "," ? "\n" : cur.value), "");
  }
</script>

<div class="w-full flex-1 rounded-lg bg-linear-to-b from-[#3b6978] to-[#204051]">
  <Chart {data} x="idx" y="balance" yNice>
    <Layer type="svg">
      <Axis
        tickMarks={false}
        tickSpacing={125}
        placement="bottom"
        grid={{ style: "stroke-dasharray: 1,3", class: "stroke-[#edffea]/20" }}
        format={formatMonthTick}
      >
        {#snippet tickLabel({ props })}
          <Text {...props} textAnchor="start" />
        {/snippet}
      </Axis>
      <LinearGradient class="from-[#edffea]/10 to-[#edffea]/50" vertical>
        {#snippet children({ gradient })}
          <Area line={{ class: "stroke-1", stroke: gradient }} fill={gradient} />
        {/snippet}
      </LinearGradient>
    </Layer>
  </Chart>
</div>
