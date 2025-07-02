interface MonthData {
  idx: number;
  endingBalance: number;
  total: Record<"interest" | "invested", number>;
  inMonth: Record<"interest" | "invested" | "rate", number>;
}
