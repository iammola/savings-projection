export type BONUS_INTEREST_TYPE =
  | { type: "MIN_CONTRIBUTION"; rate: number; data: { amount: number } }
  | { type: "IN_ACCOUNT_AGE"; rate: number; data: { minMonth?: number; maxMonth?: number } };
