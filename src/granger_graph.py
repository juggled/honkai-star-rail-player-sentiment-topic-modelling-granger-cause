# Import required libraries
import seaborn as sns
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Function to pivot
def pivot(df, str):
    df = duckdb.sql(f"""PIVOT df
                    ON Topic
                    USING MAX("Sentiment_Times_Feedback_Count")
                    GROUP BY Date, 'Revenue (USD)'
                    ORDER BY Date""").df()
    df.drop('Cyrene Feedback', axis=1, inplace=True)
    df.dropna(inplace=True)
    df = duckdb.sql(f"""SELECT DISTINCT Date, "Revenue (USD)", "{str}" FROM df ORDER BY Date""").df()
    print(f'{str} is pivoted!\n')
    return df

# Import dataframe
df = pd.read_csv('data/02-processed/merged_reviews_revenue.csv')

# Add column
df['Sentiment_Times_Feedback_Count'] = df['Avg_Sentiment'] * df['Feedback_Count'] 

# From grangercausalitytests.py
topic_lag = {
    'Story/Dialogue': 3,
    'General Feedback': 1,
    'Power Creep': 2,
    'Gacha Feedback': 1,
    'Login Issues': 2
}

# Make a results to store results
results = []

# For each topic and lag from dictionary
for topic, lag in topic_lag.items():
    # Call function to pivot it into df_lag
    df_lag = pivot(df, topic)

    # Create a revenue in millions for graph
    df_lag['Revenue (Millions, USD)'] = df_lag['Revenue (USD)'] / 1000000

    # Create shifted column with the given lag
    df_lag['Lag'] = df_lag[topic].shift(lag)

    # Sort it by date
    df_lag.sort_values(by=['Date'])

    # Drop any columns that are empty
    df_lag.dropna(inplace=True)

    # Create figure with one axis
    fig, ax1 = plt.subplots(figsize = (19,6))

    # Add the second axis
    ax2 = ax1.twinx()
    
    # Make the scatter plot for Revenue (Millions, USD) and Lag and Date
    sns.scatterplot(x='Date', y='Revenue (Millions, USD)', data=df_lag, ax=ax1, color='Green')
    sns.scatterplot(x='Date', y='Lag', data=df_lag, ax=ax2)
    sns.lineplot(x='Date', y='Revenue (Millions, USD)', data=df_lag, ax=ax1, color='Green')
    sns.lineplot(x='Date', y='Lag', data=df_lag, ax=ax2)
    ax1.set_title(f"Granger Causality Graph of {topic}, with a Time Lag of {lag}")
    ax2.set_ylabel(f'{topic} shifted by {lag} period')

    # Ensure it's within the plot
    plt.tight_layout()

    # Make a copy of lag to drop empty again
    df_lag_copy = df_lag.dropna(subset=topic).copy()

    # Save figures
    if topic == 'Story/Dialogue':
        plt.savefig(f"data/03-fig/StoryDialogue_{lag}_lag.png")
    else:
        plt.savefig(f"data/03-fig/{topic}_{lag}_lag.png")
    
    # Dataframe to append later on
    topic_results = df_lag[['Date', 'Revenue (USD)']].copy()

    # Add back in the default 
    topic_results['Topic'] = topic
    topic_results['Lag'] = lag

    # Calculations
    topic_results['correlation'] = df_lag['Lag'].corr(df_lag['Revenue (USD)'])
    # abs(old) was done as sentiment times feedback had many negative and positive values
    topic_results['sentimentxfeedback_%_change'] = 100*df_lag[topic].diff() / df_lag[topic].abs().shift()
    topic_results['revenue_%_change'] = df_lag['Revenue (USD)'].dropna().pct_change() * 100
    topic_results['sentimentxfeedback_'] = df_lag[topic].diff()
    topic_results['revenue_absolute_change'] = df_lag['Revenue (USD)'].diff()

    # Clean the topic up, wouldn't work outside of it for some reason
    clean_topic = topic.replace('/','_').replace(' ', '_')

    # Calculate trendline
    if topic == 'Story/Dialogue':
        plt.savefig(f"data/03-fig/StoryDialogue_{lag}_lag.png")
        df_lag_copy.rename(columns={
            'Story/Dialogue': 'Story_Dialogue'
        }, inplace=True)
        model = smf.ols(formula = f'Q("Revenue (USD)") ~ Story_Dialogue', data= df_lag_copy).fit()
        topic_results['Trend'] = model.params['Story_Dialogue']
    else:
        df_lag_copy[clean_topic] = df_lag_copy[topic]
        model = smf.ols(formula = f'Q("Revenue (USD)") ~ Q("{clean_topic}")', data= df_lag_copy).fit()
        topic_results['Trend'] = model.params[f'Q("{clean_topic}")']
    # Append to results
    results.append(topic_results)

# Concat results into dataframe
results_df = pd.concat(results)
# Sort by Date
results_df.sort_values(by=['Date'], inplace=True)
# Save to CSV
results_df.to_csv("data/02-processed/date_revenue_topic_correlation_sentimentxfeedback__revenue_change_trend.csv", index = False)

# Aggregate
results_df = duckdb.sql("""SELECT Topic, 
                        MAX(LAG) as Lag, MAX(correlation) as Correlation,
                        MEDIAN("sentimentxfeedback_%_change") as "Median Sentiment Times Feedback Percentage Change", 
                        MEDIAN("revenue_%_change") as "Median Revenue Percentage Change",
                        MEDIAN("sentimentxfeedback_") as "Median Absolute Sentiment Times Feedback Change",
                        MEDIAN("revenue_absolute_change") as "Median Absolute Revenue Change",
                        MAX(Trend) as "Trendline Slope"
                        FROM results_df
                        GROUP BY Topic
                        ORDER BY Lag, Topic
                        """).df()

# Save
results_df.to_csv("data/02-processed/correlation_sentimentxfeedback__revenue_median_pct_change_trend.csv", index = False)
print("Saved to data/02-processed/date_revenue_topic_correlation_sentimentxfeedback__revenue_change_trend.csv and data/02-processed/correlation_sentimentxfeedback__revenue_median_pct_change_trend.csv")