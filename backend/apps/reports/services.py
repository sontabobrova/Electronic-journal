from __future__ import annotations

import csv
import tempfile
from dataclasses import dataclass
from pathlib import Path

from django.core.files import File
from django.db.models import QuerySet
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from apps.education.models import StudentProfile
from apps.journal.models import AttendanceRecord, Grade

from .models import ReportFormat, ReportRequest, ReportType


@dataclass(frozen=True)
class ReportData:
    title: str
    headers: list[str]
    rows: list[list[str]]


def filter_grades(user, parameters: dict) -> QuerySet[Grade]:
    queryset = Grade.objects.select_related(
        "student__user",
        "student__group",
        "work__assignment__subject",
        "work__assignment__group",
        "work__assignment__period",
        "work__assignment__teacher__user",
    )
    if user.is_teacher and not user.is_system_admin:
        queryset = queryset.filter(work__assignment__teacher__user=user)
    elif user.is_student:
        queryset = queryset.filter(student__user=user)

    if group_id := parameters.get("group"):
        queryset = queryset.filter(student__group_id=group_id)
    if subject_id := parameters.get("subject"):
        queryset = queryset.filter(work__assignment__subject_id=subject_id)
    if period_id := parameters.get("period"):
        queryset = queryset.filter(work__assignment__period_id=period_id)
    if student_id := parameters.get("student"):
        queryset = queryset.filter(student_id=student_id)
    return queryset.order_by("student__group__name", "student__student_id", "work__work_date")


def filter_attendance(user, parameters: dict) -> QuerySet[AttendanceRecord]:
    queryset = AttendanceRecord.objects.select_related(
        "student__user",
        "student__group",
        "session__assignment__subject",
        "session__assignment__group",
        "session__assignment__period",
        "session__assignment__teacher__user",
    )
    if user.is_teacher and not user.is_system_admin:
        queryset = queryset.filter(session__assignment__teacher__user=user)
    elif user.is_student:
        queryset = queryset.filter(student__user=user)

    if group_id := parameters.get("group"):
        queryset = queryset.filter(student__group_id=group_id)
    if subject_id := parameters.get("subject"):
        queryset = queryset.filter(session__assignment__subject_id=subject_id)
    if period_id := parameters.get("period"):
        queryset = queryset.filter(session__assignment__period_id=period_id)
    if student_id := parameters.get("student"):
        queryset = queryset.filter(student_id=student_id)
    return queryset.order_by("student__group__name", "student__student_id", "session__session_date")


def build_grades_data(user, parameters: dict) -> ReportData:
    headers = ["ID студента", "Студент", "Группа", "Дисциплина", "Период", "Работа", "Дата", "Оценка", "Макс. балл"]
    rows = [
        [
            str(grade.student.student_id),
            grade.student.user.get_full_name() or grade.student.user.username,
            grade.student.group.name,
            grade.work.assignment.subject.name,
            grade.work.assignment.period.name,
            grade.work.title,
            grade.work.work_date.isoformat(),
            str(grade.value),
            str(grade.work.max_score),
        ]
        for grade in filter_grades(user, parameters)
    ]
    return ReportData(title="Отчет по успеваемости", headers=headers, rows=rows)


def build_attendance_data(user, parameters: dict) -> ReportData:
    headers = ["ID студента", "Студент", "Группа", "Дисциплина", "Период", "Занятие", "Дата", "Статус"]
    rows = [
        [
            str(record.student.student_id),
            record.student.user.get_full_name() or record.student.user.username,
            record.student.group.name,
            record.session.assignment.subject.name,
            record.session.assignment.period.name,
            record.session.topic,
            record.session.session_date.isoformat(),
            record.get_status_display(),
        ]
        for record in filter_attendance(user, parameters)
    ]
    return ReportData(title="Отчет по посещаемости", headers=headers, rows=rows)


def build_report_data(user, report_type: str, parameters: dict) -> ReportData:
    if report_type == ReportType.GRADES:
        return build_grades_data(user, parameters)
    return build_attendance_data(user, parameters)


def write_csv(path: Path, data: ReportData) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data.title])
        writer.writerow(data.headers)
        writer.writerows(data.rows)


def write_xlsx(path: Path, data: ReportData) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Отчет"
    worksheet.append([data.title])
    worksheet.append(data.headers)
    for row in data.rows:
        worksheet.append(row)
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 42)
    workbook.save(path)


def write_pdf(path: Path, data: ReportData) -> None:
    font_name = get_pdf_font_name()
    document = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    styles["Title"].fontName = font_name
    table_data = [data.headers] + data.rows
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
            ]
        )
    )
    document.build([Paragraph(data.title, styles["Title"]), table])


def get_pdf_font_name() -> str:
    font_name = "DejaVuSans"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(candidate)))
            return font_name
    return "Helvetica"


def generate_report_file(report: ReportRequest) -> None:
    data = build_report_data(report.requested_by, report.report_type, report.parameters)
    suffix = report.file_format
    with tempfile.NamedTemporaryFile(suffix=f".{suffix}", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    writers = {
        ReportFormat.CSV: write_csv,
        ReportFormat.XLSX: write_xlsx,
        ReportFormat.PDF: write_pdf,
    }
    writers[report.file_format](tmp_path, data)
    filename = f"report_{report.id}_{report.report_type}.{suffix}"
    with tmp_path.open("rb") as file:
        report.file.save(filename, File(file), save=True)
    tmp_path.unlink(missing_ok=True)


def validate_student_filter_access(user, parameters: dict) -> bool:
    if not user.is_student:
        return True
    student_id = parameters.get("student")
    if not student_id:
        return True
    return StudentProfile.objects.filter(id=student_id, user=user).exists()
