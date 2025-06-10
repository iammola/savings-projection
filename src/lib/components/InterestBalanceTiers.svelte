<script lang="ts">
  import { CircleAlertIcon, PlusIcon, XIcon } from "@lucide/svelte";

  import * as Tooltip from "$lib/components/shadcn/tooltip";
  import * as Popover from "$lib/components/shadcn/popover";
  import { Button, buttonVariants } from "$lib/components/shadcn/button";

  import NumberInput from "$lib/components/NumberInput.svelte";

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
  <div class="grid grid-cols-[max-content_minmax(0,1fr)_repeat(2,max-content)] gap-2">
    <div class="col-span-full grid grid-cols-subgrid items-center">
      <div></div>
      <div class="text-sm">Balance</div>
      <div class="text-sm">Interest</div>
      <div></div>
    </div>
    {#each storedTiers as tier, tierIndex (tierIndex)}
      <div class="col-span-full grid grid-cols-subgrid items-center">
        <div class="w-5 text-center text-sm">
          {#if invalidTierIndex === tierIndex}
            <Tooltip.Root>
              <Tooltip.Trigger class="text-red-500">
                <CircleAlertIcon class="aspect-square size-full" />
              </Tooltip.Trigger>
              <Tooltip.Content collisionPadding={10}>The balance cannot be more than the next item</Tooltip.Content>
            </Tooltip.Root>
          {:else}
            {tierIndex + 1}.
          {/if}
        </div>
        <div>
          <NumberInput type="currency" bind:value={tier.min} min={tierIndex < 1 ? 0 : value[tierIndex - 1].min} />
        </div>
        <div class="w-28">
          <NumberInput type="percent" bind:value={tier.rate} min={0} max={1} />
        </div>
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
      </div>
    {/each}
  </div>
  <Button variant="ghost" size="sm" class="mt-2" onclick={() => addTier()}>
    <PlusIcon /> Add Tier
  </Button>
</Tooltip.Provider>
