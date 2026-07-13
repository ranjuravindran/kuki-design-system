import * as React from 'react';
import type { KukiTone } from '../tokens';

export interface ChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: KukiTone;
  emphasis?: 'bold' | 'subtle';
  icon?: React.ReactNode;
}

export function Chip({ tone = 'neutral', emphasis = 'subtle', icon, className = '', children, ...rest }: ChipProps) {
  return (
    <span className={`kuki-chip kuki-tone--${tone} kuki-tone--${emphasis} ${className}`} {...rest}>
      {icon}
      {children}
    </span>
  );
}
