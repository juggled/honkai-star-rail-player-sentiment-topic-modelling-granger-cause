# Import required libraries
import duckdb
import pandas as pd

# File paths
reviews = 'data/02-processed/modeled_reviews.csv'
revenue = 'data/01-raw/date_revenue.xlsx'

# Transform into dataframes
df_reviews = pd.read_csv(reviews)
df_revenue = pd.read_excel(revenue)

# Convert date columns to datetime
df_revenue['Date'] = pd.to_datetime(df_revenue['Date'])
df_reviews['Year_Month_Date'] = pd.to_datetime(df_reviews['Year_Month_Date'])

# SQL to merge dataframes on month and year, calculating complaint count and average sentiment per topic
# CTE to grab complaint count and average sentiment per topic per month, then an inner join to revenue data on month and year
merged_df = duckdb.sql("""
WITH complaint_count_sentiment_avg AS (
    SELECT DATE_TRUNC('month', Year_Month_Date) AS Year_Month,
    CustomName AS Topic,
    COUNT(*) AS Complaint_Count,
    AVG(compound) AS Avg_Sentiment FROM df_reviews
    GROUP BY Year_Month, CustomName
    ORDER BY Year_Month)
SELECT a.Date, a.Expanded as 'Revenue (USD)', b.Topic, b.Complaint_Count, b.Avg_Sentiment
    FROM df_revenue a
    INNER JOIN complaint_count_sentiment_avg b 
    ON a.Date = b.Year_Month""").df()

# Print merged_df for user to see, save to CSV and let the user know it saved
print(merged_df)
merged_df.to_csv('data/02-processed/merged_reviews_revenue.csv', index=False)
print("Saved to data/02-processed/merged_reviews_revenue.csv!")