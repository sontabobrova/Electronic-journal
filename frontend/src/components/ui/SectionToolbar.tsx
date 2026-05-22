import type { ReactNode } from "react";

type SectionToolbarProps = {
  actions?: ReactNode;
  children?: ReactNode;
  title: string;
};

export function SectionToolbar({ actions, children, title }: SectionToolbarProps) {
  return (
    <div className="section-toolbar">
      <div>
        <h2>{title}</h2>
        {children ? <div className="section-toolbar__filters">{children}</div> : null}
      </div>
      {actions ? <div className="section-toolbar__actions">{actions}</div> : null}
    </div>
  );
}
