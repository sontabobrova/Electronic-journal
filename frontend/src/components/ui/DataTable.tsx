import type { ReactNode } from "react";

import { EmptyState } from "./EmptyState";
import { LoadingState } from "./LoadingState";

export type DataTableColumn<T> = {
  key: string;
  header: string;
  align?: "left" | "center" | "right";
  render: (row: T) => ReactNode;
  width?: string;
};

type DataTableProps<T> = {
  columns: Array<DataTableColumn<T>>;
  data: T[];
  emptyText?: string;
  getRowKey: (row: T) => string | number;
  isLoading?: boolean;
};

export function DataTable<T>({ columns, data, emptyText = "Нет данных для отображения.", getRowKey, isLoading }: DataTableProps<T>) {
  if (isLoading) {
    return <LoadingState text="Загружаем таблицу" />;
  }

  if (!data.length) {
    return <EmptyState title="Данных пока нет" text={emptyText} />;
  }

  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} style={{ width: column.width }} className={column.align ? `is-${column.align}` : undefined}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={getRowKey(row)}>
              {columns.map((column) => (
                <td key={column.key} className={column.align ? `is-${column.align}` : undefined}>
                  {column.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
