/** KuKi design tokens — semantic names mirror the Figma variables 1:1.
 *  Values live in ../../tokens/css/tokens.css as CSS custom properties.
 *  Use `kukiVar('surface/brand')` → `var(--kuki-sem-surface-brand)`.
 */
export type KukiStatus = 'none' | 'critical' | 'caution' | 'good' | 'excellent';

export type KukiTone =
  | 'neutral' | 'brand' | 'critical' | 'caution' | 'good'
  | 'excellent' | 'info' | 'pink' | 'violet' | 'turquoise';

export type KukiMetric =
  | 'weight' | 'vaccine' | 'activity' | 'nutrition' | 'sleep' | 'medication';

/** Streak-day count → wellness status, per KuKi product rules. */
export function statusForStreak(days: number | null, severeToday = false): KukiStatus {
  if (severeToday) return 'critical';
  if (days === null) return 'none';
  if (days >= 8) return 'excellent';
  if (days >= 4) return 'good';
  if (days >= 1) return 'caution';
  return 'critical';
}

export function kukiVar(semanticName: string): string {
  return `var(--kuki-sem-${semanticName.replace(/\//g, '-')})`;
}
