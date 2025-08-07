<script lang="ts">
  import debounce from "lodash.debounce";
  import { Input } from "$lib/components/shadcn/input";
  import { FormLabel } from "$lib/components/shadcn/label";
  import { Textarea } from "$lib/components/shadcn/textarea";
  import * as Accordion from "$lib/components/shadcn/accordion";

  import CurrencyInput from "$lib/components/CurrencyInput.svelte";
  import InterestTiers from "$lib/components/InterestTiers.svelte";
  import BonusRules from "$lib/components/BonusRules/BonusRules.svelte";

  import { currency } from "$lib/shared.svelte";

  type ExtractionData = {
    document_id: string;
    text: string;
    extractions: Array<
      {
        extraction_text: string;
        char_interval: Record<"start_pos" | "end_pos", number> | null;
        alignment_status: "match_fuzzy" | "match_exact" | "match_lesser" | null;
        extraction_index: number;
        group_index: number;
        description: string | null;
      } & (
        | {
            extraction_class: "currency";
            attributes: Record<"symbol" | "code", string>;
          }
        | {
            extraction_class: "initial_balance" | "monthly_withdrawal" | "monthly_contribution";
            attributes: Record<"amount" | "link_to", string>;
          }
        | {
            extraction_class: "interest_rate_tiers";
            attributes: Record<"tier_min" | "tier_max" | "rate", string>;
          }
      )
    >;
  };
  interface Props {
    config: ChartConfig;
    overrides: Map<string, Partial<ChartConfig>>;
  }

  let basePrompt = $state("");
  let { config = $bindable(), overrides }: Props = $props();

  const reset: ChartConfig = {
    initialBalance: 0,
    contribution: 0,
    withdrawals: 0,
    period: 120,
    bonuses: [],
    tiers: [],
  };

  const getExtractions = debounce(
    async (text: string, signal: AbortSignal) => {
      try {
        if (text === "") return;

        const res = await fetch("/api/extract", {
          method: "POST",
          body: JSON.stringify({ text }),
          signal,
          headers: { "Content-Type": "application/json" },
          // body: JSON.stringify({ text: "The interest rate schedule is pretty good: you get 0.7% on anything over $500,000, and 0.4% on balances from $100,000 to that amount. Below $100,000, it's just 0.2%. My initial deposit was $75,000. I have a monthly draw of $500 and a monthly deposit of $2,500.", }),
          // body: JSON.stringify({ text: "Initial balance: $1,000. Monthly contribution: $2,000. Monthly withdrawal: $500. Tiers are 0.15% for amounts under $5k, 0.35% for amounts up to $50k, and 0.9% for amounts greater than $50k." }),
          // body: JSON.stringify({ text: "I'm starting a new account with $25,000. I'll add $750 every month, but I don't have any withdrawals. The interest rates are 0.3% on balances under $10,000, 0.5% for balances between $10,000 and $50,000, and 0.75% for everything over $50,000." }),
        });

        const { extractions } = (await res.json()) as ExtractionData;
        if (extractions.length < 1) return;

        for (const key in reset) {
          const k = key as keyof typeof reset;
          config[k] = reset[k];
        }

        extractions.forEach((cur) => {
          switch (cur.extraction_class) {
            case "currency":
              currency.code = cur.attributes.code;
              break;
            case "initial_balance":
              config.initialBalance = +cur.attributes.amount;
              break;
            case "monthly_withdrawal":
              config.withdrawals = +cur.attributes.amount;
              break;
            case "monthly_contribution":
              config.contribution = +cur.attributes.amount;
              break;
            case "interest_rate_tiers":
              break;
          }
        });

        console.log(config);
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") return;
        console.error("Error: But not aborted", e);
        // Do something to report the error.
        // throw e;
      }
    },
    400,
    { trailing: true },
  );

  $effect(() => {
    if (basePrompt === "") return;

    const controller = new AbortController();
    void getExtractions(basePrompt, controller.signal);

    return () => controller.abort();
  });
</script>

<div class="grid grid-cols-[max-content_minmax(0,1fr)] items-center gap-2 *:gap-y-1">
  <div class="col-span-full grid gap-1.5">
    <FormLabel for="prompt">Prompt</FormLabel>
    <Textarea id="prompt" placeholder="Enter Prompt here" bind:value={basePrompt} />
    <p class="text-muted-foreground text-sm">The extracted entities will be displayed here.</p>
  </div>
  <div class="col-span-full grid gap-1.5"></div>
  <!--
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
  </div> -->
</div>
