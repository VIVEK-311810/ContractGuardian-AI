"""
PDF Report Generator
Creates downloadable PDF reports of contract analysis
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import re


def generate_pdf_report(analysis_results: dict, filename: str = "contract_analysis.pdf") -> BytesIO:
    """
    Generate a PDF report from analysis results including plain text negotiation report

    Args:
        analysis_results: Complete analysis results dictionary with negotiation_report
        filename: Output filename

    Returns:
        BytesIO object containing the PDF
    """

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Container for PDF elements
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=8,
        spaceBefore=12
    )

    # Title
    story.append(Paragraph("ContractGuardian AI Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Metadata
    metadata_text = f"""
    <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    <b>Job ID:</b> {analysis_results.get('job_id', 'N/A')}<br/>
    <b>Powered by:</b> IBM WatsonX Orchestrate (3-Agent Architecture)
    """
    story.append(Paragraph(metadata_text, styles['Normal']))
    story.append(Spacer(1, 20))

    # Quick Summary
    story.append(Paragraph("Quick Summary", heading_style))

    risk_score = analysis_results.get('risk_score', 0)
    risk_level = analysis_results.get('risk_level', 'Unknown')
    recommendation = analysis_results.get('recommendation', 'N/A')

    summary_data = [
        ['Risk Score', str(risk_score) + '/10'],
        ['Risk Level', risk_level],
        ['Recommendation', recommendation]
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Extracted Entities
    if 'entities' in analysis_results:
        story.append(Paragraph("Extracted Information", heading_style))

        entities = analysis_results['entities']

        # Parties
        if 'parties' in entities:
            parties = entities['parties']
            story.append(Paragraph("<b>Parties:</b>", styles['Normal']))
            story.append(Paragraph(f"Client: {parties.get('client', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Contractor: {parties.get('contractor', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Dates
        if 'dates' in entities:
            dates = entities['dates']
            story.append(Paragraph("<b>Key Dates:</b>", styles['Normal']))
            story.append(Paragraph(f"Effective: {dates.get('effective_date', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Expiration: {dates.get('expiration_date', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Payment Terms
        if 'payment_terms' in entities:
            payment = entities['payment_terms']
            story.append(Paragraph("<b>Payment Terms:</b>", styles['Normal']))
            story.append(Paragraph(f"Amount: {payment.get('total_amount', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Schedule: {payment.get('payment_schedule', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Net Days: {payment.get('net_days', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 20))

    # High-Risk Clauses
    if 'high_risk_clauses' in analysis_results:
        story.append(Paragraph("High-Risk Clauses", heading_style))

        for idx, clause in enumerate(analysis_results['high_risk_clauses'], 1):
            story.append(Paragraph(f"<b>{idx}. {clause.get('clause_name', 'Unknown')} (Risk: {clause.get('risk_score', 0)}/10)</b>", styles['Normal']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Text:</b> {clause.get('text', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>Explanation:</b> {clause.get('explanation', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 6))

            if clause.get('precedent'):
                story.append(Paragraph(f"<b>Precedent:</b> {clause.get('precedent')}", styles['Normal']))

            story.append(Spacer(1, 12))

    # Page break before negotiation report
    story.append(PageBreak())

    # Comprehensive Negotiation Report
    if 'negotiation_report' in analysis_results:
        story.append(Paragraph("Comprehensive Negotiation Strategy Report", heading_style))
        story.append(Spacer(1, 12))

        report_text = analysis_results['negotiation_report']

        # Parse and format the plain text report
        # Split by major section headers (I., II., III., etc.)

        # Add custom style for report sections
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )

        subsection_style = ParagraphStyle(
            'SubsectionStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4,
            spaceBefore=6,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            leading=14
        )

        # Split report into lines for processing
        lines = report_text.split('\n')

        for line in lines:
            line = line.strip()

            # Skip decorative lines and empty lines
            if not line or line.startswith('═') or line.startswith('─'):
                continue

            # Skip title line
            if 'CONTRACT NEGOTIATION STRATEGY REPORT' in line:
                continue

            # Major section headers (I., II., III., etc.)
            if re.match(r'^[IVX]+\.\s+[A-Z\s]+$', line):
                story.append(Spacer(1, 12))
                story.append(Paragraph(line, section_style))
                story.append(Spacer(1, 6))

            # Subsection headers (bold with colon or numbered)
            elif line.endswith(':') or re.match(r'^\d+\.', line) or line.isupper():
                story.append(Paragraph(f"<b>{line}</b>", subsection_style))

            # Bullet points
            elif line.startswith('•') or line.startswith('-'):
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{line}", body_style))

            # Regular paragraphs
            else:
                # Escape special characters for reportlab
                line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Don't try to parse bold markers - just render as plain text
                story.append(Paragraph(line_escaped, body_style))

    # Footer
    story.append(Spacer(1, 30))
    footer_text = "Generated by ContractGuardian | Powered by IBM WatsonX Orchestrate"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.grey)))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return buffer
