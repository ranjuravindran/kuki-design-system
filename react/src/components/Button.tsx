import * as React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  appearance?: 'primary' | 'secondary' | 'ghost' | 'link';
  tone?: 'default' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leadingIcon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      appearance = 'primary',
      tone = 'default',
      size = 'md',
      loading = false,
      leadingIcon,
      trailingIcon,
      className = '',
      children,
      disabled,
      ...rest
    },
    ref,
  ) => {
    const isLink = appearance === 'link';
    const showSpinner = loading && !isLink;
    const cls = [
      'kuki-btn',
      `kuki-btn--${appearance}`,
      `kuki-btn--${size}`,
      tone === 'destructive' ? 'kuki--destructive' : '',
      showSpinner ? 'kuki-btn--loading' : '',
      className,
    ]
      .filter(Boolean)
      .join(' ');
    return (
      <button ref={ref} className={cls} disabled={disabled || showSpinner} {...rest}>
        {leadingIcon}
        <span className="kuki-btn__label">{children}</span>
        {trailingIcon}
        {showSpinner && <span className="kuki-btn__spinner" aria-hidden />}
      </button>
    );
  },
);
Button.displayName = 'Button';
