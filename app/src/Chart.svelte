<script lang="ts">
  import { TrashIcon } from "@lucide/svelte";

  import { Button } from "$lib/components/shadcn/button";
  import { cn } from "$lib/utils";

  import Graph from "./Graph.svelte";

  let { data, layout, title }: Props = $props();

  const finalMonth = $derived(data.result.at(-1));
  const depletedMonth = $derived(data.completed ? undefined : data.result.at(-2));

  interface Props {
    title: string;
    layout: string | undefined;
    data: { result: MonthData[]; completed: boolean };
  }
</script>

<div class={cn(layout, "@container")}>
  <div class="flex h-full flex-col items-center justify-center-safe gap-2 *:min-h-0 *:w-full">
    <div class="flex gap-2">
      <h1 class="grow text-2xl font-bold text-foreground">{title}</h1>
      <Button size="icon" variant="ghost">
        <TrashIcon />
      </Button>
    </div>
    <div class="flex-1 *:bg-secondary/50">
      <Graph months={data.result} errorRange={depletedMonth} />
    </div>
    <!-- {#if finalMonth != null}
      <h3 class="pt-4 text-2xl font-bold text-foreground">Summary</h3>
      <div class="flex flex-col flex-wrap gap-2 @xl:flex-row @xl:gap-4">
        {#snippet children()}
          {@const cards = [
            { title: "Final Balance", value: finalMonth.endingBalance },
            { title: "Total Contributions", value: finalMonth.total.invested },
            { title: "Total Interest Earned", value: finalMonth.total.interest },
          ]}
          {#each cards as { title, value } (title)}
            <div
              class="flex flex-1 items-center justify-between gap-x-4 gap-y-2 rounded-lg border bg-secondary/50 p-2 @xl:flex-col @xl:items-start @xl:p-4"
            >
              <h4 class="min-w-max text-sm text-muted-foreground">{title}</h4>
              <p class="text-lg font-bold tracking-wide text-foreground @xl:text-3xl">
                {currencyFormatter.format(value)}
              </p>
            </div>
          {/each}
        {/snippet}
        {@render children()}
      </div>
    {/if} -->
  </div>
</div>
