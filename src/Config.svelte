<script lang="ts">
  import { Input } from "$lib/components/shadcn/input";
  import { FormLabel } from "$lib/components/shadcn/label";

  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  let { config = $bindable() }: { config: ChartConfig } = $props();
</script>

<aside class="flex flex-col gap-4 overflow-y-auto rounded-lg h-full bg-secondary/50 p-3">
  <div>
    <FormLabel class="text-foreground">Initial Balance</FormLabel>
    <CurrencyInput bind:value={config.initialBalance} min={0} />
  </div>
  <div>
    <FormLabel class="text-foreground">Monthly Contribution</FormLabel>
    <CurrencyInput bind:value={config.contribution} min={0} />
  </div>
  <div>
    <FormLabel class="text-foreground">Monthly Withdrawals</FormLabel>
    <CurrencyInput bind:value={config.withdrawals} min={0} />
    {#if config.withdrawals > config.contribution}
      <p class="text-xs text-muted-foreground">The simulation may not complete</p>
    {/if}
  </div>
  <div>
    <FormLabel class="text-foreground">Total Months</FormLabel>
    <Input type="number" inputmode="numeric" bind:value={config.period} min={2} />
  </div>
  <div>
    <FormLabel class="text-foreground">Interest Tiers</FormLabel>
    <InterestTiers bind:value={config.tiers} />
  </div>
  <div>
    <FormLabel class="text-foreground">Bonus Rules</FormLabel>
    <BonusRules bind:value={config.bonuses} />
  </div>
</aside>
