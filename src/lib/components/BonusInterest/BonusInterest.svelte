<script lang="ts">
  import { PlusIcon, XIcon } from "@lucide/svelte";
  import { Button, buttonVariants } from "$lib/components/shadcn/button";
  import * as Select from "$lib/components/shadcn/select";
  import * as Popover from "$lib/components/shadcn/popover";

  const { value = $bindable() }: Props = $props();

  const BONUS_INTEREST_TYPES = [
    { value: "MIN_CONTRIBUTION" as const, label: "Minimum Contribution" },
    { value: "IN_ACCOUNT_AGE" as const, label: "Account Age (Months)" },
  ];

  const selectedLabel = $derived(value.map((item) => BONUS_INTEREST_TYPES.find((type) => type.value === item)?.label));

  function addInterestItem() {
    value.push("");
  }

  function deleteInterestItem(index: number) {
    value.splice(index, 1);
  }

  interface Props {
    value: string[];
  }
</script>

{#each value as item, idx (item)}
  <div class="flex items-center justify-start gap-2">
    <Select.Root open type="single" bind:value={value[idx]}>
      <Select.Trigger class="grow">{selectedLabel[idx] ?? "Select an option"}</Select.Trigger>
      <Select.Content>
        {#each BONUS_INTEREST_TYPES as { value, label } (value)}
          <Select.Item {value}>{label}</Select.Item>
        {/each}
      </Select.Content>
    </Select.Root>
    <Popover.Root>
      <Popover.Trigger class={buttonVariants({ variant: "ghost", size: "icon" })}>
        <XIcon />
      </Popover.Trigger>
      <Popover.Content class="space-y-2">
        <p class="text-sm">Are you sure you want to delete this interest entry?</p>
        <div class="flex items-center justify-end gap-2">
          <Popover.Close class={buttonVariants({ size: "sm" })}>Cancel</Popover.Close>
          <Button variant="ghost" size="sm" onclick={() => deleteInterestItem(idx)}>Yes, Delete.</Button>
        </div>
      </Popover.Content>
    </Popover.Root>
  </div>
{/each}
<Button variant="outline" size="sm" class="mt-2" onclick={addInterestItem} disabled={value.includes("")}>
  <PlusIcon /> Add Tier
</Button>
