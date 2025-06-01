<script lang="ts">
  import { PlusIcon } from "@lucide/svelte";
  import { Button } from "$lib/components/shadcn/button";

  import BonusInterest from "./BonusInterest.svelte";

  import type { BONUS_INTEREST_TYPE } from "./types";

  const { value = $bindable() }: Props = $props();

  let isAdding = $state<{ type: "" }>();

  $effect(() => {
    if (isAdding?.type == null || isAdding.type === "") return;

    switch (isAdding.type as BONUS_INTEREST_TYPE["type"]) {
      case "IN_ACCOUNT_AGE":
        value.push({ type: "IN_ACCOUNT_AGE", rate: 0, data: {} });
        break;
      case "MIN_CONTRIBUTION":
        value.push({ type: "MIN_CONTRIBUTION", rate: 0, data: { amount: 0 } });
        break;
    }

    isAdding = undefined;
  });

  function addInterestItem() {
    isAdding = { type: "" };
  }

  function deleteInterestItem(index: number) {
    value.splice(index, 1);
  }

  interface Props {
    value: BONUS_INTEREST_TYPE[];
  }
</script>

<div class="space-y-2">
  {#each value as item, idx (`${item.type}-${idx}`)}
    <BonusInterest bind:value={value[idx]} onDelete={() => deleteInterestItem(idx)} />
  {/each}
  {#if isAdding != null}
    <BonusInterest isAdding bind:value={isAdding} />
  {/if}
</div>
<Button variant="outline" size="sm" class="mt-2" onclick={addInterestItem} disabled={isAdding != null}>
  <PlusIcon /> Add Tier
</Button>
