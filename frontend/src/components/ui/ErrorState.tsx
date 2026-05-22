import { AlertTriangle } from "lucide-react";
import type { ReactNode } from "react";

type ErrorStateProps = {
  action?: ReactNode;
  text: string;
  title?: string;
};

export function ErrorState({ action, text, title = "Не удалось загрузить данные" }: ErrorStateProps) {
  return (
    <div className="error-state">
      <AlertTriangle aria-hidden="true" size={22} />
      <div>
        <h3>{title}</h3>
        <p>{text}</p>
        {action ? <div className="error-state__action">{action}</div> : null}
      </div>
    </div>
  );
}
