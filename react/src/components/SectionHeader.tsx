import * as React from 'react';

export interface SectionHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  action?: string;
  onAction?: () => void;
}

export function SectionHeader({ title, action, onAction, className = '', ...rest }: SectionHeaderProps) {
  return (
    <div className={`kuki-section-header ${className}`} {...rest}>
      <span className="kuki-section-header__title">{title}</span>
      {action && (
        <button type="button" className="kuki-section-header__action" onClick={onAction}>
          {action}
        </button>
      )}
    </div>
  );
}
