<script lang="ts">
  import { CogIcon } from "@lucide/svelte";
  import { MediaQuery } from "svelte/reactivity";

  import { cn } from "$lib/utils";
  import { currencyFormatter } from "$lib/shared";

  import * as Drawer from "$lib/components/shadcn/drawer";
  import { buttonVariants } from "$lib/components/shadcn/button";

  import Chart from "./Chart.svelte";
  import Config from "./Config.svelte";

  const chartConfigs = $state<ChartConfig[]>([
    {
      initialBalance: 2500,
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
      bonuses: [
        { type: "IN_ACCOUNT_AGE", rate: 5, data: { minMonth: 0, maxMonth: 2 } }, // Between the first 3 months, give an additional 5% interest
        { type: "MIN_CONTRIBUTION", rate: 0.25, data: { amount: 200 } }, // Give an additional 0.25% interest if the closing balance is 200 more than the previous month
      ],
    },
  ]);

  const chartData = $derived.by(() => {
    return chartConfigs.map(({ initialBalance, period, withdrawals, contribution, tiers, bonuses }) => {
      period = Math.max(2, period);

      let previous: MonthData = {
        idx: 0,
        startingBalance: 0,
        endingBalance: initialBalance,
        inMonth: { interest: 0, invested: initialBalance, rate: 0 },
        total: { interest: 0, invested: initialBalance },
      };
      const result: MonthData[] = [previous];

      let completed = true;
      const monthInvested = contribution - withdrawals;

      for (let monthIndex = 1; monthIndex <= period; monthIndex++) {
        const interestRate = [
          tiers.findLast((tier) => tier.min < previous.endingBalance)?.rate ?? 0,
          ...bonuses.flatMap((i) => {
            switch (i.type) {
              case "IN_ACCOUNT_AGE":
                if (i.data.minMonth != null && monthIndex < i.data.minMonth) return [];
                if (i.data.maxMonth != null && monthIndex > i.data.maxMonth) return [];
                break;
              case "MIN_CONTRIBUTION":
                if (contribution < i.data.amount) return [];
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

      return { result, completed };
    });
  });

  const isDesktop = new MediaQuery("(min-width: 1024px)");
  const isDarkMode = new MediaQuery("(prefers-color-scheme: dark)");

  $effect(() => {
    if (isDarkMode.current) document.body.classList.add("dark");
    else document.body.classList.remove("dark");
  });
</script>

{#each chartData as data, i}
  {@const finalMonth = data.result.at(-1)}
  {@const depletedMonth = data.completed ? undefined : data.result.at(-2)}
  <Drawer.Root direction="left">
    <div
      class={cn("h-dvh w-dvw bg-background p-5 *:min-h-0", {
        "grid grid-cols-[minmax(max-content,25%)_minmax(0,1fr)] gap-8 p-8": isDesktop.current,
      })}
    >
      {#if isDesktop.current}
        <Config bind:config={chartConfigs[i]} />
      {:else}
        <Drawer.Content class="!w-max max-w-[calc(100%-3rem)]">
          <Config bind:config={chartConfigs[i]} />
        </Drawer.Content>
      {/if}
      <main class="flex h-full flex-col items-center justify-center-safe gap-4 *:min-h-0 *:w-full">
        <div class="flex w-full items-center justify-start gap-4">
          <h1 class="text-2xl font-bold text-foreground">Savings Projection</h1>
          {#if !isDesktop.current}
            <Drawer.Trigger class={buttonVariants({ size: "sm", variant: "secondary" })}>
              <CogIcon /> Configure
            </Drawer.Trigger>
          {/if}
        </div>
        <div class="flex-1 *:bg-secondary/50">
          <Chart months={data.result} errorRange={depletedMonth} />
        </div>
        {#if finalMonth != null}
          <h3 class="pt-4 text-2xl font-bold text-foreground">Summary</h3>
          <div class="flex flex-col flex-wrap gap-2 lg:flex-row lg:gap-4">
            {#snippet children()}
              {@const cards = [
                { title: "Final Balance", value: finalMonth.endingBalance },
                { title: "Total Contributions", value: finalMonth.total.invested },
                { title: "Total Interest Earned", value: finalMonth.total.interest },
              ]}
              {#each cards as { title, value } (title)}
                <div
                  class="flex flex-1 items-center justify-between gap-x-4 gap-y-2 rounded-lg border bg-secondary/50 p-2 lg:flex-col lg:items-start lg:p-4"
                >
                  <h4 class="min-w-max text-sm text-muted-foreground">{title}</h4>
                  <p class="text-lg font-bold tracking-wide text-foreground lg:text-3xl">
                    {currencyFormatter.format(value)}
                  </p>
                </div>
              {/each}
            {/snippet}
            {@render children()}
          </div>
        {/if}
      </main>
    </div>
  </Drawer.Root>
{/each}
