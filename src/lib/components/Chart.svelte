<script lang="ts" generics="Type extends ChartType">
  import { Chart } from "chart.js/auto";

  import type { HTMLCanvasAttributes } from "svelte/elements";
  import type { ChartData, ChartOptions, ChartType, Plugin } from "chart.js";

  interface Props extends HTMLCanvasAttributes {
    type: Type;
    data: ChartData<Type>;
    options?: ChartOptions<Type>;
    plugins?: Plugin<Type>[];
  }

  const { type, data, options, plugins, ...rest }: Props = $props();

  let canvasElem: HTMLCanvasElement;
  let chart: Chart<Type>;

  $effect(() => {
    chart = new Chart(canvasElem, { type, data, options, plugins });
    return () => chart.destroy();
  });

  $effect(() => {    
    if (chart) {
      chart.data = data;
      chart.update();
    }
  });
</script>

<canvas bind:this={canvasElem} {...rest}></canvas>
