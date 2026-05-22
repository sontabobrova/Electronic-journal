import type { ReactNode } from "react";

type PageHeaderProps = {
  actions?: ReactNode;
  badge?: ReactNode;
  description?: string;
  icon?: ReactNode;
  title: string;
};

export function PageHeader({ actions, badge, description, icon, title }: PageHeaderProps) {
  return (
    <div className="page-heading">
      <div>
        {badge}
        <h1>{title}</h1>
        {description ? <p>{description}</p> : null}
      </div>
      <div className="page-heading__side">
        {actions ? <div className="page-heading__actions">{actions}</div> : null}
        {icon}
      </div>
    </div>
  );
}
