interface MonthData {
  idx: number;
  startingBalance: number;
  endingBalance: number;
  total: Record<"interest" | "invested", number>;
  inMonth: Record<"interest" | "invested" | "rate", number>;
}

interface ChartConfig {
  initialBalance: number;
  withdrawals: number;
  contribution: number;
  period: number;
  tiers: Array<{ min: number; rate: number; tierId: string }>;
  bonuses: BONUS_INTEREST_TYPE[];
}

type BONUS_INTEREST_TYPE =
  | { type: "MIN_CONTRIBUTION"; rate: number; data: { amount: number } }
  | { type: "IN_ACCOUNT_AGE"; rate: number; data: { minMonth?: number; maxMonth?: number } };

type MonthDataPath = FlattenObjectKeys<MonthData>;

type FlattenObjectKeys<T extends Record<string, unknown>, Key = keyof T> =
  Key extends string ?
    T[Key] extends Record<string, unknown> ?
      `${Key}.${FlattenObjectKeys<T[Key]>}`
    : `${Key}`
  : never;
