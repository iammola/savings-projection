<script lang="ts">
  import { Input } from "$lib/components/shadcn/input";
  import { FormLabel } from "$lib/components/shadcn/label";

  import Chart from "./Chart.svelte";
  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  import { currencyFormatter } from "$lib/shared";

  import type { BONUS_INTEREST_TYPE } from "$lib/components/BonusRules/types";

  let initialBalance = $state(2500);
  let monthlyWithdrawal = $state(0);
  let monthlyContribution = $state(300);
  let totalMonths = $state(12 /* 1 Year */);
  let interestTiers = $state([
    { min: 0, rate: 0.25, tierId: Math.random().toString(36) },
    { min: 10e3, rate: 0.3, tierId: Math.random().toString(36) },
    { min: 25e3, rate: 0.55, tierId: Math.random().toString(36) },
    { min: 10e4, rate: 0.8, tierId: Math.random().toString(36) },
    { min: 5e5, rate: 1, tierId: Math.random().toString(36) },
  ]);

  let bonusInterest = $state<BONUS_INTEREST_TYPE[]>([
    { type: "IN_ACCOUNT_AGE", rate: 5, data: { minMonth: 0, maxMonth: 2 } }, // Between the first 3 months, give an additional 5% interest
    { type: "MIN_CONTRIBUTION", rate: 0.25, data: { amount: 200 } }, // Give an additional 0.25% interest if the closing balance is 200 more than the previous month
  ]);

  const data = $derived.by(() => {
    const result: MonthData[] = [
      {
        idx: 0,
        startingBalance: 0,
        endingBalance: initialBalance,
        inMonth: { interest: 0, invested: initialBalance, rate: 0 },
        total: { interest: 0, invested: initialBalance },
      },
    ];
    let previous = result[0];

    let completed = true;
    const monthInvested = monthlyContribution - monthlyWithdrawal;

    for (let monthIndex = 1; monthIndex <= totalMonths; monthIndex++) {
      const interestRate = [
        interestTiers.findLast((tier) => tier.min < previous.endingBalance)?.rate ?? 0,
        ...bonusInterest.flatMap((i) => {
          switch (i.type) {
            case "IN_ACCOUNT_AGE":
              if (i.data.minMonth != null && monthIndex < i.data.minMonth) return [];
              if (i.data.maxMonth != null && monthIndex > i.data.maxMonth) return [];
              break;
            case "MIN_CONTRIBUTION":
              if (monthlyContribution < i.data.amount) return [];
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

  const finalMonth = $derived(data.result.at(-1));
  const depletedMonth = $derived(data.completed ? undefined : data.result.at(-2));

  $effect(() => {
    const cb = (e: MediaQueryList | MediaQueryListEvent) =>
      e.matches ? document.body.classList.add("dark") : document.body.classList.remove("dark");
    const darkModePreference = window.matchMedia("(prefers-color-scheme: dark)");

    cb(darkModePreference);
    darkModePreference.addEventListener("change", cb);
    return () => darkModePreference.removeEventListener("change", cb);
  });
</script>

<div class="grid h-screen w-screen grid-cols-[25%_minmax(0,1fr)] gap-8 bg-background p-8 *:min-h-0">
  <aside class="flex flex-col gap-4 overflow-y-auto rounded-lg bg-secondary/50 p-3">
    <div>
      <FormLabel class="text-foreground">Initial Balance</FormLabel>
      <CurrencyInput bind:value={initialBalance} min={0} />
    </div>
    <div>
      <FormLabel class="text-foreground">Monthly Contribution</FormLabel>
      <CurrencyInput bind:value={monthlyContribution} min={0} />
    </div>
    <div>
      <FormLabel class="text-foreground">Monthly Withdrawals</FormLabel>
      <CurrencyInput bind:value={monthlyWithdrawal} min={0} />
      {#if monthlyWithdrawal > monthlyContribution}
        <p class="text-xs text-muted-foreground">The simulation may not complete</p>
      {/if}
    </div>
    <div>
      <FormLabel class="text-foreground">Total Months</FormLabel>
      <Input type="number" bind:value={totalMonths} min={2} />
    </div>
    <div>
      <FormLabel class="text-foreground">Interest Tiers</FormLabel>
      <InterestTiers bind:value={interestTiers} />
    </div>
    <div>
      <FormLabel class="text-foreground">Bonus Rules</FormLabel>
      <BonusRules bind:value={bonusInterest} />
    </div>
  </aside>
  <main class="flex flex-col items-center justify-center-safe gap-4 *:min-h-0">
    <h1 class="w-full text-2xl font-bold text-foreground">Savings Projection</h1>
    <div class="w-full flex-1 *:bg-secondary/50">
      <Chart months={data.result} errorRange={depletedMonth} />
    </div>
    {#if finalMonth != null}
      <h3 class="w-full pt-4 text-2xl font-bold text-foreground">Summary</h3>
      <div class="flex w-full flex-wrap gap-4">
        {#snippet children()}
          {@const cards = [
            { title: "Final Balance", value: finalMonth.endingBalance },
            { title: "Total Contributions", value: finalMonth.total.invested },
            { title: "Total Interest Earned", value: finalMonth.total.interest },
          ]}
          {#each cards as { title, value } (title)}
            <div class="flex-1 space-y-2 rounded-lg border bg-secondary/50 p-4">
              <h4 class="text-sm text-muted-foreground">{title}</h4>
              <p class="text-3xl font-bold tracking-wide text-foreground">{currencyFormatter.format(value)}</p>
            </div>
          {/each}
        {/snippet}
        {@render children()}
      </div>
    {/if}
  </main>
</div>
