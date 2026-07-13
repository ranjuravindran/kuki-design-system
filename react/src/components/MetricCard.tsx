import * as React from 'react';
import { Chip } from './Chip';
import type { KukiMetric, KukiTone } from '../tokens';

const METRIC_TONE: Record<KukiMetric, KukiTone> = {
  weight: 'turquoise',
  vaccine: 'pink',
  activity: 'info',
  nutrition: 'good',
  sleep: 'violet',
  medication: 'excellent',
};

export interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  metric: KukiMetric;
  label: string;
  value: string;
  sub?: string;
  empty?: boolean;
  icon?: React.ReactNode;
}

export function MetricCard({ metric, label, value, sub, empty = false, icon, className = '', ...rest }: MetricCardProps) {
  return (
    <div className={`kuki-metric-card ${empty ? 'kuki-metric-card--empty' : ''} ${className}`} {...rest}>
      <Chip tone={METRIC_TONE[metric]} emphasis="subtle" icon={icon}>
        {label}
      </Chip>
      <div>
        <div className="kuki-metric-card__value">{value}</div>
        {sub && <div className="kuki-metric-card__sub">{sub}</div>}
      </div>
    </div>
  );
}
