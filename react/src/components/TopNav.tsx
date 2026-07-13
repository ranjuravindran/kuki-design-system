import * as React from 'react';

export interface TopNavTab {
  key: string;
  label: string;
  icon: React.ReactNode;
}

export interface TopNavProps extends React.HTMLAttributes<HTMLElement> {
  tabs: TopNavTab[];
  active: string;
  onTabChange?: (key: string) => void;
}

export function TopNav({ tabs, active, onTabChange, className = '', ...rest }: TopNavProps) {
  return (
    <nav className={`kuki-topnav ${className}`} {...rest}>
      {tabs.map((t) => {
        const isActive = t.key === active;
        return (
          <button
            key={t.key}
            type="button"
            className="kuki-topnav__tab"
            aria-current={isActive ? 'page' : undefined}
            onClick={() => onTabChange?.(t.key)}
          >
            {t.icon}
            {isActive && <span>{t.label}</span>}
          </button>
        );
      })}
    </nav>
  );
}
