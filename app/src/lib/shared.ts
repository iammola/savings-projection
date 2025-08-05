import { getCurrency } from "locale-currency";

export const currencyFormatter = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: getCurrency(Intl.NumberFormat().resolvedOptions().locale) ?? "USD",
});

export const percentFormatter = new Intl.NumberFormat(undefined, { style: "percent", minimumFractionDigits: 2 });

// @ts-expect-error Intl.DurationFormat (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat) not typed
export const timeFormatter = new Intl.DurationFormat(undefined, { style: "long" });
