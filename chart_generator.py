import json

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os


def process_attributes(df, date_column, attribute_column, score_column, save_path):
    # Get unique attributes
    attributes = df[attribute_column].unique()

    create_barchart(df, attribute_column, score_column, save_path)

    # Create a line chart for each attribute
    for attribute in attributes:
        attribute_df = df[df[attribute_column] == attribute].sort_values(by=date_column)
        print(20*'++', '\n', f"{attribute} chart processing!")
        create_linechart(attribute_df, date_column, score_column, title=attribute, chart_type="attribute", save_path=save_path)
        create_hist(df=attribute_df, score_column=score_column, date_column=date_column, title=f"Mean Score for {attribute}", save_path=os.path.join(save_path, f"attribute_{attribute}_hist.png"))


def create_linechart(df, date_column, score_column, title, chart_type, save_path):
    df = df[[score_column, date_column]].copy()
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column)
    df = df[df[date_column].dt.year == 2024]

    # Resample the data to ensure continuous lines and fill missing values
    resampled = df.set_index(date_column).resample('D').mean().fillna(method='ffill').fillna(method='bfill')

    # Calculate mean and standard deviation over a rolling window
    df = pd.DataFrame({
        score_column: resampled[score_column].rolling(window=32, min_periods=1).mean(),
        f'{score_column}_std': resampled[score_column].rolling(window=32, min_periods=1).std(),
        'count': resampled[score_column].rolling(window=64, min_periods=1).count()
    })

    # for _, row in df.iterrows():
    #     print(f"{row.index}: {row[score_column]}")

    df = df.dropna()

    # Define new colors for lines and circles
    line_color = 'rgb(0, 51, 102)'  # Deep blue for lines
    circle_color = 'rgb(255, 0, 127)'  # Vibrant magenta for circles

    fig = go.Figure()

    # Add line trace with shaded area for standard deviation
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[score_column],
        mode='lines',
        line=dict(color=line_color),
        name='review_score'
    ))

    # Add shaded area for standard deviation
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[score_column] + df[f'{score_column}_std'],
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        name='Upper Bound',
        fill=None
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[score_column] - df[f'{score_column}_std'],
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'),
        fill='tonexty',
        fillcolor='rgba(0,0,0,0.1)',
        name='Standard Deviation'
    ))

    # Add circle markers with labels
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[score_column],
        mode='markers+text',
        marker=dict(size=df['count'] * 6, sizemode='area', color=circle_color,
                    line=dict(color='black', width=1)),  # New size and color of the markers
        name='Number of Reviews',
        showlegend=False
    ))

    fig.update_layout(
        template='plotly_white',  # Apply the professional theme
        # title=dict(
        #     text=f'Score and Number of Reviews by Date for {title}',
        #     font=dict(size=30)  # Title font size
        # ),
        xaxis=dict(
            title=dict(
                text='review_date',
                font=dict(size=30)  # X-axis title font size
            ),
            showgrid=True,  # Show gridlines for better readability
            gridcolor='lightgrey',
            tickfont=dict(size=26)
        ),
        yaxis=dict(
            title=dict(
                text='review_score',
                font=dict(size=30)  # Y-axis title font size
            ),
            showgrid=True,  # Show gridlines for better readability
            gridcolor='lightgrey',
            tickfont=dict(size=26)
        ),
        legend=dict(
            font=dict(
                family='Arial, sans-serif',
                size=30,
                color='black'
            )
        ),
        width=1600,  # Adjust width
        height=1000,  # Adjust height
        margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins for a cleaner look
    )

    # Save the figure as an image file
    file_path = os.path.join(save_path, f"{chart_type}_{title}_linechart.png")
    fig.write_image(file_path, format='png')
    print("Charts created successfully!")


def create_pie_chart(df, sentiment_column, save_path):
    # Extract the sentiment column and count the occurrences of each sentiment
    sentiment_counts = df[sentiment_column].value_counts()

    # Define a custom color palette including 'mixed'
    color_discrete_map = {
        'positive': '#2ECC71',  # Green
        'negative': '#E74C3C',  # Red
        'mixed': '#9B59B6'  # Purple
    }

    # Create a pie chart using Plotly with custom colors and percentages
    fig = px.pie(sentiment_counts,
                 values=sentiment_counts.values,
                 names=sentiment_counts.index,
                 title='Sentiment Distribution',
                 color=sentiment_counts.index,
                 color_discrete_map=color_discrete_map,
                 hole=0.4)

    # Update the hoverinfo to display percentages
    fig.update_traces(textinfo='percent+label',
                      hoverinfo='label+percent',
                      textfont_size=28)  # Increase the size of the labels

    # Customize the layout for the title, annotations, and legend
    fig.update_layout(title_font_size=32,  # Increase the size of the title
                      title_x=0.5,  # Center the title
                      legend_title_font_size=28,  # Increase the size of the legend title
                      legend_font_size=28,  # Increase the size of the legend labels
                      plot_bgcolor='rgba(255, 255, 255, 0)',  # Transparent plot background
                      paper_bgcolor='rgba(255, 255, 255, 0.7)',  # Semi-transparent paper background
                      annotations=[dict(text='Sentiment', x=0.5, y=0.5, font_size=28, showarrow=False)],
                      width=1600,  # Adjust width
                      height=1000,  # Adjust height
                      margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins for a cleaner look
                      )  # Add central text

    # Save the pie chart as a PNG image
    fig.write_image(save_path)


def create_word_cloud(df, sentiment_column, keyword_column, positive_save__path, negative_save_path):
    positive_df = df[df[sentiment_column] == 'positive']
    negative_df = df[df[sentiment_column] == 'negative']

    # Extract keywords and join them into a single string
    positive_keywords_list = positive_df[keyword_column].tolist() #.apply(ast.literal_eval).explode()
    positive_keywords_list = [string for sublist in positive_keywords_list for string in sublist]
    negative_keywords_list = negative_df[keyword_column].tolist() #.apply(ast.literal_eval).explode()
    negative_keywords_list = [string for sublist in negative_keywords_list for string in sublist]

    positive_keywords_text = ' '.join(positive_keywords_list)
    negative_keywords_text = ' '.join(negative_keywords_list)

    # Create stopwords set
    stopwords = set(STOPWORDS)

    # Load the mask image with transparent background
    # Load the mask images with transparent background
    positive_mask_image_path = 'src/utils/wordcloud_images/like.png'
    negative_mask_image_path = 'src/utils/wordcloud_images//dislike.png'

    positive_mask_image = np.array(Image.open(positive_mask_image_path))
    negative_mask_image = np.array(Image.open(negative_mask_image_path))

    # Generate the word clouds with the masks
    try:
        positive_wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=stopwords,
                                       mask=positive_mask_image, contour_width=3, contour_color='steelblue',
                                       colormap='summer').generate(positive_keywords_text)
    except Exception as e:
        print(e)
        positive_wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=stopwords,
                                       mask=negative_mask_image, contour_width=3, contour_color='steelblue',
                                       colormap='autumn').generate("NoWords")
    try:
        negative_wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=stopwords,
                                       mask=negative_mask_image, contour_width=3, contour_color='steelblue',
                                       colormap='autumn').generate(negative_keywords_text)
    except Exception as e:
        print(e)
        negative_wordcloud = WordCloud(width=800, height=800, background_color='white', stopwords=stopwords,
                                       mask=negative_mask_image, contour_width=3, contour_color='steelblue',
                                       colormap='autumn').generate("NoWords")
    # Display the word cloud
    plt.figure(figsize=(10, 10))
    plt.imshow(positive_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    # Save the word cloud to a file
    positive_wordcloud.to_file(positive_save__path)

    # Display the word cloud
    plt.figure(figsize=(10, 10))
    plt.imshow(negative_wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    # Save the word cloud to a file
    negative_wordcloud.to_file(negative_save_path)


def create_barchart(df, attribute_column, score_column, save_path):
    attribute_avg_scores = df.groupby(attribute_column)[score_column].mean().round(2).reset_index()
    attribute_avg_scores.columns = ['Attribute', 'Average Score']

    # Create the bar chart
    fig = px.bar(attribute_avg_scores, x='Attribute', y='Average Score',
                 title='Average Score for Each Attribute',
                 labels={'Attribute': 'Attribute', 'Average Score': 'Average Score'},
                 color='Attribute',
                 color_discrete_sequence=px.colors.qualitative.Vivid,
                 text='Average Score')  # Display the average score on the bars

    # Update layout for better visualization
    fig.update_layout(title_font_size=32,  # Increase the size of the title
                      title_x=0.5,  # Center the title
                      legend_title_font_size=24,  # Increase the size of the legend title
                      legend_font_size=24,  # Increase the size of the legend labels
                      plot_bgcolor='rgba(255, 255, 255, 0)',  # Transparent plot background
                      paper_bgcolor='rgba(255, 255, 255, 0.7)',  # Semi-transparent paper background
                      width=1600,  # Adjust width
                      height=1000,  # Adjust height
                      margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins for a cleaner look
                      xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
                      xaxis_title_font_size=28,  # Increase x-axis title font size
                      yaxis_title_font_size=28,  # Increase y-axis title font size
                      xaxis=dict(tickfont=dict(size=24)),  # Increase x-axis tick font size
                      yaxis=dict(tickfont=dict(size=24))  # Increase y-axis tick font size
                      )

    # Save the bar chart as an image file
    save_path = os.path.join(save_path, "allAttributesAverageScore.png")
    fig.write_image(save_path)


def create_hist(df, score_column, date_column, save_path, title, days=15):
    # Convert date column to datetime
    df = df[[score_column, date_column]].copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Filter data for the year 2024
    df = df[df[date_column].dt.year == 2024]
    
    # Sort the dataframe by date
    df = df.sort_values(date_column)
    
    # Set date column as index
    df.set_index(date_column, inplace=True)
    
    # Resample data to the specified number of days and calculate mean
    resampled_df = df.resample(f'{days}D', label='left').mean()
    
    # Count the number of samples in each period
    counts = df.resample(f'{days}D').size()
    
    # Add the counts as a new column to the resampled dataframe
    resampled_df['Counts'] = counts.values
    
    # Calculate the minimum score from the resampled dataframe
    min_score = resampled_df[score_column].min()
    max_score = resampled_df[score_column].max()
    """
    # Create a bar plot
    fig = px.bar(resampled_df, x=resampled_df.index, y=score_column, color='Counts', color_continuous_scale='Bluered',
                 labels={'x': 'Date', 'y': 'Score'}, title=title)
    
    # Update layout to customize appearance
    fig.update_layout(title_font_size=32,  # Increase the size of the title
                      title_x=0.5,  # Center the title
                      legend_title_font_size=26,  # Increase the size of the legend title
                      legend_font_size=30,  # Increase the size of the legend labels
                      plot_bgcolor='rgba(255, 255, 255, 0)',  # Transparent plot background
                      paper_bgcolor='rgba(255, 255, 255, 0.7)',  # Semi-transparent paper background
                      width=1600,  # Adjust width
                      height=1000,  # Adjust height
                      margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins for a cleaner look
                      xaxis_tickangle=-45,  # Rotate x-axis labels for better readability
                      xaxis_title_font_size=28,  # Increase x-axis title font size
                      yaxis_title_font_size=28,  # Increase y-axis title font size
                      xaxis=dict(tickfont=dict(size=24)),  # Increase x-axis tick font size
                      yaxis=dict(tickfont=dict(size=24)),  # Increase y-axis tick font size
                      legend=dict(font=dict(size=28)),  # Increase the size of the legend labels

                      )


    fig.update_layout(yaxis_range=[min_score - 1, max_score + 1])

    # Update trace text font size
    fig.update_traces(textfont_size=20)
    """

    # Create the bar chart
    fig = go.Figure(data=go.Bar(
        x=resampled_df.index,
        y=resampled_df[score_column],
        marker=dict(
            color=resampled_df['Counts'],
            colorscale='Bluered',
            colorbar=dict(
                thickness=28,  # Adjust the width of the colorbar
                title='Counts',  # Title of the colorbar
                titleside='right',
                titlefont=dict(size=26),  # Font size of the colorbar title
                tickfont=dict(size=24)  # Font size of the colorbar ticks
            )
        ),
        textfont=dict(size=30)
    ))

    # Update layout to customize appearance
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=32)),  # Title configuration
        xaxis=dict(
            title='review_date',
            tickangle=-45,
            title_font=dict(size=30),
            tickfont=dict(size=26)
        ),  # X-axis configuration
        yaxis=dict(
            title='review_score',
            range=[min_score - 1, max_score + 1],
            title_font=dict(size=30),
            gridcolor='rgba(0, 0, 0, 1)',
            tickfont=dict(size=26)
        ),  # Y-axis configuration
        legend=dict(
            title_font=dict(size=28),
            font=dict(size=32)
        ),  # Legend configuration
        plot_bgcolor='rgba(255, 255, 255, 0)',  # Transparent plot background
        paper_bgcolor='rgba(255, 255, 255, 0.5)',  # Semi-transparent paper background
        width=1600,  # Adjust width
        height=1000,  # Adjust height
        margin=dict(l=50, r=50, t=100, b=50)  # Adjust margins for a cleaner look
    )

    # Save the figure to a file
    fig.write_image(save_path)


if __name__ == "__main__":
    with open("../product_review_criteria.json") as f:
        data = json.load(f)
    print(data)
