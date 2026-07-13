import * as React from 'react';

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  appearance?: 'primary' | 'secondary' | 'ghost' | 'emphasis';
  tone?: 'default' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  selected?: boolean;
  /** Accessible name is required for icon-only controls. */
  label: string;
  children: React.ReactNode;
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      appearance = 'ghost',
      tone = 'default',
      size = 'md',
      selected = false,
      label,
      className = '',
      children,
      ...rest
    },
    ref,
  ) => {
    const cls = [
      'kuki-iconbtn',
      `kuki-iconbtn--${appearance}`,
      `kuki-iconbtn--${size}`,
      tone === 'destructive' ? 'kuki--destructive' : '',
      className,
    ]
      .filter(Boolean)
      .join(' ');
    return (
      <button ref={ref} className={cls} aria-label={label} aria-pressed={selected || undefined} {...rest}>
        {children}
      </button>
    );
  },
);
IconButton.displayName = 'IconButton';
