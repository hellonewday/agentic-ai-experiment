# report.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
import json

def generate_report(funnel_data, visuals, anomaly, llm_agent):
    try:
        if not funnel_data or not visuals or not anomaly:
            raise ValueError("Missing data for report generation")
        
        tone = input("Report tone (e.g., 'formal', 'concise', 'engaging') [default: engaging]: ") or "engaging"
        focus = input("Report focus (e.g., 'anomalies', 'recommendations', 'all') [default: all]: ") or "all"
        
        # Prompt moved to task description; simulate report content here
        max_dropoff = max(funnel_data["dropoffs"], default=0)
        max_drop_stage = funnel_data["stages"][funnel_data["dropoffs"].index(max_dropoff)] if max_dropoff > 0 else "N/A"
        report_content = f"""
# Funnel Drop-off Analysis Report

## Executive Summary
Analyzing over a million clickstream records, we identified a {max_dropoff:.1f}% drop-off at {max_drop_stage}.

## Methodology
Transformed raw logs into sessions, filtered for engagement, and analyzed the funnel.

## Funnel Analysis
[Insert Table Here]
[Insert Chart Here]

## Anomaly Insights
{anomaly}

## Recommendations
- Optimize {max_drop_stage}.
- Test UI changes.
- Gather user feedback.
"""
        
        pdf = SimpleDocTemplate("funnel_report.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        for section in report_content.split("\n\n"):
            if section.startswith("# "):
                elements.append(Paragraph(section[2:], styles["Title"]))
            elif section.startswith("## "):
                elements.append(Paragraph(section[3:], styles["Heading2"]))
            elif "[Insert Table Here]" in section:
                table = Table(visuals["table"])
                elements.append(table)
            elif "[Insert Chart Here]" in section:
                elements.append(Image(visuals["chart"], width=400, height=200))
            else:
                elements.append(Paragraph(section, styles["BodyText"]))
            elements.append(Spacer(1, 12))
        
        pdf.build(elements)
        print("Saved report to funnel_report.pdf")
        return "funnel_report.pdf"
    except Exception as e:
        print(f"Failed to generate report: {str(e)}")
        return None