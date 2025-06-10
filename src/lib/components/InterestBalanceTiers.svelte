<script lang="ts">
  import { CircleAlertIcon, PlusIcon, XIcon } from "@lucide/svelte";

  import * as Tooltip from "$lib/components/shadcn/tooltip";
  import * as Popover from "$lib/components/shadcn/popover";
  import { Button, buttonVariants } from "$lib/components/shadcn/button";

  import NumberInput from "$lib/components/NumberInput.svelte";
  import PercentInput from "$lib/components/PercentInput.svelte";

  let { value = $bindable() }: Props = $props();

  let storedTiers = $state($state.snapshot(value));

  const invalidTierIndex = $derived(
    storedTiers.findIndex((tier, idx, arr) => idx < arr.length - 1 && tier.min >= arr[idx + 1].min),
  );

  $effect(() => {
    if (invalidTierIndex < 0) value = $state.snapshot(storedTiers);
  });

  function addTier(index = storedTiers.length) {
    index = Math.min(Math.max(0, index), storedTiers.length);

    const nextMin = index === storedTiers.length ? 0 : storedTiers[index].min;
    const prevMin = index === 0 ? 0 : storedTiers[index - 1].min;

    const min = prevMin + Math.abs(nextMin - prevMin) / 2;

    storedTiers.splice(index, 0, { min, rate: 0 });
  }

  function deleteTier(index: number) {
    if (storedTiers.length < 2) return;
    storedTiers.splice(index, 1);
  }

  interface Props {
    value: Array<{ min: number; rate: number }>;
  }
</script>

<Tooltip.Provider>
  <div class="grid grid-cols-[minmax(0,1fr)_repeat(2,max-content)] gap-2">
    {#each storedTiers as tier, tierIndex (tierIndex)}
      <div class="col-span-full grid grid-cols-subgrid items-center">
        <div>
          <NumberInput type="currency" bind:value={tier.min} min={tierIndex < 1 ? 0 : value[tierIndex - 1].min} />
        </div>
        <PercentInput class="max-w-28" bind:value={tier.rate} />
        <div>
          <Popover.Root>
            <Popover.Trigger
              class={buttonVariants({
                variant: "ghost",
                size: "icon",
                class: "data-[state=open]:bg-accent data-[state=open]:text-accent-foreground",
              })}
            >
              <XIcon />
            </Popover.Trigger>
            <Popover.Content class="space-y-2">
              <p class="text-sm">Are you sure you want to delete this tier?</p>
              <div class="flex items-center justify-end gap-2">
                <Popover.Close class={buttonVariants({ size: "sm" })}>Cancel</Popover.Close>
                <Button variant="ghost" size="sm" onclick={() => deleteTier(tierIndex)}>Yes, Delete.</Button>
              </div>
            </Popover.Content>
          </Popover.Root>
        </div>
        {#if invalidTierIndex === tierIndex}
          <!-- TODO -->
          <div class="col-span-full text-xs text-red-500">The balance cannot be more than the next item</div>
        {/if}
      </div>
    {/each}
  </div>
  <Button variant="ghost" size="sm" class="mt-2" onclick={() => addTier()}>
    <PlusIcon /> Add Tier
  </Button>
</Tooltip.Provider>
