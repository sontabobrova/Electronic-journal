import type { ReactNode } from "react";

import { StatusBadge } from "../components/StatusBadge";
import { Button, EmptyState, PageHeader } from "../components/ui";

type PlaceholderPageProps = {
  title: string;
  description: string;
  icon: ReactNode;
  nextSteps: string[];
};

export function PlaceholderPage({ title, description, icon, nextSteps }: PlaceholderPageProps) {
  return (
    <section className="content-stack">
      <PageHeader badge={<StatusBadge tone="warning">Скоро</StatusBadge>} description={description} icon={icon} title={title} />

      <div className="panel">
        <h3>Ближайшая реализация</h3>
        <ul className="check-list">
          {nextSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
      </div>

      <EmptyState
        action={
          <Button size="sm" variant="secondary">
            Подготовлено
          </Button>
        }
        text="Здесь появятся таблицы, фильтры и рабочие формы раздела."
        title="Раздел ожидает подключение данных"
      />
    </section>
  );
}
