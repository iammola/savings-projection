<script lang="ts">
  import { Input } from "$lib/components/shadcn/input";
  import type { ComponentProps } from "svelte";
  import type { Action } from "svelte/action";

  const formatter = new Intl.NumberFormat(undefined, { style: "currency", currency: "CAD" });

  interface Props {
    type?: "currency" | "number";
    value?: number;
    min?: number;
    max?: number;
  }

  let { type = "number", value = $bindable(), ...rest }: Props = $props();

  let isEditing = $state(false);

  let inputEl = $state<HTMLInputElement | null>(null);

  const formatted = $derived.by(() => {
    if (value == null) return "";
    if (isEditing || type !== "currency") return value.toFixed(2);

    return formatter.format(value ?? 0);
  });

  function finishEditing() {
    value = +(inputEl?.value ?? "").replace(/[^0-9.-]+/g, "");

    isEditing = false;
  }

  function onKeyDown(e: KeyboardEvent) {
    switch (e.key) {
      case "Enter":
        finishEditing();
        break;
    }
  }

  function startEditing() {
    isEditing = true;
  }

  $effect(() => inputEl?.focus());
</script>

{#if isEditing}
  <Input
    {...rest}
    bind:ref={inputEl}
    type="text"
    defaultValue={formatted}
    placeholder={formatter.format(0)}
    onkeydown={onKeyDown}
    onblur={finishEditing}
  />
{:else}
  <div
    aria-label="Click to start editing"
    role="button"
    tabindex="0"
    onclick={startEditing}
    onkeydown={startEditing}
    class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:outline-hidden md:text-sm"
  >
    {formatted}
  </div>
{/if}
