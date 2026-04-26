from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus import Image
from io import BytesIO

def generate_pdf_report(
    df,
    duplicates_removed,
    insights,
    ai_summary=None,
    dashboard_plan=None,
    prep_execution_log=None,
    chart_images=None
):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AI-Powered Data Analyst Report", styles["Title"]))
    story.append(Spacer(1, 16))

    # Dataset Overview
    story.append(Paragraph("1. Dataset Overview", styles["Heading2"]))

    overview_data = [
        ["Metric", "Value"],
        ["Rows", str(df.shape[0])],
        ["Columns", str(df.shape[1])],
        ["Numeric Columns", str(len(df.select_dtypes(include="number").columns))],
        ["Missing Values", str(int(df.isnull().sum().sum()))],
    ]

    overview_table = Table(overview_data)
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(overview_table)
    story.append(Spacer(1, 14))

    # Cleaning Summary
    story.append(Paragraph("2. Automatic Data Cleaning", styles["Heading2"]))
    story.append(Paragraph(f"Duplicates removed: {duplicates_removed}", styles["Normal"]))
    story.append(Paragraph(
        "Missing values handled automatically: numeric columns were filled with mean, categorical columns with mode.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 14))

    # Preparation Log
    story.append(Paragraph("3. Data Preparation Log", styles["Heading2"]))

    if prep_execution_log:
        for item in prep_execution_log:
            story.append(Paragraph(f"- {item}", styles["Normal"]))
    else:
        story.append(Paragraph("No advanced data preparation actions were applied.", styles["Normal"]))

    story.append(Spacer(1, 14))

    # Insights
    story.append(Paragraph("4. Generated Insights", styles["Heading2"]))

    if insights:
        for insight in insights:
            story.append(Paragraph(f"- {insight}", styles["Normal"]))
    else:
        story.append(Paragraph("No insights generated.", styles["Normal"]))

    story.append(Spacer(1, 14))

    # AI Summary
    story.append(Paragraph("5. AI Summary", styles["Heading2"]))

    if ai_summary:
        story.append(Paragraph(ai_summary, styles["Normal"]))
    else:
        story.append(Paragraph("AI summary was not generated.", styles["Normal"]))

    story.append(Spacer(1, 14))

    # Dashboard Plan
    story.append(Paragraph("6. AI Dashboard Plan", styles["Heading2"]))

    if dashboard_plan:
        story.append(Paragraph(
            f"Dashboard Title: {dashboard_plan.get('dashboard_title', 'Recommended Dashboard')}",
            styles["Normal"]
        ))

        kpis = dashboard_plan.get("kpis", [])
        if kpis:
            story.append(Paragraph("Recommended KPIs:", styles["Heading3"]))
            for kpi in kpis:
                story.append(Paragraph(f"- {kpi}", styles["Normal"]))

        charts = dashboard_plan.get("charts", [])
        if charts:
            story.append(Paragraph("Recommended Charts:", styles["Heading3"]))
            for chart in charts:
                title = chart.get("title", "Chart")
                chart_type = chart.get("chart_type", "unknown")
                reason = chart.get("reason", "")
                story.append(Paragraph(f"- {title} ({chart_type}): {reason}", styles["Normal"]))
    else:
        story.append(Paragraph("AI dashboard plan was not generated.", styles["Normal"]))
    
    # Charts
    story.append(Paragraph("7. Dashboard Charts", styles["Heading2"]))

    if chart_images:
        for chart_title, image_buffer in chart_images:
            story.append(Paragraph(chart_title, styles["Heading3"]))

            img = Image(image_buffer, width=400, height=240)
            story.append(img)
            story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("No charts were added to the report.", styles["Normal"]))
    doc.build(story)

    buffer.seek(0)
    return buffer