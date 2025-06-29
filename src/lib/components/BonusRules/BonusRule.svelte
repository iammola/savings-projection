<script lang="ts">
  import { Settings2Icon } from "@lucide/svelte";

  import { Input } from "$lib/components/shadcn/input";
  import { FormLabel } from "$lib/components/shadcn/label";
  import * as Select from "$lib/components/shadcn/select";
  import * as Popover from "$lib/components/shadcn/popover";
  import { Separator } from "$lib/components/shadcn/separator";
  import { Button, buttonVariants } from "$lib/components/shadcn/button";

  import PercentInput from "$lib/components/PercentInput.svelte";
  import CurrencyInput from "$lib/components/CurrencyInput.svelte";

  import type { BONUS_INTEREST_TYPE } from "./types";

  const { isAdding = false, value = $bindable(), onDelete }: Props = $props();

  const BONUS_INTEREST_TYPES: Record<BONUS_INTEREST_TYPE["type"], string> = {
    MIN_CONTRIBUTION: "Minimum Contribution",
    IN_ACCOUNT_AGE: "Account Age (Months)",
  };

  const displayLabel = $derived(value.type === "" ? undefined : BONUS_INTEREST_TYPES[value.type]);

  type Props =
    | { value: { type: "" }; isAdding: true; onDelete?: never }
    | { value: BONUS_INTEREST_TYPE; isAdding?: false; onDelete: () => void };
</script>

<div class="flex items-center justify-start gap-2">
  <Select.Root type="single" bind:value={value.type}>
    <Select.Trigger class="grow bg-background text-foreground">{displayLabel ?? "Select an option"}</Select.Trigger>
    <Select.Content>
      {#each Object.entries(BONUS_INTEREST_TYPES) as [value, label] (value)}
        <Select.Item {value}>{label}</Select.Item>
      {/each}
    </Select.Content>
  </Select.Root>
  {#if value.type !== ""}
    <Popover.Root>
      <Popover.Trigger
        class={buttonVariants({
          variant: "ghost",
          size: "icon",
          class: "data-[state=open]:bg-accent data-[state=open]:text-accent-foreground",
        })}
      >
        <Settings2Icon />
      </Popover.Trigger>
      <Popover.Content class="w-sm space-y-4">
        <h4 class="leading-none font-medium underline underline-offset-2">Options</h4>
        <div class="grid grid-cols-[max-content_minmax(0,1fr)_max-content] gap-2">
          {#if value.type === "IN_ACCOUNT_AGE"}
            <div class="col-span-full grid grid-cols-subgrid items-center">
              <FormLabel for="min">Age <span class="text-xs text-muted-foreground">(min)</span></FormLabel>
              <Input id="min" class="h-8" type="number" max={value.data.maxMonth} bind:value={value.data.minMonth} />
              <span class="text-xs text-muted-foreground">months</span>
            </div>
            <div class="col-span-full grid grid-cols-subgrid items-center">
              <FormLabel for="max">Age <span class="text-xs text-muted-foreground">(max)</span></FormLabel>
              <Input id="max" class="h-8" type="number" max={value.data.minMonth} bind:value={value.data.maxMonth} />
              <span class="text-xs text-muted-foreground">months</span>
            </div>
          {:else if value.type === "MIN_CONTRIBUTION"}
            <div class="col-span-full grid grid-cols-subgrid items-center">
              <FormLabel for="amount">Min Amount</FormLabel>
              <CurrencyInput id="amount" bind:value={value.data.amount} class="col-start-2 -col-end-1" />
            </div>
          {/if}
          <Separator class="col-span-full my-1.5" />
          <div class="col-span-full grid grid-cols-subgrid items-center">
            <FormLabel for="interest">Interest</FormLabel>
            <PercentInput id="interest" bind:value={value.rate} class="col-start-2 -col-end-1" />
          </div>
        </div>
        <Separator />
        <div class="flex items-center justify-end">
          <Button variant="ghost" size="sm" onclick={onDelete}>Delete</Button>
        </div>
      </Popover.Content>
    </Popover.Root>
  {/if}
</div>
