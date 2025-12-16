# Import required libaries
from statsmodels.tsa.stattools import grangercausalitytests
import pandas as pd
import duckdb

# Pivot function
def pivot(df, str):
    df = duckdb.sql(f"""PIVOT df
                    ON Topic USING MAX({str})
                    GROUP BY Date, 'Revenue (USD)'
                    ORDER BY Date""").df()
    print(f'{str} is pivoted!\n')
    print(df.head())
    return df

# Granger function, df for dataframe, lag for the max lag, name for for the type
def granger(df, lag, name):
    print(f"Granger Causality Test Results for {name}:")
    # Dataframe to store Topic, Lag and P-value
    df_G = pd.DataFrame({
        'Topic': [],
        'Lag': [],
        'P-value': []
    })

    # Row to start 
    row_index = 0
    
    # For loop
    for topic in topics:

        # State the topic
        print(f"Topic: {topic}")
        
        # Cyrene's unique in that she's a recent release, but is 5% of total reviews. So it doesn't have enough dates, and is placed in a unique bit
        if topic == 'Cyrene Feedback':
            # Copy, and drop blanks with regards to Cyrene
            cyrene_df = df.dropna(subset=['Cyrene Feedback']).copy()

            # Cyrene's max lag is 1
            maxlag = 1
            
            # The lag value the Granger Causality test is on, starting at 0
            n = 0

            # Print the dataframe
            print(df)

            # Granger causality test
            result = grangercausalitytests(cyrene_df[['Revenue (USD)', topic]], maxlag=maxlag, verbose=True)
            
            # For loop to store everything
            for n in range(1, maxlag+1):
                df_G.at[row_index, 'Topic'] = topic
                df_G.at[row_index, 'Lag'] = n
                df_G.at[row_index, 'F-value'] = result[n][0]['ssr_ftest'][0]
                df_G.at[row_index, 'P-value'] = result[n][0]['ssr_ftest'][1]
                row_index+=1
        else:
            # Max lag is lag here
            maxlag = lag
            
            # The lag value the Granger Causality test is on, starting at 0
            n = 0
            
            # Drop Cyrene
            df_copy = df.drop('Cyrene Feedback', axis = 1).copy()
            
            # Drop empty
            df_copy.dropna(inplace=True)
            
            # Append a row to df_G with the topic under column Topic
            df_G.loc[len(df), 'Topic'] = topic
            
            # Granger causality test
            result = grangercausalitytests(df_copy[['Revenue (USD)', topic]], maxlag=maxlag, verbose=True)
            
            # For loop to store everything
            for n in range(1, lag+1):
                df_G.at[row_index, 'Topic'] = topic
                df_G.at[row_index, 'Lag'] = n
                df_G.at[row_index, 'F-value'] = result[n][0]['ssr_ftest'][0]
                df_G.at[row_index, 'P-value'] = result[n][0]['ssr_ftest'][1]
                row_index+=1
    # Sort values by p-value then f-value
    df_G.sort_values(by=[ 'P-value', 'F-value'], ascending=[True, False], inplace=True)
   
    # If it exists, append it, otherwise, overwrite
    try:
        with pd.ExcelWriter('data/02-processed/granger.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
            df_G.to_excel(writer, sheet_name = name, index = False)
    except:
        with pd.ExcelWriter('data/02-processed/granger.xlsx', mode="w", engine="openpyxl", if_sheet_exists="replace") as writer:
            df_G.to_excel(writer, sheet_name = name, index = False)
    return df

# Get datafarme
df = pd.read_csv('data/02-processed/merged_reviews_revenue.csv')

# Add column
df['Sentiment_Times_Feedback_Count'] = df['Avg_Sentiment'] * df['Feedback_Count'] 

# List of topics
topics = ['Cyrene Feedback', 'Gacha Feedback', 'General Feedback',
          'Login Issues', 'Optimization Feedback', 'Power Creep',
          'Story/Dialogue']

# Pivot them
df_sentiment = pivot(df, 'Avg_Sentiment')
df_feedback_count = pivot(df, 'Feedback_Count')
df_weighted = pivot(df, 'Sentiment_Times_Feedback_Count')

# Dictionary
dataframes = {'df_sentiment' : df_sentiment,
              'df_feedback_count': df_feedback_count,
              'df_weighted': df_weighted}

# For loop to go through Granger causality test
for name, frame in dataframes.items():
    granger(frame, 5, name)