import * as React from 'react';
import type { KukiStatus } from '../tokens';

export interface WellnessCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** none = no data yet · critical = severe symptom today · caution = 1–3 clear days · good = 4–7 · excellent = 8+ */
  status: KukiStatus;
  title: string;
  value: string;
  subtitle?: string;
}

export function WellnessCard({ status, title, value, subtitle, className = '', ...rest }: WellnessCardProps) {
  return (
    <div className={`kuki-wellness kuki-wellness--${status} ${className}`} role="status" {...rest}>
      <div className="kuki-wellness__title">{title}</div>
      <div className="kuki-wellness__value">{value}</div>
      {subtitle && <div className="kuki-wellness__subtitle">{subtitle}</div>}
    </div>
  );
}
