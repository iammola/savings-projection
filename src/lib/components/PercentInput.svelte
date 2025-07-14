<!-- Ported from https://21st.dev/camwebby/numeric-scrubber/default -->
<script lang="ts">
  import { cn } from "$lib/utils";

  import type { EventHandler, HTMLInputAttributes } from "svelte/elements";

  /**
   * Minimum allowable value (clamped)
   */
  const min = 0;
  /**
   * Maximum allowable value (clamped)
   */
  const max = 100;
  /**
   * Step for increments (e.g., 1, 0.1, etc.)
   */
  const step = 0.01;

  /**
   * Controls the number of pixels required to increase/decrease a step.
   * A value of 1.0 means 1 pixel per step; 0.1 means 10 pixels per step
   *
   * * For fine-grained control (like opacity: 0-1): use a small value like 0.001
   * * For medium control (like rotation: 0-360): use a medium value like 0.1
   * * For coarse control (like integer counts): use a larger value like 0.5
   */
  const scrubSensitivity = 0.5;

  interface NumericScrubberProps extends Omit<HTMLInputAttributes, "value"> {
    /**
     * Current numeric value
     */
    value: number;
  }

  let { value = $bindable(), class: className, ...rest }: NumericScrubberProps = $props();

  // Refs to track dragging
  let isDraggingRef = false;
  let initialXRef = 0;
  let initialValueRef = value;

  // Determine how many decimals to keep based on `step`
  const decimals = $derived.by(() => {
    if (!Number.isFinite(step)) return 0;
    const stepString = step.toString();
    const decimalPart = stepString.split(".")[1];
    return decimalPart ? decimalPart.length : 0;
  });

  /**
   * Clamp and quantize the given number
   */
  function clampAndQuantize(n: number) {
    // First quantize to nearest step
    const quantized = Math.round(n / step) * step;
    // Then clamp between min and max
    const clamped = Math.max(min, Math.min(quantized, max));
    return parseFloat(clamped.toFixed(decimals));
  }

  /**
   * On pointer down: start dragging
   */
  function handlePointerDown(e: PointerEvent) {
    // Only left-click
    if (e.button !== 0) return;

    isDraggingRef = true;
    initialXRef = e.clientX;
    initialValueRef = value;

    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener("pointerup", handlePointerUp);
  }

  /**
   * On pointer move: compute distance from initial pointer down
   * and update value accordingly
   */
  function handlePointerMove(e: PointerEvent) {
    if (!isDraggingRef) return;

    const deltaX = e.clientX - initialXRef;
    // Apply sensitivity factor to make scrubbing slower
    let newValue = initialValueRef + deltaX * step * scrubSensitivity;
    newValue = clampAndQuantize(newValue);

    value = newValue;
  }

  /**
   * On pointer up: stop dragging
   */
  function handlePointerUp() {
    isDraggingRef = false;
    document.removeEventListener("pointermove", handlePointerMove);
    document.removeEventListener("pointerup", handlePointerUp);
  }

  /**
   * When user types in the input
   */
  const handleInputChange: EventHandler<Event, HTMLInputElement> = (e) => {
    const inputVal = e.currentTarget.value;
    if (inputVal === "") {
      value = min;
      return;
    }

    const parsed = parseFloat(inputVal);
    if (isNaN(parsed)) {
      value = min;
      return;
    }

    const newValue = clampAndQuantize(parsed);
    value = newValue;
  };
</script>

<div
  onpointerdown={handlePointerDown}
  class={cn(
    "flex h-10 min-w-0 items-center justify-end gap-2 rounded-md border border-input bg-background px-3 py-2 ring-offset-background select-none *:min-w-0 focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
    className,
    "cursor-ew-resize",
  )}
>
  <input
    type="number"
    inputmode="decimal"
    class="flex field-sizing-content [appearance:textfield] text-base text-foreground placeholder:text-muted-foreground hover:cursor-ew-resize focus-visible:outline-hidden active:cursor-none active:caret-transparent disabled:cursor-not-allowed disabled:opacity-50 md:text-sm [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
    {step}
    value={value.toFixed(decimals)}
    onchange={handleInputChange}
    {...rest}
  />
  <span class="flex shrink-0 items-center leading-none text-muted-foreground select-none">%</span>
</div>
