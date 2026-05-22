import { Loader2 } from "lucide-react";

type LoadingStateProps = {
  text?: string;
};

export function LoadingState({ text = "Загружаем данные" }: LoadingStateProps) {
  return (
    <div className="loading-state">
      <Loader2 aria-hidden="true" className="spin" size={22} />
      <span>{text}</span>
    </div>
  );
}
