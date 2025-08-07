export const currency = $state({ code: "USD" });

const currencyFormatter = $derived(new Intl.NumberFormat(undefined, { style: "currency", currency: currency.code }));
// @ts-expect-error Intl.DurationFormat (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DurationFormat) not typed
const timeFormatter = new Intl.DurationFormat(undefined, { style: "long" });
const percentFormatter = new Intl.NumberFormat(undefined, { style: "percent", minimumFractionDigits: 2 });

export const format = {
  time: timeFormatter,
  percent: percentFormatter,
  get currency() {
    return currencyFormatter;
  },
};
