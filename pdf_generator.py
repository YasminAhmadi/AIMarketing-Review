import os
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle # type: ignore

from reportlab.lib.units import inch, cm # type: ignore

from src.utils.llm_call_functions import *
from langchain_openai import ChatOpenAI # type: ignore
from src.utils.prompts import *
from styles import *
from textProcessors import *

model = ChatOpenAI(temperature=0, model="gpt-4o")
# Get the current working directory
current_dir = os.path.join(Path.cwd(), "AquaventureResult")

img_index = 1
# Create the PDF file
pdf_file = os.path.join(current_dir, 'output.pdf')
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
elements = []


styles = getSampleStyleSheet()

title = Paragraph('Aquaventure Waterpark', title_style)
elements.append(title)
elements.append(Spacer(1, 0.5 * cm))
atlantis_url = 'https://www.google.com/travel/search?q=best%20hotel%20in%20dubai&g2lb=2503771%2C2503781%2C4814050%2C4874190%2C4893075%2C4965990%2C72277293%2C72302247%2C72317059%2C72406588%2C72414906%2C72420597%2C72421566%2C72458066%2C72462234%2C72470440%2C72470899%2C72471280%2C72472051%2C72473841%2C72481458%2C72485658%2C72486593%2C72494250%2C72513422%2C72513513%2C72536387%2C72538597%2C72543209%2C72549171%2C72556202%2C72570850%2C72572588%2C72577179%2C72582843%2C72582855&hl=en-IR&gl=ir&cs=1&ssta=1&ts=CAESCAoCCAMKAggDGh4SHBIUCgcI6A8QBhgEEgcI6A8QBhgFGAEyBAgAEAAqCQoFOgNJUlIoCA&qs=CAEyE0Nnb0l4WldCMUpqSWxzb0ZFQUU4CkIJCcVKgIpBWpQFQgkJOODwebhx2rNCCQl2KUo5Toz3R1pTCAEyT6oBTBABKg4iCmJlc3QgaG90ZWwoADIfEAEiGwGl8ZxFlP7WLrSHfG20UXqhRU_Q-hSQMLwqWzIXEAIiE2Jlc3QgaG90ZWwgaW4gZHViYWk&ap=KigKEgl_oX8Q2xQ5QBFvP4WY4ItLQBISCdABN6OrLzlAEW8_hfg8k0tAMABoAboBB3Jldmlld3M&ictx=111&ved=0CAAQ5JsGahcKEwjo4631pZWGAxUAAAAAHQAAAAAQCw'
aquaventure_url = 'https://www.google.com.pk/travel/entity/key/ChoI3eTz_5vPx8e3ARoNL2cvMTFmOHAzMXF5NRAE/reviews?utm_campaign=sharing&utm_medium=link&utm_source=htls&ts=CAEaBAoCGgAqBAoAGgA'

# Add the product/business description
general_review = "World's largest water park with over 105 slides, attractions & experiences, plus a splash area for kids."
business_info_dict = {"name": "Aquaventure", "type": "Waterpark", "about": general_review}
business_info_text = ""
for key in business_info_dict:
    business_info_text = business_info_text + f"{key}: {business_info_dict[key]}\n"
description = get_llm_output(model=model, prompt=prompt_business_info, input_dict={"info": business_info_text}, output_type="string")
# description = description + "\nThe reviews have been extracted from the page below" + "\n" + atlantis_url
description = description + f'\nThe data has been gathered from this <a href="{aquaventure_url}" color="blue">link</a>'
section_header = Paragraph('Introduction', header_style)
elements.append(section_header)

elements.extend([Paragraph(line, body_style) for line in description.split("\n")])
# content = Paragraph(description, body_style)

# elements.append(content)
######################################

elements.append(Spacer(1, 0.5 * cm))
elements.append(Paragraph('_' * 76, body_style))
elements.append(Spacer(1, 0.5 * cm))

########################################

# Add statistics about user's score
section_header = Paragraph('Scores Given By Users', header_style)
elements.append(section_header)
user_score_description = "Here we provide charts and statistics to better understand the scores given by the users"
elements.append(Paragraph(user_score_description, body_style))
elements.append(Spacer(1, 0.2 * inch))
df = pd.read_csv("AquaventureResult/resultCSV.csv")
stats = [["Statistic", "Value"], ["Mean", round(df['Score'].mean(), 2)], ["Median", round(df['Score'].median(), 2)], ["Standard Deviation", round(df['Score'].std(), 2)], ["Min", df['Score'].min()], ["Max", df['Score'].max()]]
table_style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                           ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                           ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                           ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                           ('FONTSIZE', (0,0), (-1,0), 12),
                           ('BOTTOMPADDING', (0,0), (-1,0), 12),
                           ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                           ('GRID', (0,0), (-1,-1), 1, colors.black)])
table = Table(stats, style=table_style)
elements.append(table)
elements.append(Spacer(1, 0.5 * inch))

# image_reader = ImageReader('Initial Results/UsersScorePlot.png')
# image_data = image_reader.getRGBData()
image = Image('AquaventureResult/userScore_UserScores_linechart.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. The line chart of scores given by users over time"
img_index += 1
footer = Paragraph(footer_text, footer_style)
elements.append(footer)

elements.append(Spacer(1, 0.5 * inch))

image = Image('AquaventureResult/UserScore_Histogram.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. The histogram of scores given by users over time"
img_index += 1
footer = Paragraph(footer_text, footer_style)
elements.append(footer)

##########################################################

elements.append(PageBreak())

##########################################################

section_header = Paragraph('Attributes of Reviews', header_style)
elements.append(section_header)
# attributes = ["Amenities", "Property Quality", "Cleanliness", "Service", "Price", "Comfort", "Location", "View", "Food Services", "Entertainment", "Room Variations", "Accessibility"]
with open("../product_review_criteria.json") as f:
    data = json.load(f)
attributes = data["Waterpark"]
attributes_description = "In our assessment of user reviews, we have selected several characteristics pertinent to waterpark analysis. This section elaborates on these characteristics and their connection to our evaluation."
attributes_description = attributes_description + "\n" + get_llm_output(model=model, prompt=prompt_business_attribute_description, input_dict={"info": business_info_text, "attributes": attributes}, output_type="string")
# attributes_description = 300 * "A"
attributes_description = attributes_description + "\n\nIn the next section, we will analyze the mentioned attributes specifically."
# elements.append(Paragraph(attributes_description, body_style))
# elements.extend(process_text(line))
elements.extend([Paragraph(process_markdown(line), body_style) for line in attributes_description.split("\n")])
elements.append(Spacer(1, 0.2 * cm))
# attributes_description = attributes_description.split('\n')
# elements.extend([Paragraph(line, body_style) for line in attributes_description])
image = Image('AquaventureResult/allAttributesAverageScore.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. bar chart for the average score given to each attribute"
img_index += 1

footer = Paragraph(footer_text, footer_style)
elements.append(footer)
##################################################

elements.append(PageBreak())

##################################################

# Add summary and chart for each attributes
summary_df = pd.read_csv("AquaventureResult/AttributesSummary.csv")
file_list = [file_name for file_name in os.listdir("AquaventureResult") if file_name.endswith(('.jpg', '.png')) and "attribute" in file_name.lower()]
print(file_list)
print(attributes)
for attribute in attributes:
    img_name = "No"
    try:
        section_header = Paragraph(attribute, header_style)
        elements.append(section_header)
        attr_row = summary_df.loc[summary_df['Attribute'] == attribute]
        attribute_summary = attr_row['Summary'].values[0]
        # elements.append(Paragraph(attribute_summary, body_style))
        elements.extend([Paragraph(process_markdown(line), body_style) for line in attribute_summary.split("\n")])
        imgs_name = [name for name in file_list if attribute in name]
        # line chart
        img_name = [name for name in imgs_name if "linechar" in name][0]
        img_path = os.path.join("AquaventureResult", img_name)
        image = Image(img_path, width=6 * inch, height=3.2 * inch)
        elements.append(image)
        footer_text = f"{img_index}. chart for {attribute} over time"
        img_index += 1
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
        elements.append(Spacer(1, 0.5 * inch))
        # histogram
        img_name = [name for name in imgs_name if "hist.png" in name][0]
        img_path = os.path.join("AquaventureResult", img_name)
        image = Image(img_path, width=6 * inch, height=3.2 * inch)
        elements.append(image)
        footer_text = f"{img_index}. Histogram for {attribute} over time"
        img_index += 1
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)

        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph('_' * 76, body_style))
        elements.append(Spacer(1, 0.5 * inch))
    except Exception as e:
        print(f"{img_name}")
##################################################

elements.append(PageBreak())

##################################################

section_header = Paragraph('Keyword Analysis', header_style)
elements.append(section_header)

user_score_description = "Charts below are created to show the amount and the number of words used in positive and negative reviews."
elements.append(Paragraph(user_score_description, body_style))
elements.append(Spacer(1, 0.2 * inch))
image = Image('AquaventureResult/PositiveWordCloud.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. Positive Keywords"
img_index += 1
footer = Paragraph(footer_text, footer_style)
elements.append(footer)

elements.append(Spacer(1, 0.3 * inch))

image = Image('AquaventureResult/negativeWordCloud.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. Negative Keywords"
img_index += 1
footer = Paragraph(footer_text, footer_style)
elements.append(footer)

##################################################

elements.append(PageBreak())

##################################################


section_header = Paragraph('Semantic Analysis', header_style)
elements.append(section_header)

user_score_description = "the chart below shows the percentage of negative, positive and mixed reviews"
elements.append(Paragraph(user_score_description, body_style))
elements.append(Spacer(1, 0.2 * inch))
image = Image('AquaventureResult/SentimentPieChart.png', width=6*inch, height=3.5*inch)
elements.append(image)
# elements.append(Spacer(1, 0.2 * inch))
footer_text = f"{img_index}. semantic pie chart"
img_index += 1
footer = Paragraph(footer_text, footer_style)
elements.append(footer)

##################################################

elements.append(PageBreak())

##################################################

section_header = Paragraph('Cost Report', header_style)
elements.append(section_header)

user_score_description = "At the end we have provided the cost of creating this report"
elements.append(Paragraph(user_score_description, body_style))

with open(os.path.join(current_dir, "PriceReport.txt")) as f:
    price_report = f.read().splitlines()
elements.extend([Paragraph(line, body_style) for line in price_report])

doc.build(elements, onFirstPage=lambda canvas, doc: canvas.setFont("Helvetica-Bold", 16))
