<script lang="ts">
  import { CircleAlertIcon } from "@lucide/svelte";

  import * as Tooltip from "$lib/components/shadcn/tooltip";
  import NumberInput from "$lib/components/NumberInput.svelte";

  let { value = $bindable() }: Props = $props();

  let storedTiers = $state($state.snapshot(value));

  const invalidTierIndex = $derived(
    storedTiers.findIndex((tier, idx, arr) => idx < arr.length - 1 && tier.min >= arr[idx + 1].min),
  );

  $effect(() => {
    if (invalidTierIndex < 0) value = $state.snapshot(storedTiers);
  });

  interface Props {
    value: Array<{ min: number; rate: number }>;
  }
</script>

<Tooltip.Provider>
  <div class="grid grid-cols-[max-content_minmax(0,1fr)_max-content] gap-3">
    <div class="col-span-full grid grid-cols-subgrid items-center">
      <div></div>
      <div class="text-sm">Balance</div>
      <div class="text-sm">Interest</div>
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
      </div>
    {/each}
  </div>
</Tooltip.Provider>
