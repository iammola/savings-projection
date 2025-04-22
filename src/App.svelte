<script lang="ts">
  import { Tooltip } from "chart.js";

  import Chart from "$lib/components/Chart.svelte";
  import { Input } from "$lib/components/shadcn/input";
  import { Label } from "$lib/components/shadcn/label";

  const currencyFormatter = new Intl.NumberFormat(undefined, { style: "currency", currency: "CAD" });

  let initialBalance = $state(2500);
  let monthlyContribution = $state(300);
  let totalMonths = $state(12 /* 1 Year */);

  const bonusInterest = [
    { minMonth: 0, maxMonth: 2, rate: 5 }, // Between the first 3 months, give an additional 5% interest
    { minContribution: 200, rate: 0.25 }, // Give an additional 0.25% interest if the closing balance is 200 more than the previous month
  ];
  const interestTiers = [
    { min: 0, rate: 0.25 },
    { min: 10e3, rate: 0.3 },
    { min: 25e3, rate: 0.55 },
    { min: 10e4, rate: 0.8 },
    { min: 5e5, rate: 1 },
  ];

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
  <aside class="flex flex-col gap-2 divide-y p-4">
    <h1>Money!</h1>
    <section class="space-y-5">
      <div>
        <Label>Initial Balance ({initialBalance})</Label>
        <Input type="range" bind:value={initialBalance} min={0} max={10e5} step={100} />
      </div>
      <div>
        <Label>Monthly Contribution ({monthlyContribution})</Label>
        <Input type="range" bind:value={monthlyContribution} min={0} max={2e3} step={10} />
      </div>
      <div>
        <Label>Total Months ({totalMonths})</Label>
        <Input type="range" bind:value={totalMonths} min={2} max={12 * 25} step={1} />
      </div>
    </section>
  </aside>
  <main class="flex flex-col items-center justify-center-safe gap-4 p-4 *:min-h-0">
    <p></p>
    <Chart
      type="line"
      data={{
        labels: data.map((d) => d.label),
        datasets: [
          { label: "Balance", data: data.map((d) => d.balance), normalized: true, pointRadius: 1 },
          { label: "Total Invested", data: data.map((d) => d.invested), normalized: true, pointRadius: 1 },
        ],
      }}
      options={{
        animation: false,
        scales: {
          y: { ticks: { callback: (tickValue) => currencyFormatter.format(+tickValue) } },
        },
        interaction: { intersect: false, mode: "index" },
        plugins: {
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
            const { caretX: x, caretY: y } = args.tooltip;

            const ctx = chart.ctx;
            ctx.save();

            ctx.lineWidth = 2;
            ctx.strokeStyle = "red";

            ctx.beginPath();
            ctx.setLineDash([5, 7]);
            ctx.moveTo(chart.chartArea.left, y);
            ctx.lineTo(x, y);
            ctx.lineTo(x, chart.chartArea.top);
            ctx.stroke();

            ctx.beginPath();
            ctx.setLineDash([]);
            ctx.moveTo(x, chart.chartArea.bottom);
            ctx.lineTo(x, y);
            ctx.lineTo(chart.chartArea.right, y);
            ctx.stroke();
            //
            ctx.restore();
          },
        },
      ]}
      defaults={{ font: { family: 'ui-serif, Georgia, Cambria, "Times New Roman", Times, serif' } }}
      class="p-2"
    />
  </main>
</div>
