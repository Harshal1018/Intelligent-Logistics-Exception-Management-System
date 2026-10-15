from __future__ import annotations

from datetime import datetime
from io import BytesIO
import math
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


NAVY = colors.HexColor('#123A70')
BLUE = colors.HexColor('#2563EB')
PALE_BLUE = colors.HexColor('#EFF6FF')
TEXT = colors.HexColor('#1F2937')
MUTED = colors.HexColor('#64748B')
RULE = colors.HexColor('#D8E1EC')


def _display_value(value: Any) -> str:
    if value is None or value == '' or (isinstance(value, float) and math.isnan(value)):
        return 'Not available'
    return escape(str(value))


def generate_shipment_pdf(shipment: dict, prediction: dict) -> BytesIO:
    """Build a branded PDF report for one shipment and its delay-risk estimate."""
    pdf = BytesIO()
    document = SimpleDocTemplate(
        pdf,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.7 * inch,
        title=f"Shipment {shipment.get('shipment_id', 'Details')}",
        author='Intelligent Logistics Exception Management System',
    )
    base_styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=base_styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        textColor=NAVY,
        alignment=0,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=MUTED,
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=base_styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=NAVY,
        spaceBefore=10,
        spaceAfter=7,
    )
    label_style = ParagraphStyle(
        'FieldLabel',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    )
    value_style = ParagraphStyle(
        'FieldValue',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=TEXT,
    )
    note_style = ParagraphStyle(
        'ReportNote',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=MUTED,
    )

    fields = [
        ('Shipment ID', shipment.get('shipment_id')),
        ('Customer ID', shipment.get('customer_id')),
        ('Carrier', shipment.get('carrier_id')),
        ('Origin hub', shipment.get('origin_hub_id')),
        ('Destination hub', shipment.get('destination_hub_id')),
        ('Shipment type', shipment.get('shipment_type')),
        ('Priority', shipment.get('priority')),
        ('Current status', shipment.get('status')),
        ('Weight', f"{_display_value(shipment.get('weight_kg'))} kg"),
        ('Distance', f"{_display_value(shipment.get('distance_km'))} km"),
        ('SLA allowance', f"{_display_value(shipment.get('sla_hours'))} hours"),
        ('Planned delivery', shipment.get('planned_delivery_datetime')),
        ('Actual delivery', shipment.get('actual_delivery_datetime')),
        ('Delayed', 'Yes' if shipment.get('delay_flag') == 1 else 'No'),
        ('SLA breached', 'Yes' if shipment.get('sla_breach') == 1 else 'No'),
        ('Record created', shipment.get('created_at')),
    ]
    rows = [
        [Paragraph(label, label_style), Paragraph(_display_value(value), value_style)]
        for label, value in fields
    ]
    detail_table = Table(rows, colWidths=[2.05 * inch, 4.75 * inch], hAlign='LEFT')
    detail_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.35, RULE),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    risk_category = _display_value(prediction.get('risk_category'))
    risk_probability = _display_value(prediction.get('delay_probability'))
    risk_action = _display_value(prediction.get('recommended_action'))
    risk_table = Table(
        [
            [
                Paragraph('<font color="#64748B">ESTIMATED DELAY RISK</font><br/>'
                          f'<font size="19" color="#123A70"><b>{risk_probability}%</b></font>',
                          base_styles['Normal']),
                Paragraph(f'<font color="#64748B">RISK LEVEL</font><br/><b>{risk_category}</b>',
                          base_styles['Normal']),
            ],
            [
                Paragraph('<font color="#64748B">RECOMMENDED ACTION</font>', base_styles['Normal']),
                Paragraph(risk_action, base_styles['Normal']),
            ],
        ],
        colWidths=[2.05 * inch, 4.75 * inch],
        hAlign='LEFT',
    )
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE_BLUE),
        ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor('#BFDBFE')),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#BFDBFE')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 1), (0, 1)),
        ('LEFTPADDING', (0, 0), (-1, -1), 11),
        ('RIGHTPADDING', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
    ]))

    story = [
        Paragraph('Shipment Record', title_style),
        Paragraph('Operational shipment details and delivery risk assessment', subtitle_style),
        Spacer(1, 13),
        Paragraph('SHIPMENT INFORMATION', section_style),
        detail_table,
        Paragraph('DELIVERY RISK ASSESSMENT', section_style),
        risk_table,
        Spacer(1, 9),
        Paragraph(
            'Risk prediction is an estimate generated by the logistics system and should be '
            'used alongside current operational information.',
            note_style,
        ),
    ]

    def draw_page(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        page_width, page_height = letter
        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica-Bold', 9)
        canvas.drawString(doc.leftMargin, page_height - 0.48 * inch, 'ILEMS')
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(
            doc.leftMargin + 0.48 * inch,
            page_height - 0.48 * inch,
            'INTELLIGENT LOGISTICS EXCEPTION MANAGEMENT',
        )
        canvas.setStrokeColor(RULE)
        canvas.line(doc.leftMargin, page_height - 0.58 * inch, page_width - doc.rightMargin,
                    page_height - 0.58 * inch)
        canvas.line(doc.leftMargin, 0.52 * inch, page_width - doc.rightMargin, 0.52 * inch)
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(doc.leftMargin, 0.34 * inch, 'SHIPMENT REPORT  |  INTERNAL OPERATIONS')
        canvas.drawRightString(page_width - doc.rightMargin, 0.34 * inch,
                               f'Generated {datetime.now():%d %b %Y, %H:%M}  |  Page {doc.page}')
        canvas.restoreState()

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    pdf.seek(0)
    return pdf
