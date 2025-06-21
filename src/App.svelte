<script lang="ts">
  import { Tooltip } from "chart.js";
  import { easingEffects } from "chart.js/helpers";

  import { FormLabel } from "$lib/components/shadcn/label";

  import Chart from "$lib/components/Chart.svelte";
  import { Input } from "$lib/components/shadcn/input";
  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  import type { BONUS_INTEREST_TYPE } from "$lib/components/BonusRules/types";

  const totalAnimationDuration = 2e3;
  const animationDuration = (ctx: { dataIndex: number } | { index: number }) =>
    (easingEffects.easeInOutSine(("index" in ctx ? ctx.index : ctx.dataIndex) / data.length) * totalAnimationDuration) /
    data.length;

  const currencyFormatter = new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "CAD",
    trailingZeroDisplay: "stripIfInteger",
  });

  let initialBalance = $state(2500);
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
    const FALLBACK = { label: "", interestEarned: 0, invested: initialBalance, balance: initialBalance };

    return Array.from({ length: totalMonths }).reduce<Array<typeof FALLBACK>>((acc, _, monthIndex) => {
      const previous = acc[monthIndex - 1] ?? FALLBACK;
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

      const nextInvested = +(previous.invested + monthlyContribution).toFixed(2);
      const nextInterestEarned = +(previous.interestEarned + previous.balance * interestRate).toFixed(2);

      return [
        ...acc,
        {
          label: `Month ${monthIndex + 1}`,
          invested: nextInvested,
          interestEarned: nextInterestEarned,
          balance: nextInterestEarned + nextInvested,
        },
      ];
    }, []);
  });
  const finalMonth = $derived(data.at(-1));
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
  <main class="flex flex-col items-center justify-center-safe gap-2 *:min-h-0 *:not-[canvas]:shrink-0">
    <h1 class="w-full text-2xl font-bold">Savings Projection</h1>
    <Chart
      type="line"
      data={{
        labels: data.map((d) => d.label),
        datasets: [
          { label: "Balance", data: data.map((d) => d.balance), normalized: true, pointRadius: 0, borderColor: "#000" },
        ],
      }}
      options={{
        maintainAspectRatio: false,
        animations: {
          x: {
            from: NaN,
            easing: "linear",
            duration: animationDuration,
            delay(ctx) {
              if (ctx.type !== "data" || ctx.mode !== "default") return 0;

              const totalDelay = ctx.dataIndex * 20;
              return totalDelay > totalAnimationDuration ? totalAnimationDuration : totalDelay;
            },
          },
          y: {
            easing: "linear",
            duration: animationDuration,
            from: (ctx) => {
              const dataIndex = "index" in ctx ? (ctx.index as number) : ctx.dataIndex;
              return dataIndex < 1 ?
                  ctx.chart.scales.y.getPixelForValue(100)
                : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[dataIndex - 1].getProps(["y"], true).y;
            },
          },
        },
        scales: {
          y: { display: false },
          x: { grid: { display: false }, border: { display: false }, ticks: { align: "start" } },
        },
        interaction: { intersect: false, mode: "index" },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              footer: ([a]) => `Interest Earned: ${currencyFormatter.format(data[a.dataIndex].interestEarned)}`,
            },
          },
        },
      }}
      plugins={[
        Tooltip,
        {
          id: "hoverLines",
          beforeTooltipDraw(chart, args) {
            args.tooltip.dataPoints.forEach(({ dataset, element }, index) => {
              chart.ctx.save();

              chart.ctx.lineWidth = 2;
              chart.ctx.setLineDash([5, 7]);
              chart.ctx.strokeStyle = typeof dataset.borderColor === "string" ? dataset.borderColor : "#000";

              chart.ctx.beginPath();
              chart.ctx.moveTo(chart.chartArea.left, element.y);
              chart.ctx.lineTo(chart.chartArea.right, element.y);
              chart.ctx.stroke();

              chart.ctx.restore();
            });
          },
        },
      ]}
      defaults={{
        font: {
          family: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif',
          size: 14,
          lineHeight: 1.25 / 0.875,
        },
      }}
    />
    {#if finalMonth != null}
      <h3 class="pb2 w-full pt-4 text-2xl font-bold">Summary</h3>
      <div class="grid w-full grid-cols-3 gap-4">
        <div class="min-w-60 space-y-2 rounded-lg border p-4">
          <h4 class="text-sm text-muted-foreground">Final Balance</h4>
          <p class="text-3xl font-bold tracking-wide">{currencyFormatter.format(finalMonth.balance)}</p>
        </div>
        <div class="min-w-60 space-y-2 rounded-lg border p-4">
          <h4 class="text-sm text-muted-foreground">Total Contributions</h4>
          <p class="text-3xl font-bold tracking-wide">{currencyFormatter.format(finalMonth.invested)}</p>
        </div>
        <div class="min-w-60 space-y-2 rounded-lg border p-4">
          <h4 class="text-sm text-muted-foreground">Total Interest Earned</h4>
          <p class="text-3xl font-bold tracking-wide">{currencyFormatter.format(finalMonth.interestEarned)}</p>
        </div>
      </div>
    {/if}
  </main>
</div>
