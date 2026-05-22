import { Inbox } from "lucide-react";
import type { ReactNode } from "react";

type EmptyStateProps = {
  action?: ReactNode;
  text?: string;
  title: string;
};

export function EmptyState({ action, text, title }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <Inbox aria-hidden="true" size={24} />
      <h3>{title}</h3>
      {text ? <p>{text}</p> : null}
      {action ? <div className="empty-state__action">{action}</div> : null}
    </div>
  );
}
