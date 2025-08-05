<script lang="ts">
  import { CogIcon } from "@lucide/svelte";
  import { MediaQuery, SvelteMap } from "svelte/reactivity";

  import { cn } from "$lib/utils";

  import * as Drawer from "$lib/components/shadcn/drawer";
  import { Button, buttonVariants } from "$lib/components/shadcn/button";

  import Chart from "./Chart.svelte";
  import Config from "./Config.svelte";

  const chartLayouts = [
    [{ layout: cn("grid-cols-1 grid-rows-1") }],
    [{ layout: cn("grid-cols-2 grid-rows-1") }, { layout: cn("grid-rows-2 grid-cols-1") }],
    [
      { layout: cn("grid-rows-3 grid-cols-1") },
      { layout: cn("grid-cols-3 grid-rows-1") },
      { layout: cn("grid-cols-2 grid-rows-2"), order: [cn("col-start-1 row-start-1 row-span-2")] },
      { layout: cn("grid-cols-2 grid-rows-2"), order: [cn("col-start-1 row-start-2 col-span-2")] },
      { layout: cn("grid-cols-2 grid-rows-2"), order: [cn("col-start-1 row-start-1 col-span-2")] },
      { layout: cn("grid-cols-2 grid-rows-2"), order: [cn("col-start-2 row-start-1 row-span-2")] },
    ],
    [
      { layout: cn("grid-cols-2 grid-rows-2") },
      { layout: cn("grid-cols-4 grid-rows-1") },
      { layout: cn("grid-cols-1 grid-rows-4") },
      { layout: cn("grid-cols-2 grid-rows-3"), order: [cn("col-start-1 row-start-1 row-span-3")] },
      { layout: cn("grid-cols-2 grid-rows-3"), order: [cn("col-start-2 row-start-1 row-span-3")] },
      { layout: cn("grid-cols-3 grid-rows-2"), order: [cn("col-start-1 row-start-1 col-span-3")] },
      {
        layout: cn("grid-cols-2 grid-rows-3"),
        order: [cn("col-start-1 row-start-2 col-span-3"), cn("col-start-1 row-start-3 col-span-3")],
      },
      {
        layout: cn("grid-cols-3 grid-rows-2"),
        order: [cn("col-start-1 row-start-1 row-span-3"), cn("col-start-2 row-start-1 row-span-3")],
      },
    ],
  ];

  let chartNames = $state<string[]>([]);
  let chartOverrides = new SvelteMap<string, Partial<ChartConfig>>([]);
  let chartConfig = $state<ChartConfig>({
    initialBalance: 25000,
    withdrawals: 0,
    contribution: 300,
    period: 12,
    tiers: [
      { min: 0, rate: 0.25, tierId: Math.random().toString(36) },
      { min: 10e3, rate: 0.3, tierId: Math.random().toString(36) },
      { min: 25e3, rate: 0.55, tierId: Math.random().toString(36) },
      { min: 10e4, rate: 0.8, tierId: Math.random().toString(36) },
      { min: 5e5, rate: 1, tierId: Math.random().toString(36) },
    ],
    bonuses: [],
  });

  let selectedLayoutIdx = $state(0);

  const possibleLayouts = $derived(chartLayouts[chartNames.length - 1]);
  const selectedLayout = $derived(
    possibleLayouts == null ? undefined : (possibleLayouts[selectedLayoutIdx] ?? possibleLayouts[0]),
  );

  const chartData = $derived(
    chartNames.map((id) => {
      const resolvedConfig = { ...chartConfig, ...chartOverrides.get(id) };
      resolvedConfig.period = Math.max(2, resolvedConfig.period);

      let previous: MonthData = {
        idx: 0,
        startingBalance: 0,
        endingBalance: resolvedConfig.initialBalance,
        inMonth: { interest: 0, invested: resolvedConfig.initialBalance, rate: 0 },
        total: { interest: 0, invested: resolvedConfig.initialBalance },
      };
      const result: MonthData[] = [previous];

      let completed = true;
      const monthInvested = resolvedConfig.contribution - resolvedConfig.withdrawals;

      for (let monthIndex = 1; monthIndex <= resolvedConfig.period; monthIndex++) {
        const interestRate = [
          resolvedConfig.tiers.findLast((tier) => tier.min < previous.endingBalance)?.rate ?? 0,
          ...resolvedConfig.bonuses.flatMap((i) => {
            switch (i.type) {
              case "IN_ACCOUNT_AGE":
                if (i.data.minMonth != null && monthIndex < i.data.minMonth) return [];
                if (i.data.maxMonth != null && monthIndex > i.data.maxMonth) return [];
                break;
              case "MIN_CONTRIBUTION":
                if (resolvedConfig.contribution < i.data.amount) return [];
                break;
            }

            return i.rate;
          }),
        ].reduce((acc, cur) => acc + cur / (12 * 100), 0);

        const monthInterest = previous.endingBalance * interestRate;

        // Removes whatever is left in account regardless of it being enough. So nothing else to build interest off
        const totalInterest = previous.total.interest + monthInterest;
        const totalInvested = Math.max(0, previous.total.invested + monthInvested);

        const endingBalance = Math.max(0, previous.endingBalance + monthInterest + monthInvested);

        previous = {
          idx: monthIndex,
          startingBalance: previous.endingBalance,
          endingBalance,
          inMonth: { interest: monthInterest, invested: monthInvested, rate: interestRate * 12 },
          total: { interest: totalInterest, invested: totalInvested },
        };
        result.push(previous);

        if (endingBalance === 0) {
          completed = false;
          result.push({
            idx: monthIndex + 1,
            startingBalance: 0,
            endingBalance: 0,
            inMonth: { interest: 0, invested: previous.inMonth.invested, rate: 0 },
            total: previous.total,
          });

          break;
        }
      }

      return { id, result, completed, resolvedConfig };
    }),
  );

  const canAddChart = $derived(chartNames.length < chartLayouts.length);

  function addChart() {
    if (!canAddChart) return;

    selectedLayoutIdx = 0;

    const name = `Chart ${chartNames.length + 1}`;

    chartNames.push(name);
    chartOverrides.set(name, {});
  }

  const isDarkMode = new MediaQuery("(prefers-color-scheme: dark)");
  $effect(() => {
    if (isDarkMode.current) document.body.classList.add("dark");
    else document.body.classList.remove("dark");
  });

  $effect(() => {
    fetch("/api/extract", {
      method: "POST",
      body: JSON.stringify({ text: "Lady Juliet gazed longingly at the stars, her heart aching for Romeo" }),
      headers: { "Content-Type": "application/json" },
    })
      .then((res) => res.json())
      .then(console.log);
  });
</script>

<Drawer.Root direction="left">
  <Drawer.Content
    class="!inset-2 !left-2 flex max-w-[calc(100%-3rem)] flex-col gap-4 overflow-y-auto rounded-lg border-none bg-secondary p-3"
  >
    <Button disabled={!canAddChart} onclick={addChart}>Add Chart</Button>
    <Config bind:config={chartConfig} overrides={chartOverrides} />
  </Drawer.Content>
  <div class="flex items-center justify-center gap-1 p-1">
    {#each possibleLayouts as { layout, order }, i (`${layout}-${i}`)}
      <button
        type="button"
        data-active={selectedLayoutIdx === i}
        onclick={() => (selectedLayoutIdx = i)}
        class="aspect-square size-9 rounded-full bg-background p-2 text-foreground hover:bg-accent hover:text-accent-foreground data-[active=true]:bg-primary data-[active=true]:text-primary-foreground"
      >
        <div class={cn(layout, "grid size-full overflow-hidden rounded-sm border border-current bg-inherit")}>
          {#each chartNames, i}
            <div class={cn(order?.[i], "size-full bg-inherit outline outline-current")}></div>
          {/each}
        </div>
      </button>
    {/each}
  </div>
  {#if chartData.length > 0}
    <div class="">
      <Drawer.Trigger class={buttonVariants({ size: "sm", variant: "secondary", class: "@xl:hidden" })}>
        <CogIcon /> Configure
      </Drawer.Trigger>
    </div>{/if}
  <div class={cn("grid flex-auto gap-x-5 gap-y-10 bg-background pb-5", selectedLayout?.layout)}>
    {#each chartData as data, i (data.id)}
      <Chart title={chartNames[i]} layout={selectedLayout?.order?.[i]} {data} />
    {:else}
      <div class="flex [grid-area:1/1] items-center justify-center flex-col gap-2">
        Add a Chart to Begin
        <Button disabled={!canAddChart} onclick={addChart}>Add Chart</Button>
      </div>
    {/each}
  </div>
</Drawer.Root>
