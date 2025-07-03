interface MonthData {
  idx: number;
  endingBalance: number;
  total: Record<"interest" | "invested", number>;
  inMonth: Record<"interest" | "invested" | "rate", number>;
}

type MonthDataPath = FlattenObjectKeys<MonthData>

type FlattenObjectKeys<T extends Record<string, unknown>, Key = keyof T> = Key extends string
  ? T[Key] extends Record<string, unknown>
    ? `${Key}.${FlattenObjectKeys<T[Key]>}`
    : `${Key}`
  : never
