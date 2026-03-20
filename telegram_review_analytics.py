import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob


# Load the CSV file with the first line as the header and handle irregular delimiters and bad lines
df = pd.read_csv("outputs/charts/TelegramReviews_2024.csv", delimiter='\t', engine='python')


# Check if 'Date' column is present
if 'Date' in df.columns:
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
else:
    print("Error: 'Date' column is not found in the DataFrame")

# Drop duplicates
df = df.drop_duplicates()

# Collecting basic information
info_data = {
    "Column": df.columns,
    "Non-Null Count": df.notnull().sum(),
    "Dtype": df.dtypes.astype(str)  # Convert dtype to string for JSON serialization
}
info_df = pd.DataFrame(info_data)

# Summary statistics, rounded to two decimal places
summary_df = df.describe().T.round(2)

# Check for missing values
missing_values = df.isnull().sum()

# Combine all information into one dataframe
combined_info = info_df.join(summary_df, how='outer')
combined_info['Missing Values'] = missing_values

# Ensure all data types are serializable
combined_info = combined_info.astype(str)

# Display combined information table using Plotly
fig_info = go.Figure(data=[go.Table(
    header=dict(values=list(combined_info.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[combined_info[col] for col in combined_info.columns],
               fill_color='lavender',
               align='left'))
])

fig_info.update_layout(title='Data Overview')
fig_info.show()

# Print column names separated by spaces
print("Columns in DataFrame:")

# Check if 'review_date' column is present

# Print the values of the 'review_date' column
print("Values in 'review_date' column:")
print(df.head)

# Convert 'review_date' column to datetime, with errors set to 'coerce' to handle invalid dates
df['review_date'] = pd.to_datetime(df['review_date'], format='%d %B %Y', errors='coerce')

# Check for rows where conversion failed
invalid_dates = df[df['review_date'].isna()]

# Print out invalid dates if any
if not invalid_dates.empty:
    print("Invalid dates found:\n", invalid_dates)

# Now you can use the .dt accessor to extract the month
df['Month'] = df['review_date'].dt.to_period('M')
df['Month'] = df['Month'].astype(str)

# Number of reviews over time (line chart)
df_reviews_over_time = df.groupby('Month').size().reset_index(name='Count')

# Calculate the average score for each month
df_avg_score = df.groupby('Month')['review_score'].mean().reset_index(name='AvgScore')

# Number of reviews by score over time (bar chart)
df_scores_monthly = df.groupby(['Month', 'review_score']).size().reset_index(name='Count')

# Calculate percentage for each score in each month
df_scores_monthly['Percentage'] = df_scores_monthly.groupby('Month')['Count'].transform(lambda x: 100 * x / x.sum())
# Colors for scores
colors = {
    1: 'red',
    2: '#ff6666',
    3: '#ffcc99',
    4: '#99ff99',
    5: 'green'
}

# Function to get the color based on the average score
def get_color(avg_score):
    if avg_score <= 1.5:
        return colors[1]
    elif avg_score <= 2.5:
        return colors[2]
    elif avg_score <= 3.5:
        return colors[3]
    elif avg_score <= 4.5:
        return colors[4]
    else:
        return colors[5]

# Plot the combined chart
fig1 = go.Figure()

# Add the line chart with markers
fig1.add_trace(go.Scatter(
    x=df_reviews_over_time['Month'],
    y=df_reviews_over_time['Count'],
    mode='lines',
    name='Total Reviews',
    hoverinfo='skip'  # Remove hover information for the line graph
))

# Add the circles representing the average score, placed on the line graph
fig1.add_trace(go.Scatter(
    x=df_avg_score['Month'],
    y=df_reviews_over_time['Count'],
    mode='markers',
    marker=dict(
        size=df_avg_score['AvgScore'] * 15,  # Scale the size of the circles to be much larger
        color=[get_color(score) for score in df_avg_score['AvgScore']],  # Color based on the average score
        showscale=False
    ),
    name='Average Score',
    text=df_avg_score['AvgScore'].round(2),  # Display the average score as text
    textposition='top center'
))

# Ensure keys are floats
colors = {float(key): value for key, value in colors.items()}

# Default color to use if a score is not found in the colors dictionary
default_color = 'grey'  # You can choose any color you prefer

# Add the bar chart for each score
for score in sorted(df['review_score'].unique()):
    df_score = df_scores_monthly[df_scores_monthly['review_score'] == score]
    fig1.add_trace(go.Bar(
        x=df_score['Month'],
        y=df_score['Count'],
        name=f'review_score {score}',
        marker_color=colors.get(float(score), default_color),  # Use .get() method with default color
        text=df_score['Percentage'].round(2).astype(str) + '%',
        textposition='outside'
    ))

fig1.update_layout(
    barmode='group',
    title='Number of Reviews Over Time by Score',
    xaxis_title='Month',
    yaxis_title='Number of Reviews',
    font=dict(
        size=18,  # Adjust the overall font size
    ),
    margin=dict(r=200),  # Adjust margin to make space for the legend annotations
    bargap=0.1,  # Gap between bars of the same group
    bargroupgap=0.2,  # Gap between bars of different groups
    template='plotly_white',  # Apply the professional theme
)
fig1.show()

# Sentiment analysis
def get_polarity(text):
    if isinstance(text, str):
        return TextBlob(text).sentiment.polarity
    else:
        return 0.0  # or some other default value, or np.nan if you prefer

df['Polarity'] = df['review_positives'].apply(get_polarity)

# Plot sentiment polarity
fig2 = px.histogram(df, x='Polarity', nbins=30, title='Distribution of Review Sentiment Polarity')
fig2.update_layout(xaxis_title='Sentiment Polarity', yaxis_title='Frequency', legend_title='Polarity')
fig2.show()
