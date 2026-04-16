from datetime import datetime, timedelta, date as date_type
from io import BytesIO
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ── Helpers ──────────────────────────────────────────────────────────────────

def compute_hours(start_time, end_time, break_minutes: int, direct_hours=None) -> float:
    if direct_hours is not None:
        return round(float(direct_hours), 2)
    fmt = "%H:%M"
    start = datetime.strptime(start_time, fmt)
    end = datetime.strptime(end_time, fmt)
    if end <= start:  # overnight shift
        end += timedelta(days=1)
    total_minutes = int((end - start).total_seconds() / 60) - break_minutes
    return round(max(0, total_minutes) / 60, 2)


def _iso_to_date(iso: str) -> date_type:
    return datetime.strptime(iso, "%Y-%m-%d").date()


# ── Styles ───────────────────────────────────────────────────────────────────

def _thin_border():
    t = Side(style="thin")
    return Border(left=t, right=t, top=t, bottom=t)


def _apply(cell, value=None, bold=False, size=11, align_h="left", align_v="center",
           wrap=False, border=False, number_format=None):
    if value is not None:
        cell.value = value
    cell.font = Font(bold=bold, size=size)
    cell.alignment = Alignment(horizontal=align_h, vertical=align_v, wrap_text=wrap)
    if border:
        cell.border = _thin_border()
    if number_format:
        cell.number_format = number_format


# ── Week sheet builder ────────────────────────────────────────────────────────

ROWS_PER_DAY = 5
COL_WIDTHS = {
    "A": 10.43, "B": 8.43, "C": 12.71, "D": 13.14, "E": 49.43,
    "F": 11.43, "G": 10.57, "H": 4.14, "I": 4.43, "J": 3.86,
    "K": 7.43,  "L": 8.0,
}


def _build_week_sheet(ws, user, block_start: date_type, week_shifts):
    """Populate ws with one week of timesheet data.

    block_start is the first day of the 7-day pay period block.
    Days are derived from the actual dates so any start day is handled correctly.
    """
    border = _thin_border()
    block_end = block_start + timedelta(days=6)

    # ── Row heights ───────────────────────────────────────────────────────────
    ws.row_dimensions[1].height = 29.25
    ws.row_dimensions[2].height = 12.75
    ws.row_dimensions[3].height = 8.25
    ws.row_dimensions[4].height = 15.0
    ws.row_dimensions[5].height = 15.0
    for r in range(6, 42):
        ws.row_dimensions[r].height = 12.75
    ws.row_dimensions[41].height = 18.0

    # ── Column widths ─────────────────────────────────────────────────────────
    for col_letter, width in COL_WIDTHS.items():
        ws.column_dimensions[col_letter].width = width

    # ── Row 1: Title ──────────────────────────────────────────────────────────
    ws.merge_cells("A1:L1")
    _apply(ws["A1"], "TIME SHEET", bold=True, size=16, align_h="center")

    # ── Row 2: Name / Employer / Week ending ──────────────────────────────────
    ws.merge_cells("A2:L2")
    employer = user.employer or ""
    week_ending = block_end.strftime("%d/%m/%Y")
    header_text = (
        f"NAME :   {user.name.upper()}"
        f"{'        ' + employer.upper() if employer else ''}"
        f"        WEEK ENDING :   {week_ending}"
    )
    _apply(ws["A2"], header_text, bold=True, size=12)

    # ── Rows 4–5: Column headers (double-row) ─────────────────────────────────
    for col, val in [
        ("B", "JOB No"), ("C", "CLIENT"), ("D", "JOB NAME"),
        ("E", "DESCRIPTION OF WORK CARRIED OUT"),
        ("F", "Depart from"), ("G", "Arrive at"),
        ("H", "1.0"), ("I", "1.5"), ("J", "2.0"),
        ("K", "TRAV."), ("L", "TRAV."),
    ]:
        c = ws[f"{col}4"]
        size = 8 if col in ("F", "G") else (10 if col in ("H", "I", "J", "K", "L") else 11)
        align_h = "center" if col in ("H", "I", "J", "K", "L") else "left"
        _apply(c, val, bold=True, size=size, align_h=align_h, border=True)

    _apply(ws["A5"], "DATE", bold=True, size=12, border=True)
    _apply(ws["F5"], "Depart Time", bold=True, size=8, border=True)
    _apply(ws["G5"], "Arrival Time", bold=True, size=8, border=True)
    _apply(ws["K5"], "30KM", bold=True, size=10, align_h="center", border=True)
    _apply(ws["L5"], "50KM", bold=True, size=10, align_h="center", border=True)

    # ── Day blocks (rows 6–40) ────────────────────────────────────────────────
    by_date = defaultdict(list)
    for shift in week_shifts:
        by_date[shift.date].append(shift)

    for day_idx in range(7):
        day_date = block_start + timedelta(days=day_idx)
        day_name = day_date.strftime("%A").upper()
        row_start = 6 + day_idx * ROWS_PER_DAY
        is_weekend = day_date.weekday() >= 5  # Sat or Sun

        _apply(
            ws.cell(row=row_start, column=1),
            day_name,
            bold=is_weekend,
            size=8,
            align_h="center",
            border=True,
        )

        for r in range(row_start, row_start + ROWS_PER_DAY):
            for c in range(1, 13):
                ws.cell(row=r, column=c).border = border

        day_shifts = by_date.get(day_date.strftime("%Y-%m-%d"), [])
        for i, shift in enumerate(day_shifts[:ROWS_PER_DAY]):
            r = row_start + i
            hours = compute_hours(
                shift.start_time, shift.end_time,
                shift.break_minutes, shift.direct_hours,
            )

            if shift.job_name:
                _apply(ws.cell(row=r, column=4), shift.job_name, size=10, align_h="center")
            if shift.notes:
                _apply(ws.cell(row=r, column=5), shift.notes, size=10)
            if shift.start_time:
                _apply(ws.cell(row=r, column=6), shift.start_time, size=10, align_h="center")
            if shift.end_time:
                _apply(ws.cell(row=r, column=7), shift.end_time, size=10, align_h="center")

            h_cell = ws.cell(row=r, column=8)
            h_cell.value = hours
            h_cell.font = Font(size=10)
            h_cell.alignment = Alignment(horizontal="center", vertical="center")
            h_cell.number_format = "0.##"

    # ── Row 41: NOTES ─────────────────────────────────────────────────────────
    ws.merge_cells("A41:L41")
    _apply(ws["A41"], "NOTES", bold=True, size=12)

    # ── Row 42: Total hours summary ───────────────────────────────────────────
    ws.row_dimensions[42].height = 15.0
    total = sum(
        compute_hours(s.start_time, s.end_time, s.break_minutes, s.direct_hours)
        for s in week_shifts
    )
    ws.merge_cells("A42:G42")
    _apply(ws["A42"], f"TOTAL HOURS :   {round(total, 2)}", bold=True, size=11, border=True)

    job_totals = defaultdict(float)
    for s in week_shifts:
        job_totals[s.job_name] += compute_hours(
            s.start_time, s.end_time, s.break_minutes, s.direct_hours
        )
    ws.row_dimensions[43].height = 12.75
    summary = "   ".join(f"{job}: {round(h, 2)}h" for job, h in sorted(job_totals.items()))
    ws.merge_cells("A43:L43")
    _apply(ws["A43"], summary, size=10)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_excel(user, shifts, period_start: str, period_end: str) -> bytes:
    """Generate an xlsx matching the original timesheet format.
    One sheet per 7-day block of the pay period, starting from period_start.
    This avoids splitting shifts across Mon-Sun calendar weeks.
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    start = _iso_to_date(period_start)
    end = _iso_to_date(period_end)

    block_start = start
    while block_start <= end:
        block_end = block_start + timedelta(days=6)

        block_shifts = [
            s for s in shifts
            if block_start <= _iso_to_date(s.date) <= block_end
        ]

        if block_shifts:
            sheet_name = f"Week {block_start.strftime('%-d %b')}"
            ws = wb.create_sheet(title=sheet_name)
            _build_week_sheet(ws, user, block_start, block_shifts)

        block_start += timedelta(days=7)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
