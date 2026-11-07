from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.research import ProductResearchReport


def _text(value: object) -> str:
    return str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraph(value: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_text(value).replace("\n", "<br/>"), style)


def _list(values: list[str]) -> str:
    if not values:
        return "None reported"
    return "<br/>".join(f"• {_text(value)}" for value in values)


def _table(rows: list[list[Paragraph]], widths: list[float]) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173F5F")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F6F8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def generate_research_pdf(
    report: ProductResearchReport,
    *,
    original_filename: str,
) -> BytesIO:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=12,
        textColor=colors.HexColor("#173F5F"),
    )
    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#20639B"),
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
    )
    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=6.5,
        leading=8,
    )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
        title=report.product_name or "Product Label Research Report",
    )
    story = [
        _paragraph(
            report.product_name or "Product Label Research Report",
            title_style,
        ),
        _paragraph(f"Source image: {original_filename}", body_style),
        _paragraph(f"Category: {report.product_category}", body_style),
        _paragraph(f"Jurisdiction: {report.jurisdiction}", body_style),
        Spacer(1, 8),
        _paragraph("Overall Summary", heading_style),
        _paragraph(report.overall_summary, body_style),
    ]

    if report.ingredients:
        story.append(_paragraph("Ingredient Findings", heading_style))
        ingredient_headers = [
            "Ingredient", "Identity", "Function", "Origin", "Benefits",
            "Concerns", "Long-term evidence", "Status", "Explanation", "Sources",
        ]
        ingredient_rows = [[_paragraph(header, small_style) for header in ingredient_headers]]
        for finding in report.ingredients:
            ingredient_rows.append(
                [
                    _paragraph(finding.ingredient, small_style),
                    _paragraph(finding.identity, small_style),
                    _paragraph(finding.function, small_style),
                    _paragraph(finding.natural_or_synthetic, small_style),
                    _paragraph(_list(finding.potential_benefits), small_style),
                    _paragraph(_list(finding.potential_concerns), small_style),
                    _paragraph(finding.long_term_evidence, small_style),
                    _paragraph(finding.status, small_style),
                    _paragraph(finding.explanation, small_style),
                    _paragraph("<br/>".join(finding.source_ids) or "None", small_style),
                ]
            )
        story.append(
            _table(
                ingredient_rows,
                [0.72 * inch, 0.9 * inch, 0.8 * inch, 0.7 * inch, 0.9 * inch,
                 0.9 * inch, 1.15 * inch, 0.65 * inch, 1.1 * inch, 0.8 * inch],
            )
        )

    if report.claims:
        story.append(_paragraph("Claim Findings", heading_style))
        claim_headers = ["Claim", "Type", "Status", "Explanation", "Sources"]
        claim_rows = [[_paragraph(header, small_style) for header in claim_headers]]
        for finding in report.claims:
            claim_rows.append(
                [
                    _paragraph(finding.claim, small_style),
                    _paragraph(finding.claim_type, small_style),
                    _paragraph(finding.status, small_style),
                    _paragraph(finding.explanation, small_style),
                    _paragraph("<br/>".join(finding.source_ids) or "None", small_style),
                ]
            )
        story.append(
            _table(
                claim_rows,
                [1.7 * inch, 0.9 * inch, 0.8 * inch, 3.4 * inch, 1.0 * inch],
            )
        )

    if report.sources:
        story.append(_paragraph("Sources", heading_style))
        source_headers = ["ID", "Title", "Type", "Publisher", "URL", "Quoted text", "Relevance"]
        source_rows = [[_paragraph(header, small_style) for header in source_headers]]
        for source in report.sources:
            source_rows.append(
                [
                    _paragraph(source.source_id, small_style),
                    _paragraph(source.title, small_style),
                    _paragraph(source.source_type, small_style),
                    _paragraph(source.publisher, small_style),
                    _paragraph(source.url, small_style),
                    _paragraph(source.quoted_text, small_style),
                    _paragraph(source.relevance, small_style),
                ]
            )
        story.append(
            _table(
                source_rows,
                [0.65 * inch, 1.25 * inch, 0.75 * inch, 0.95 * inch,
                 1.6 * inch, 2.2 * inch, 1.35 * inch],
            )
        )

    story.extend(
        [
            _paragraph("Limitations", heading_style),
            _paragraph(_list(report.limitations), body_style),
            Spacer(1, 10),
            _paragraph(
                "This report is informational and is not legal, medical, or regulatory advice.",
                small_style,
            ),
        ]
    )
    document.build(story)
    buffer.seek(0)
    return buffer
