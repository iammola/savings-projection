<script lang="ts" generics="Data">
  import { Area, Axis, Chart, Layer, LinearGradient, Text } from "layerchart";

  interface Props {
    data: Data[];
  }

  const { data }: Props = $props();
</script>

<div class="w-full flex-1 rounded-lg bg-linear-to-b from-[#3b6978] to-[#204051]">
  <Chart {data} x="idx" y="balance" yNice>
    <Layer type="svg">
      <Axis
        placement="bottom"
        grid={{ style: "stroke-dasharray: 2" }}
        rule
        format={(v) => (Number.isInteger(v) ? `Month ${v + 1}` : "")}
        ticks={(scale) => scale.ticks?.().slice(0, -1)}
      >
        {#snippet tickLabel({ props })}
          <Text {...props} textAnchor="start" />
        {/snippet}
      </Axis>
      <LinearGradient class="from-[#edffea] to-[#edffea]/10" vertical>
        {#snippet children({ gradient })}
          <Area line={{ class: "stroke-1", stroke: gradient }} fill={gradient} />
        {/snippet}
      </LinearGradient>
    </Layer>
  </Chart>
</div>
