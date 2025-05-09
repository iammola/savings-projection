<script lang="ts">
  import { Tooltip } from "chart.js";
  import { easingEffects } from "chart.js/helpers";

  import Chart from "$lib/components/Chart.svelte";
  import { Label } from "$lib/components/shadcn/label";
  import NumberInput from "$lib/components/NumberInput.svelte";
  import NumberTiers from "$lib/components/NumberTiers.svelte";

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
    { min: 0, rate: 0.25 },
    { min: 10e3, rate: 0.3 },
    { min: 25e3, rate: 0.55 },
    { min: 10e4, rate: 0.8 },
    { min: 5e5, rate: 1 },
  ]);

  const bonusInterest = [
    { minMonth: 0, maxMonth: 2, rate: 5 }, // Between the first 3 months, give an additional 5% interest
    { minContribution: 200, rate: 0.25 }, // Give an additional 0.25% interest if the closing balance is 200 more than the previous month
  ];

  $effect(() => {
    $inspect(interestTiers).with(console.log);
  });

  const data = $derived(calculateAccountGrowth(initialBalance, monthlyContribution, totalMonths));

  function calculateAccountGrowth(initialBalance: number, monthlyContribution: number, totalMonths: number) {
    const FALLBACK = { label: "", interestEarned: 0, invested: initialBalance, balance: initialBalance };

    return Array.from({ length: totalMonths }).reduce<Array<typeof FALLBACK>>((acc, _, monthIndex) => {
      const previous = acc[monthIndex - 1] ?? FALLBACK;
      const interestRate = [
        interestTiers.findLast((tier) => tier.min < previous.balance)?.rate ?? 0,
        ...bonusInterest.flatMap((i) => {
          if (i.minContribution != null && monthlyContribution < i.minContribution) return [];
          if (i.minMonth != null && monthIndex < i.minMonth) return [];
          if (i.maxMonth != null && monthIndex > i.maxMonth) return [];
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
  }
</script>

<div class="grid h-screen w-screen grid-cols-[25%_minmax(0,1fr)] divide-x divide-dashed *:min-h-0">
  <aside class="flex flex-col gap-2 divide-y py-4 *:px-4">
    <h1>Money!</h1>
    <section class="space-y-5 overflow-y-auto">
      <div>
        <Label>Initial Balance</Label>
        <NumberInput type="currency" bind:value={initialBalance} />
      </div>
      <div>
        <Label>Monthly Contribution</Label>
        <NumberInput type="currency" bind:value={monthlyContribution} min={0} />
      </div>
      <div>
        <Label>Total Months</Label>
        <NumberInput bind:value={totalMonths} min={2} />
      </div>
      <div>
        <Label>Interest Tiers</Label>
        <NumberTiers bind:value={interestTiers} />
      </div>
    </section>
  </aside>
  <main class="flex flex-col items-center justify-center-safe gap-4 p-2 *:min-h-0">
    <p>Description/Summary of Growth here</p>
    <Chart
      type="line"
      data={{
        labels: data.map((d) => d.label),
        datasets: [{ label: "Balance", data: data.map((d) => d.balance), normalized: true, pointRadius: 0 }],
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
          y: { ticks: { callback: (tickValue) => currencyFormatter.format(+tickValue) } },
          x: { grid: { display: false } },
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
      defaults={{ font: { family: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif' } }}
      class="p-2"
    />
  </main>
</div>
