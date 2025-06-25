<script lang="ts">
  import { FormLabel } from "$lib/components/shadcn/label";

  import Chart from "$lib/components/Chart.svelte";
  import { Input } from "$lib/components/shadcn/input";
  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  import type { BONUS_INTEREST_TYPE } from "$lib/components/BonusRules/types";

  const currencyFormatter = new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "CAD",
    trailingZeroDisplay: "stripIfInteger",
  });

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
      { idx: 0, invested: initialBalance, interestEarnedInMonth: 0, totalInterestEarned: 0, balance: initialBalance },
    ];
    let previous = result[0];

    for (let monthIndex = 1; monthIndex <= totalMonths; monthIndex++) {
      const interestRate = [
        interestTiers.findLast((tier) => tier.min < previous.balance)?.rate ?? 0,
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

      const interestEarned = +(previous.balance * interestRate).toFixed(2);

      const totalInvested = +(previous.invested + monthlyContribution - monthlyWithdrawal).toFixed(2);
      const totalInterestEarned = +(previous.totalInterestEarned + interestEarned).toFixed(2);
      const totalBalance = totalInterestEarned + totalInvested;

      previous = {
        idx: monthIndex,
        balance: totalBalance,
        invested: totalInvested,
        interestEarnedInMonth: interestEarned,
        totalInterestEarned: totalInterestEarned,
      };

      result.push(previous);
    }

    return result;
  });
  const finalMonth = $derived(data.at(-1));

  interface MonthData {
    idx: number;
    interestEarnedInMonth: number;
    totalInterestEarned: number;
    invested: number;
    balance: number;
  }
</script>

<div class="grid h-screen w-screen grid-cols-[25%_minmax(0,1fr)] gap-8 p-8 *:min-h-0">
  <aside class="flex flex-col gap-4 overflow-y-auto rounded-lg bg-slate-50 p-3">
    <div>
      <FormLabel>Initial Balance</FormLabel>
      <CurrencyInput bind:value={initialBalance} min={0} />
    </div>
    <div>
      <FormLabel>Monthly Contribution</FormLabel>
      <CurrencyInput bind:value={monthlyContribution} min={0} />
    </div>
    <div>
      <FormLabel>Monthly Withdrawals</FormLabel>
      <CurrencyInput bind:value={monthlyWithdrawal} min={0} />
    </div>
    <div>
      <FormLabel>Total Months</FormLabel>
      <Input type="number" bind:value={totalMonths} min={2} />
    </div>
    <div>
      <FormLabel>Interest Tiers</FormLabel>
      <InterestTiers bind:value={interestTiers} />
    </div>
    <div>
      <FormLabel>Bonus Rules</FormLabel>
      <BonusRules bind:value={bonusInterest} />
    </div>
  </aside>
  <main class="flex flex-col items-center justify-center-safe gap-4 *:min-h-0">
    <h1 class="w-full text-2xl font-bold">Savings Projection</h1>
    <Chart {data} x="idx" y="startingBalance" />
    {#if finalMonth != null}
      <h3 class="pb2 w-full pt-4 text-2xl font-bold">Summary</h3>
      <div class="flex w-full flex-wrap gap-4">
        {#each [{ title: "Final Balance", value: finalMonth.balance }, { title: "Total Contributions", value: finalMonth.invested }, { title: "Total Interest Earned", value: finalMonth.totalInterestEarned }] as { title, value } (title)}
          <div class="flex-1 space-y-2 rounded-lg border p-4">
            <h4 class="text-sm text-muted-foreground">{title}</h4>
            <p class="text-3xl font-bold tracking-wide">{currencyFormatter.format(value)}</p>
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>
