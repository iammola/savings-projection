<script lang="ts">
  // TODO: Implement Stepper Buttons
  import { cn } from "$lib/utils";

  import type { EventHandler, HTMLInputAttributes, KeyboardEventHandler } from "svelte/elements";

  interface Props extends Omit<HTMLInputAttributes, "value"> {
    /**
     * Current numeric value
     */
    value?: number;
  }

  let { value = $bindable(), class: className, ...rest }: Props = $props();

  const formatter = $derived(new Intl.NumberFormat(undefined, { style: "currency", currency: "CAD" }));

  const currency = $derived(formatter.formatToParts(0).find((part) => part.type === "currency"));

  const formatted = $derived(formatValue(value));

  const finishEditing = (e: { currentTarget: HTMLInputElement }) => {
    value = +(e.currentTarget.value ?? "").replace(/[^0-9.]+/g, "");
  };

  const onKeyDown: KeyboardEventHandler<HTMLInputElement> = (e) => {
    switch (e.key) {
      case "Enter":
        finishEditing(e);
        break;
    }
  };

  const onBeforeInput: EventHandler<InputEvent, HTMLInputElement> = (e) => {
    if (e.data == null || /^[0-9.,]+$/.test(e.data)) return;
    e.preventDefault();
  };

  function formatValue(value: number | undefined) {
    if (value == null) return "";
    return formatter.format(value).replace(currency?.value!, "");
  }
</script>

<div
  class={cn(
    "flex h-10 min-w-0 items-center justify-start gap-2 rounded-md border border-input bg-background px-3 py-2 ring-offset-background select-none *:min-w-0 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
    className,
  )}
>
  <span class="flex items-center leading-none text-muted-foreground select-none">{currency?.value}</span>
  {#key formatted}
    <input
      type="text"
      class="flex grow [appearance:textfield] text-base placeholder:text-muted-foreground focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
      defaultValue={formatted}
      placeholder={formatValue(0)}
      onkeydown={onKeyDown}
      onblur={finishEditing}
      onbeforeinput={onBeforeInput}
      {...rest}
    />
  {/key}
</div>
