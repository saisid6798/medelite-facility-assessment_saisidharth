from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class ReportService:
    @staticmethod
    def safe(value):
        if value is None:
            return "N/A"
        value = str(value).strip()
        return value if value else "N/A"

    def generate_pdf(self, report_data, manual_data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=30,
            bottomMargin=30,
            title="Facility Assessment Snapshot",
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "MedeliteTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=1,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=8,
        )
        subtitle_style = ParagraphStyle(
            "MedeliteSubtitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#111827"),
            spaceAfter=12,
        )
        section_style = ParagraphStyle(
            "SectionStyle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#111827"),
            spaceBefore=10,
            spaceAfter=6,
        )
        note_style = ParagraphStyle(
            "NoteStyle",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#4B5563"),
        )

        story = []
        state = self.safe(report_data.get("state"))
        ccn = self.safe(report_data.get("ccn"))

        story.append(Paragraph("INFINITE — Managed by MEDELITE", title_style))
        story.append(Paragraph(f"FACILITY ASSESSMENT SNAPSHOT<br/>{state}", subtitle_style))

        facility_rows = [
            ["Name of Facility", self.safe(manual_data.get("facility_name"))],
            ["Location", self.safe(report_data.get("location"))],
            ["EMR", self.safe(manual_data.get("emr"))],
            ["Census Capacity", self.safe(report_data.get("census_capacity"))],
            ["Current Census", self.safe(manual_data.get("current_census"))],
            ["Type of Patient", self.safe(manual_data.get("patient_type"))],
            ["Previous Coverage from Medelite", self.safe(manual_data.get("previous_coverage"))],
            ["Previous Provider Performance from Medelite", self.safe(manual_data.get("provider_performance"))],
            ["Medical Coverage", self.safe(manual_data.get("medical_coverage"))],
        ]
        story.append(self._make_table(facility_rows))

        story.append(Paragraph("STAR RATINGS", section_style))
        ratings_rows = [
            ["Overall Star Rating", self.safe(report_data.get("overall_rating"))],
            ["Health Inspection", self.safe(report_data.get("health_inspection"))],
            ["Staffing", self.safe(report_data.get("staffing"))],
            ["Quality of Resident Care", self.safe(report_data.get("quality_of_resident_care"))],
        ]
        story.append(self._make_table(ratings_rows))

        story.append(Paragraph("HOSPITALIZATION & ED METRICS", section_style))
        hosp_rows = [
            ["Short Term Hospitalization", self.safe(report_data.get("str_hosp"))],
            ["STR National Avg. for Hospitalization", self.safe(report_data.get("str_hosp_nat"))],
            ["STR State Avg. for Hospitalization", self.safe(report_data.get("str_hosp_state"))],
            ["STR ED Visit", self.safe(report_data.get("str_ed"))],
            ["STR ED Visits National Avg.", self.safe(report_data.get("str_ed_nat"))],
            ["STR ED Visits State Avg.", self.safe(report_data.get("str_ed_state"))],
            ["LT Hospitalization", self.safe(report_data.get("lt_hosp"))],
            ["LT National Avg. for Hospitalization", self.safe(report_data.get("lt_hosp_nat"))],
            ["LT State Avg. for Hospitalization", self.safe(report_data.get("lt_hosp_state"))],
            ["ED Visit", self.safe(report_data.get("lt_ed"))],
            ["LT ED Visits National Avg.", self.safe(report_data.get("lt_ed_nat"))],
            ["LT ED Visits State Avg.", self.safe(report_data.get("lt_ed_state"))],
        ]
        story.append(self._make_table(hosp_rows))

        story.append(Spacer(1, 12))
        medicare_url = f"https://www.medicare.gov/care-compare/details/nursing-home/{ccn}"
        story.append(
            Paragraph(
                f'Source: <link href="{medicare_url}">Medicare Care Compare Profile</link>',
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                "Facility metadata and star ratings are sourced from CMS Provider Information. "
                "Hospitalization and ED metrics are sourced from CMS Medicare Claims Quality Measures and State/US Averages when available.",
                note_style,
            )
        )

        doc.build(story)
        buffer.seek(0)
        return buffer

    def _make_table(self, rows):
        table = Table(rows, colWidths=[250, 260], repeatRows=0)
        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E5E7EB")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        return table
