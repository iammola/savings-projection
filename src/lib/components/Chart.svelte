<script lang="ts" generics="Type extends ChartType">
  import { Chart } from "chart.js/auto";

  import { cn } from "$lib/utils";

  import type { HTMLCanvasAttributes } from "svelte/elements";
  import type { ChartData, ChartOptions, ChartType, Defaults, Plugin } from "chart.js";

  interface Props extends HTMLCanvasAttributes {
    type: Type;
    data: ChartData<Type>;
    options?: ChartOptions<Type>;
    plugins?: Plugin<Type>[];
    defaults?: Partial<Defaults>;
  }

  const { type, data, options, plugins, defaults, ...rest }: Props = $props();

  let canvasElem: HTMLCanvasElement;
  let chart: Chart<Type>;

  function deepMerge<T>(left: T, right: T) {
    for (const key in right) {
      if (!Object.prototype.hasOwnProperty.call(right, key)) return;

      const element = right[key];

      if (element != null && typeof element === "object") {
        if (typeof left[key] !== "object") left[key] = {} as never;
        deepMerge(left[key] as Record<string, unknown>, element as Record<string, unknown>);
      } else {
        left[key] = element;
      }
    }
  }

  $effect(() => {
    // For some reason https://stackoverflow.com/a/74362058
    Chart.defaults.devicePixelRatio = 4
    if (defaults != null) deepMerge(Chart.defaults, defaults);

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

<canvas bind:this={canvasElem} {...rest} class={cn(rest.class, "[box-sizing:initial]!")}></canvas>
