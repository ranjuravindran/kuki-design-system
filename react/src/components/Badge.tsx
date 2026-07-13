import * as React from 'react';
import type { KukiTone } from '../tokens';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  tone?: KukiTone;
  emphasis?: 'bold' | 'subtle';
}

export function Badge({ tone = 'neutral', emphasis = 'subtle', className = '', children, ...rest }: BadgeProps) {
  return (
    <span className={`kuki-badge kuki-tone--${tone} kuki-tone--${emphasis} ${className}`} {...rest}>
      {children}
    </span>
  );
}
