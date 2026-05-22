import { FormEvent, useMemo, useState } from "react";
import { AxiosError } from "axios";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ClipboardList, Download, FileSpreadsheet, FileText, Search } from "lucide-react";

import { fetchGroups, fetchPeriods, fetchStudentsAdmin, fetchSubjects } from "../../api/admin";
import { generateReport, fetchReportRequests, getReportDownloadUrl } from "../../api/reports";
import type { ReportFormat, ReportParameters, ReportRequest, ReportType } from "../../api/reports";
import { useAuth } from "../../auth/authContext";
import { StatusBadge } from "../../components/StatusBadge";
import {
  Button,
  DataTable,
  ErrorState,
  LoadingState,
  PageHeader,
  SectionToolbar,
  SelectField,
  TextField,
} from "../../components/ui";
import type { DataTableColumn } from "../../components/ui";

type FilterForm = {
  group: string;
  period: string;
  student: string;
  subject: string;
};

const emptyReports: ReportRequest[] = [];
const reportTypeOptions: Array<{ description: string; label: string; value: ReportType }> = [
  { description: "Оценки, работы журнала и максимальный балл", label: "Успеваемость", value: "grades" },
  { description: "Занятия, статусы посещаемости и даты", label: "Посещаемость", value: "attendance" },
];

const formatOptions: Array<{ label: string; value: ReportFormat }> = [
  { label: "CSV", value: "csv" },
  { label: "XLSX", value: "xlsx" },
  { label: "PDF", value: "pdf" },
];

const reportTypeLabels: Record<ReportType, string> = {
  attendance: "Посещаемость",
  grades: "Успеваемость",
};

const formatLabels: Record<ReportFormat, string> = {
  csv: "CSV",
  pdf: "PDF",
  xlsx: "XLSX",
};

export function ReportsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [reportType, setReportType] = useState<ReportType>("grades");
  const [fileFormat, setFileFormat] = useState<ReportFormat>("xlsx");
  const [filters, setFilters] = useState<FilterForm>({ group: "", period: "", student: "", subject: "" });
  const [search, setSearch] = useState("");
  const [generatedReport, setGeneratedReport] = useState<ReportRequest | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const reportsQuery = useQuery({ queryKey: ["reports", "requests"], queryFn: fetchReportRequests });
  const groupsQuery = useQuery({ queryKey: ["reports", "groups"], queryFn: fetchGroups });
  const subjectsQuery = useQuery({ queryKey: ["reports", "subjects"], queryFn: fetchSubjects });
  const periodsQuery = useQuery({ queryKey: ["reports", "periods"], queryFn: fetchPeriods });
  const studentsQuery = useQuery({ queryKey: ["reports", "students"], queryFn: fetchStudentsAdmin });

  const generateMutation = useMutation({
    mutationFn: () => generateReport({ file_format: fileFormat, parameters: buildParameters(filters), report_type: reportType }),
    onSuccess: async (report) => {
      setGeneratedReport(report);
      setFormError(null);
      await queryClient.invalidateQueries({ queryKey: ["reports", "requests"] });
    },
    onError: (error) => {
      setGeneratedReport(null);
      setFormError(getApiErrorMessage(error));
    },
  });

  const reports = reportsQuery.data ?? emptyReports;
  const normalizedSearch = search.trim().toLowerCase();
  const filteredReports = useMemo(
    () =>
      reports.filter((report) =>
        `${reportTypeLabels[report.report_type]} ${formatLabels[report.file_format]} ${formatDateTime(report.generated_at)} ${JSON.stringify(report.parameters)}`
          .toLowerCase()
          .includes(normalizedSearch),
      ),
    [normalizedSearch, reports],
  );

  const groupOptions = [{ label: "Все группы", value: "" }, ...(groupsQuery.data ?? []).map((group) => ({ label: group.name, value: group.id.toString() }))];
  const subjectOptions = [{ label: "Все дисциплины", value: "" }, ...(subjectsQuery.data ?? []).map((subject) => ({ label: subject.name, value: subject.id.toString() }))];
  const periodOptions = [{ label: "Все периоды", value: "" }, ...(periodsQuery.data ?? []).map((period) => ({ label: period.name, value: period.id.toString() }))];
  const studentOptions = [
    { label: user?.role === "student" ? "Только мои данные" : "Все студенты", value: "" },
    ...(studentsQuery.data ?? []).map((student) => ({
      label: `${student.user_details.full_name || student.user_details.username} (${student.group_name})`,
      value: student.id.toString(),
    })),
  ];

  const historyColumns: Array<DataTableColumn<ReportRequest>> = [
    { key: "date", header: "Дата", render: (row) => formatDateTime(row.generated_at), width: "180px" },
    { key: "type", header: "Отчет", render: (row) => reportTypeLabels[row.report_type], width: "170px" },
    { key: "format", header: "Формат", render: (row) => <StatusBadge tone="neutral">{formatLabels[row.file_format]}</StatusBadge>, width: "120px" },
    { key: "filters", header: "Фильтры", render: (row) => renderReportParameters(row.parameters) },
    {
      key: "download",
      header: "",
      align: "right",
      render: (row) => (
        <Button disabled={!getReportDownloadUrl(row)} icon={<Download aria-hidden="true" size={14} />} onClick={() => openReport(row)} size="sm" variant="secondary">
          Скачать
        </Button>
      ),
      width: "150px",
    },
  ];

  if (reportsQuery.isLoading) {
    return <LoadingState text="Загружаем отчеты" />;
  }

  if (reportsQuery.isError) {
    return <ErrorState text="Не удалось загрузить историю отчетов." />;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    generateMutation.mutate();
  }

  return (
    <section className="content-stack">
      <PageHeader
        badge={<StatusBadge tone="success">Отчеты и экспорт</StatusBadge>}
        description="Формирование файлов по успеваемости и посещаемости с сохранением истории выгрузок."
        icon={<ClipboardList aria-hidden="true" size={34} />}
        title="Отчеты"
      />

      <section className="reports-layout">
        <form className="panel report-builder" onSubmit={handleSubmit}>
          <SectionToolbar title="Новый отчет" />

          <div className="report-option-grid">
            {reportTypeOptions.map((option) => (
              <button
                className={`report-option ${reportType === option.value ? "is-active" : ""}`}
                key={option.value}
                onClick={() => setReportType(option.value)}
                type="button"
              >
                <span className="report-option__icon">
                  {option.value === "grades" ? <FileSpreadsheet aria-hidden="true" size={20} /> : <FileText aria-hidden="true" size={20} />}
                </span>
                <strong>{option.label}</strong>
                <span>{option.description}</span>
              </button>
            ))}
          </div>

          <div className="form-grid form-grid--two">
            <SelectField label="Группа" onChange={(event) => setFilters((current) => ({ ...current, group: event.target.value }))} options={groupOptions} value={filters.group} />
            <SelectField label="Дисциплина" onChange={(event) => setFilters((current) => ({ ...current, subject: event.target.value }))} options={subjectOptions} value={filters.subject} />
            <SelectField label="Период" onChange={(event) => setFilters((current) => ({ ...current, period: event.target.value }))} options={periodOptions} value={filters.period} />
            <SelectField label="Студент" onChange={(event) => setFilters((current) => ({ ...current, student: event.target.value }))} options={studentOptions} value={filters.student} />
          </div>

          <div className="section-toolbar">
            <div>
              <h2>Формат</h2>
              <div className="segmented-control" role="group">
                {formatOptions.map((format) => (
                  <button className={fileFormat === format.value ? "is-active" : ""} key={format.value} onClick={() => setFileFormat(format.value)} type="button">
                    {format.label}
                  </button>
                ))}
              </div>
            </div>
            <Button disabled={generateMutation.isPending} icon={<Download aria-hidden="true" size={16} />} type="submit" variant="primary">
              {generateMutation.isPending ? "Формируем" : "Сформировать"}
            </Button>
          </div>

          <FormError text={formError} />

          {generatedReport ? (
            <div className="report-ready">
              <div>
                <strong>Отчет сформирован</strong>
                <span>{reportTypeLabels[generatedReport.report_type]} · {formatLabels[generatedReport.file_format]}</span>
              </div>
              <Button icon={<Download aria-hidden="true" size={16} />} onClick={() => openReport(generatedReport)} variant="secondary">
                Скачать
              </Button>
            </div>
          ) : null}
        </form>

        <aside className="panel report-summary">
          <SummaryItem label="Всего выгрузок" value={reports.length.toString()} />
          <SummaryItem label="Успеваемость" value={reports.filter((report) => report.report_type === "grades").length.toString()} />
          <SummaryItem label="Посещаемость" value={reports.filter((report) => report.report_type === "attendance").length.toString()} />
        </aside>
      </section>

      <section className="panel">
        <SectionToolbar title="История отчетов">
          <TextField icon={<Search aria-hidden="true" size={16} />} label="Поиск" onChange={(event) => setSearch(event.target.value)} placeholder="Тип, формат или фильтры" value={search} />
        </SectionToolbar>
        <DataTable columns={historyColumns} data={filteredReports} emptyText="Сформированных отчетов пока нет." getRowKey={(row) => row.id} />
      </section>
    </section>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="report-summary__item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function FormError({ text }: { text: string | null }) {
  return text ? <div className="form-error">{text}</div> : null;
}

function buildParameters(filters: FilterForm): ReportParameters {
  return Object.fromEntries(
    Object.entries(filters)
      .filter(([, value]) => value)
      .map(([key, value]) => [key, Number(value)]),
  ) as ReportParameters;
}

function openReport(report: ReportRequest) {
  const url = getReportDownloadUrl(report);
  if (url) {
    window.open(url, "_blank", "noopener,noreferrer");
  }
}

function renderReportParameters(parameters: ReportParameters) {
  const entries = Object.entries(parameters).filter(([, value]) => value);

  if (!entries.length) {
    return <span className="muted-text">Без фильтров</span>;
  }

  return (
    <div className="report-params">
      {entries.map(([key, value]) => (
        <span key={key}>{parameterLabels[key] ?? key}: {value}</span>
      ))}
    </div>
  );
}

const parameterLabels: Record<string, string> = {
  group: "Группа",
  period: "Период",
  student: "Студент",
  subject: "Дисциплина",
};

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(value));
}

function getApiErrorMessage(error: unknown): string {
  if (error instanceof AxiosError && error.response?.data) {
    return flattenError(error.response.data);
  }
  return "Не удалось сформировать отчет. Проверьте фильтры и повторите попытку.";
}

function flattenError(value: unknown): string {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(flattenError).join(" ");
  if (value && typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${flattenError(item)}`)
      .join(" ");
  }
  return "Ошибка формирования отчета.";
}
