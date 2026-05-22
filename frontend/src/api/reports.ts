import { API_BASE_URL, apiClient } from "./client";

export type ReportType = "attendance" | "grades";
export type ReportFormat = "csv" | "pdf" | "xlsx";

export type ReportParameters = {
  group?: number;
  period?: number;
  student?: number;
  subject?: number;
};

export type ReportRequest = {
  id: number;
  report_type: ReportType;
  file_format: ReportFormat;
  parameters: ReportParameters;
  generated_at: string;
  file: string;
  download_url: string | null;
};

export type ReportGeneratePayload = {
  file_format: ReportFormat;
  parameters: ReportParameters;
  report_type: ReportType;
};

export async function fetchReportRequests(): Promise<ReportRequest[]> {
  const response = await apiClient.get<ReportRequest[]>("/api/reports/requests/");
  return response.data;
}

export async function generateReport(payload: ReportGeneratePayload): Promise<ReportRequest> {
  const response = await apiClient.post<ReportRequest>("/api/reports/requests/generate/", payload);
  return response.data;
}

export function getReportDownloadUrl(report: ReportRequest): string | null {
  const url = report.download_url || report.file;

  if (!url) {
    return null;
  }

  return url.startsWith("http") ? url : `${API_BASE_URL}${url}`;
}
