<script lang="ts">
  import { MinusIcon, PlusIcon } from "@lucide/svelte";

  import { cn } from "$lib/utils";
  import { currencyFormatter } from "$lib/shared";

  import type { EventHandler, HTMLInputAttributes, KeyboardEventHandler } from "svelte/elements";

  interface Props extends Omit<HTMLInputAttributes, "value"> {
    /**
     * Current numeric value
     */
    value: number;
  }

  const STEP_AMOUNT = 100;

  let { value = $bindable(), class: className, ...rest }: Props = $props();

  const symbol = $derived(currencyFormatter.formatToParts(0).find((part) => part.type === "currency")?.value);

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

  function formatValue(value: number) {
    return currencyFormatter.format(value).replace(symbol!, "");
  }

  function stepper(action: "INC" | "DEC") {
    let change = STEP_AMOUNT;
    if (action === "DEC") change *= -1;

    value += change;
    if (rest.max != null) value = Math.min(value, +rest.max);
    if (rest.min != null) value = Math.max(value, +rest.min);
  }
</script>

<div
  class={cn(
    "flex h-10 min-w-0 items-center justify-start gap-2 overflow-hidden rounded-md border border-input bg-background ring-offset-background select-none [--padding-x:theme(spacing.3)] [--padding-y:theme(spacing.2)] *:min-w-0 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
    className,
  )}
>
  <span
    class="flex shrink-0 items-center py-(--padding-y) pl-(--padding-x) leading-none text-muted-foreground select-none"
  >
    {symbol}
  </span>
  {#key formatted}
    <input
      type="text"
      class="flex field-sizing-content grow [appearance:textfield] py-(--padding-y) pr-(--padding-x) text-base text-foreground placeholder:text-muted-foreground focus-visible:outline-hidden disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
      defaultValue={formatted}
      placeholder={formatValue(0)}
      onkeydown={onKeyDown}
      onblur={finishEditing}
      onbeforeinput={onBeforeInput}
      {...rest}
    />
  {/key}
  <div
    class="flex h-full shrink-0 divide-x border-l *:grid *:h-full *:cursor-pointer *:place-items-center *:px-2 *:text-foreground *:hover:bg-secondary/90 *:[&_svg]:size-4"
  >
    <button
      type="button"
      aria-label="Decrement"
      title={`Remove ${currencyFormatter.format(STEP_AMOUNT)}`}
      onclick={() => stepper("DEC")}
    >
      <MinusIcon />
    </button>
    <button
      type="button"
      aria-label="Increment"
      title={`Add ${currencyFormatter.format(STEP_AMOUNT)}`}
      onclick={() => stepper("INC")}
    >
      <PlusIcon />
    </button>
  </div>
</div>
