<script lang="ts">
  import { Input } from "$lib/components/shadcn/input";

  interface Props {
    type?: "currency" | "percent" | "number";
    value?: number;
    min?: number;
    max?: number;
  }

  let { type = "number", value = $bindable(), ...rest }: Props = $props();

  let isEditing = $state(false);

  let inputEl = $state<HTMLInputElement | null>(null);

  const formatter = $derived(
    new Intl.NumberFormat(
      undefined,
      type === "percent" ? { style: "percent", minimumFractionDigits: 2 }
      : type === "currency" ? { style: "currency", currency: "CAD" }
      : {},
    ),
  );

  const formatted = $derived.by(() => {
    if (value == null) return "";

    if (isEditing || type === "number") return value.toFixed(2);

    if (type === "currency") return formatter.format(value);

    if (type === "percent") return formatter.format(value / 100);
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
