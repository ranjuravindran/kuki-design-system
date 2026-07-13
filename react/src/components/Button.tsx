import * as React from 'react';

export interface ButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  appearance?: 'primary' | 'secondary' | 'ghost' | 'link' | 'emphasis';
  tone?: 'default' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  /** Toggle state — segmented controls, favorited icon buttons, etc. */
  selected?: boolean;
  /** Forces the disabled-like "blocked" appearance and shows a spinner. Never
   *  layered on top of the normal appearance as a same-colored overlay. */
  loading?: boolean;

  /** Circular icon-only mode — replaces the old separate IconButton. */
  iconOnly?: boolean;
  /** Icon shown when iconOnly is true. */
  icon?: React.ReactNode;
  /** Accessible name. Required when iconOnly (icon-only controls have no visible text). */
  label?: string;

  /** Labeled-mode button text. */
  children?: React.ReactNode;
  /** Outer icon — edge-anchored via the button's own padding. */
  leadingIcon?: React.ReactNode;
  /** Inner icon — hugs the label at a consistent gap, independent of the outer icons. */
  leadingAdornment?: React.ReactNode;
  trailingAdornment?: React.ReactNode;
  trailingIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      appearance = 'primary',
      tone = 'default',
      size = 'md',
      selected = false,
      loading = false,
      iconOnly = false,
      icon,
      label,
      children,
      leadingIcon,
      leadingAdornment,
      trailingAdornment,
      trailingIcon,
      className = '',
      disabled,
      ...rest
    },
    ref,
  ) => {
    const cls = [
      'kuki-btn',
      `kuki-btn--${appearance}`,
      `kuki-btn--${size}`,
      iconOnly ? 'kuki-btn--icon-only' : '',
      tone === 'destructive' ? 'kuki--destructive' : '',
      selected ? 'kuki--selected' : '',
      loading ? 'kuki-btn--loading' : '',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    if (iconOnly) {
      return (
        <button
          ref={ref}
          type="button"
          className={cls}
          aria-label={label}
          aria-pressed={selected || undefined}
          disabled={disabled || loading}
          {...rest}
        >
          {loading ? (
            <span className="kuki-btn__icon kuki-btn__spinner" aria-hidden />
          ) : (
            <span className="kuki-btn__icon">{icon}</span>
          )}
        </button>
      );
    }

    return (
      <button ref={ref} type="button" className={cls} disabled={disabled || loading} {...rest}>
        {!loading && leadingIcon && <span className="kuki-btn__icon">{leadingIcon}</span>}
        <span className="kuki-btn__content">
          {loading ? (
            <span className="kuki-btn__icon kuki-btn__spinner" aria-hidden />
          ) : (
            leadingAdornment && <span className="kuki-btn__icon">{leadingAdornment}</span>
          )}
          <span className="kuki-btn__label">{children}</span>
          {!loading && trailingAdornment && <span className="kuki-btn__icon">{trailingAdornment}</span>}
        </span>
        {!loading && trailingIcon && <span className="kuki-btn__icon">{trailingIcon}</span>}
      </button>
    );
  },
);
Button.displayName = 'Button';
