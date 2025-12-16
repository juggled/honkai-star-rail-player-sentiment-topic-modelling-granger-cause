# Import required libraries
from google_play_scraper import Sort, reviews_all
import pandas as pd
import numpy as np
import duckdb
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import demoji

# Function to get reviews from Google Play Store
def get_reviews():
    # Let the user know the function started
    print("Starting scraping!")

    # Scrape all reviews
    result = reviews_all(
        'com.HoYoverse.hkrpgoversea',
        sleep_milliseconds=0, # defaults to 0
        lang='en', # defaults to 'en'
        country='us', # defaults to 'us'
        sort=Sort.MOST_RELEVANT, # defaults to Sort.MOST_RELEVANT
        filter_score_with=None # defaults to None(means all score)
    )

    # Transform into Dataframe
    df = pd.DataFrame(result)
    
    # Save to CSV
    df.to_csv('data/01-raw/reviews.csv', index=False)
    
    # Print confirmation
    print("Raw saved to data/01-raw/reviews.csv!")
    
    # Return reviews
    return result

# Function to clean reviews and select columns
def sql_select():
    # Let the user know the function started
    print("Starting cleaning!")

    # Select file
    file_path = 'data/01-raw/reviews.csv'
    
    # Load CSV as Dataframe
    df = pd.read_csv(file_path)
    
    # Drop blanks for demoji to run
    df = df.dropna(how='any')
    
    # Remove emojis
    df['content'] = df['content'].apply(demoji.replace, repl='')
    
    # Turn blanks to NaN
    df['content'] = df['content'].replace('', np.nan)

    # Remove non-english entries
    df[df['content'].astype(str).map(lambda x: x.isascii())]

    # Regex for characters that we can keep
    pattern = r'[^a-zA-Z0-9\s.,!?;:\'"()-]'

    # Keep only wanted patterns and replace those without empty strings
    df['content'] = df['content'].str.replace(pattern, '', regex=True)

    # Remove extra spaces
    df['content'] = df['content'].str.replace(r'\s+', ' ', regex=True)

    # Strip leading and trailing spaces
    df['content'] = df['content'].str.strip()

    # Keep only those at least contain alphanumeric characters and drops the rest
    df = df[df['content'].str.contains(r'[a-zA-Z0-9]', na=False)]
    
    # Drop empty again, just in case
    df = df.dropna(how='any')

    # Use DuckDB to select specific columns
    result_df = duckdb.sql("SELECT \"at\", STRFTIME(CAST(\"at\" AS TIMESTAMP), '%Y-%m-%d') AS Year_Month_Date, content, score  FROM df").df()
    
    # Return Dataframe
    return result_df

# Function to analyze sentiment
def sentimentAnalyzer(df):
    # Let the user know the function started
    print("Analyzing sentiment...")

    # Intialize sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Apply sentiment analysis
    df['scores'] = df['content'].apply(sid.polarity_scores)

    # Turn scores dictionary into separate columns
    df[['neg', 'neu', 'pos', 'compound']] = df['scores'].apply(pd.Series)

    # Drop unnecessary columns
    df = df.drop(columns=['scores', 'neg', 'neu', 'pos'])

    # Save to CSV
    df.to_csv('data/02-processed/reviews_sentiment.csv', index=False)

    # Let the user know it saved
    print("Sentiment analysis and cleaning done, saved to reviews_sentiment.csv!")

    # Return Dataframe
    return df

# get_reviews()
# df = sql_select()
# df = sentimentAnalyzer(df)

# Main level user input
print("""1) Get reviews from Google Play Store and save to data/01-raw/reviews.csv
2) Clean reviews, select columns, analyze sentiment, and save to data/02-processed/reviews_sentiment.csv
3) Both 1, 2 and 3
      
Please select which step you would like to run:\n> """, end = "")

# Grab user input
user = input()

# Run function based on input
match user:
    case '1':
        get_reviews()
    case '2':
        df = sql_select()
        sentimentAnalyzer(df)