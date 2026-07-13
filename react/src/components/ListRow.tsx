import * as React from 'react';

export interface ListRowProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  value?: string;
  valueSub?: string;
  valueSubTone?: 'default' | 'critical' | 'good';
}

export function ListRow({ title, subtitle, value, valueSub, valueSubTone = 'default', className = '', ...rest }: ListRowProps) {
  const subCls =
    valueSubTone === 'critical'
      ? 'kuki-list-row__valuesub kuki-list-row__valuesub--critical'
      : valueSubTone === 'good'
        ? 'kuki-list-row__valuesub kuki-list-row__valuesub--good'
        : 'kuki-list-row__valuesub';
  return (
    <div className={`kuki-list-row ${className}`} {...rest}>
      <div>
        <div className="kuki-list-row__title">{title}</div>
        {subtitle && <div className="kuki-list-row__subtitle">{subtitle}</div>}
      </div>
      <div className="kuki-list-row__right">
        {value && <div className="kuki-list-row__title">{value}</div>}
        {valueSub && <div className={subCls}>{valueSub}</div>}
      </div>
    </div>
  );
}
