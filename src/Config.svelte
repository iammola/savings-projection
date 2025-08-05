<script lang="ts">
  import { Input } from "$lib/components/shadcn/input";
  import { FormLabel } from "$lib/components/shadcn/label";
  import * as Accordion from "$lib/components/shadcn/accordion";

  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  interface Props {
    config: ChartConfig;
    overrides: Map<string, Partial<ChartConfig>>;
  }

  let { config = $bindable(), overrides }: Props = $props();
</script>

<div class="grid grid-cols-[max-content_minmax(0,1fr)] items-center gap-2 *:gap-y-1">
  <div class="col-span-full grid grid-cols-subgrid">
    <FormLabel class="flex items-center">Initial Balance</FormLabel>
    <CurrencyInput bind:value={config.initialBalance} min={0} />
  </div>
  <div class="col-span-full grid grid-cols-subgrid">
    <FormLabel class="flex items-center">Monthly Contribution</FormLabel>
    <CurrencyInput bind:value={config.contribution} min={0} />
  </div>
  <div class="col-span-full grid grid-cols-subgrid">
    <FormLabel class="flex items-center">Monthly Withdrawals</FormLabel>
    <CurrencyInput bind:value={config.withdrawals} min={0} />
    {#if config.withdrawals > config.contribution}
      <p class="text-xs text-muted-foreground">The simulation may not complete</p>
    {/if}
  </div>
  <div class="col-span-full grid grid-cols-subgrid">
    <FormLabel class="flex items-center">Total Months</FormLabel>
    <Input type="number" inputmode="numeric" bind:value={config.period} min={2} class="h-[unset] py-1 text-sm" />
  </div>
  <div class="col-span-full grid grid-cols-subgrid *:col-span-full">
    <FormLabel class="flex items-center">Interest Tiers</FormLabel>
    <InterestTiers bind:value={config.tiers} />
  </div>
  <div class="col-span-full grid grid-cols-subgrid *:col-span-full">
    <FormLabel class="flex items-center">Bonus Rules</FormLabel>
    <BonusRules bind:value={config.bonuses} />
  </div>
  <div class="col-span-full grid grid-cols-subgrid *:col-span-full">
    <FormLabel class="flex items-center">Overrides</FormLabel>
    <Accordion.Root type="multiple" class="space-y-1">
      {#each overrides as [name, override]}
        <Accordion.Item value={name} class="overflow-hidden rounded-lg border">
          <Accordion.Trigger
            class="items-center justify-start gap-2 rounded-none px-4 py-1 hover:no-underline data-[state=open]:border-b"
          >
            {#snippet children()}
              {@const overridesApplied = Object.keys(override).length}
              {name}
              {#if overridesApplied > 0}
                <p class="rounded-lg bg-primary/10 px-2 py-1 text-xs font-normal text-primary">
                  {`${overridesApplied} ${overridesApplied === 1 ? "override" : "overrides"} applied`}
                </p>
              {/if}
              <div class="grow"></div>
            {/snippet}
          </Accordion.Trigger>
          <Accordion.Content class="bg-white">
            HOWDY {name}
          </Accordion.Content>
        </Accordion.Item>
      {/each}
    </Accordion.Root>
  </div>
</div>
