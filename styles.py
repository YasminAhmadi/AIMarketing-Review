from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Heading1'],
    fontName='Times-Bold',  # Use a serif font for a more professional look
    alignment=TA_CENTER,
    fontSize=22,
    leading=26,
    textColor=colors.black  # Use black for better contrast and readability
)

header_style = ParagraphStyle(
    'HeaderStyle',
    parent=styles['Heading2'],
    fontName='Times-Bold',
    alignment=TA_LEFT,  # Align headers to the left for better readability
    fontSize=18,
    leading=20,
    textColor=colors.black  # Use a slightly gray color for headers
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['BodyText'],
    fontName='Times-Roman',  # Use a serif font for the body text
    alignment=TA_JUSTIFY,  # Justify the body text for a more professional look
    fontSize=12,
    leading=16,
    textColor=colors.black  # Use black for better readability
)
bold_style = ParagraphStyle(
    'BoldStyle',
    parent=body_style,
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=14
)
footer_style = ParagraphStyle(
    'FooterStyle',
    parent=styles['BodyText'],
    fontName='Times-Italic',  # Use an italic font for footer text
    alignment=TA_CENTER,
    fontSize=10,
    leading=12,
    textColor=colors.black  # Use a light gray color for footer text
)