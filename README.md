<h1 align = center>
📊 Data Analysis Project 📊
</h1>
<h3 align = center>
Modelling the Impact of Feedback and Customer Sentiment on Revenue
</h3>

---

## Steps to follow
1. Clone repository
```bash
git clone https://github.com/juggled/honkai-star-rail-player-sentiment-topic-modelling-granger-cause.git
```
2. Install requirements
```bash
pip3 install -r requirements.txt
```
3. There are five files. The first file to run is src/api_scrape_clean_sentiment.py to grab all the reviews from Google Play Store. The second file to run is src/model.py . The third file to run is src/merge_reviews_revenue.py . Data is already modelled and trained, so you may wish to skip these if you only want to preview the data. The fourth file to run is granger_causality_tests.py . The fifth file to run is granger_graph.py .

4. Run above said files in the directory outside of src.
```bash
cd HSR # Your folder containing bertopic_model, data, src, etc
```
```bash
python src/api_scrape_clean_sentiment.py # Grab reviews, clean data and analyze sentiment
```
```bash
python src/model.py # Model your reviews and save them
```
```bash
python src/merge_reviews_revenue.py # Merge them with date_revenue.xlsx and save it
```
```bash
python src/granger_causality_tests.py # Deduce the impact of topics on revenue
```
```bash
python src/granger_graph.py # Quantify the above
```
5. To see a word cloud of the reviews, please see src/wordcloud_reviews.ipynb and run it. Alternative, see wordcloud_reviews.png in data/03-fig.
---
## Explanation of files
### File directory
``` bash
📦honkai-star-rail-player-sentiment-topic-modelling-granger-cause
 ┣ 📂.git
 ┃ ┣ 📂hooks
 ┃ ┃ ┣ 📜applypatch-msg.sample
 ┃ ┃ ┣ 📜commit-msg.sample
 ┃ ┃ ┣ 📜fsmonitor-watchman.sample
 ┃ ┃ ┣ 📜post-update.sample
 ┃ ┃ ┣ 📜pre-applypatch.sample
 ┃ ┃ ┣ 📜pre-commit.sample
 ┃ ┃ ┣ 📜pre-merge-commit.sample
 ┃ ┃ ┣ 📜pre-push.sample
 ┃ ┃ ┣ 📜pre-rebase.sample
 ┃ ┃ ┣ 📜pre-receive.sample
 ┃ ┃ ┣ 📜prepare-commit-msg.sample
 ┃ ┃ ┣ 📜push-to-checkout.sample
 ┃ ┃ ┣ 📜sendemail-validate.sample
 ┃ ┃ ┗ 📜update.sample
 ┃ ┣ 📂info
 ┃ ┃ ┗ 📜exclude
 ┃ ┣ 📂objects
 ┃ ┃ ┣ 📂info
 ┃ ┃ ┗ 📂pack
 ┃ ┣ 📂refs
 ┃ ┃ ┣ 📂heads
 ┃ ┃ ┗ 📂tags
 ┃ ┣ 📜config
 ┃ ┣ 📜description
 ┃ ┗ 📜HEAD
 ┣ 📂bertopic_model
 ┃ ┣ 📜config.json
 ┃ ┣ 📜ctfidf.safetensors
 ┃ ┣ 📜ctfidf_config.json
 ┃ ┣ 📜topics.json
 ┃ ┗ 📜topic_embeddings.safetensors
 ┣ 📂data
 ┃ ┣ 📂01-raw
 ┃ ┃ ┣ 📜date_revenue.xlsx
 ┃ ┃ ┗ 📜reviews.csv
 ┃ ┣ 📂02-processed
 ┃ ┃ ┣ 📜correlation_sentimentxfeedback__revenue_median_pct_change_trend.csv
 ┃ ┃ ┣ 📜date_revenue_topic_correlation_sentimentxfeedback__revenue_change_trend.csv
 ┃ ┃ ┣ 📜granger.xlsx
 ┃ ┃ ┣ 📜merged_reviews_revenue.csv
 ┃ ┃ ┣ 📜modeled_reviews.csv
 ┃ ┃ ┣ 📜reviews_sentiment.csv
 ┃ ┃ ┗ 📜topics_over_time.csv
 ┃ ┗ 📂03-fig
 ┃ ┃ ┣ 📜Gacha Feedback_1_lag.png
 ┃ ┃ ┣ 📜General Feedback_1_lag.png
 ┃ ┃ ┣ 📜intertopic_distance_map.html
 ┃ ┃ ┣ 📜Login Issues_2_lag.png
 ┃ ┃ ┣ 📜Power Creep_2_lag.png
 ┃ ┃ ┣ 📜StoryDialogue_3_lag.png
 ┃ ┃ ┣ 📜topics_over_time.html
 ┃ ┃ ┣ 📜topic_word_score.html
 ┃ ┃ ┗ 📜wordcloud_reviews.png
 ┣ 📂insights # Insights written here are removed and stored elsewhere
 ┣ 📂src
 ┃ ┣ 📜api_scrape_clean_sentiment.py
 ┃ ┣ 📜granger_causality_tests.py
 ┃ ┣ 📜granger_graph.py
 ┃ ┣ 📜merge_reviews_revenue.py
 ┃ ┣ 📜model.py
 ┃ ┗ 📜wordcloud_reviews.ipynb
 ┣ 📜.gitignore
 ┣ 📜README.md
 ┗ 📜requirements.txt
 ```
### Pre-included data
- All the data included is data I processed.
- data/01-raw
    - date_revenue.xlsx
        - Data taken from https://revenue.ennead.cc/games/star-rail and https://www.statista.com/statistics/1403891/honkai-star-rail-player-revenue-app/ 
        - Both of these websites use estimates, and are combined as I was unfortunately unable to get revenue since launch in one single site
        - Both of these websites give revenue estimates from IOS and Android players
    - reviews.csv
        - Scraped reviews using src/api_scrape_clean_sentiment.py
- data/02-processed
    - reviews_sentiment.csv
        - Processed and cleaned reviews.csv with sentiment analysis via src/api_scrape_clean_sentiment.py
    - modeled_reviews.csv
        - reviews_sentiment.csv with the topic info via src/model.py
    - topics_over_time.csv
        - A CSV created by BERTopic for the change in topics over time via src/model.py
    - merged_reviews_revenue.csv
        - A CSV created via a SQL statement to merge the topics, sentiment and revenue together via src/merge_reviews_revenue.py
    - granger.xlsx
        - An Excel file to contain the p-values and f-values from Granger Causality tests with time lag
    - date_revenue_topic_correlation_sentimentxfeedback__revenue_change_trend.csv
        - Un-aggregated percentage and absolute change
    - correlation_sentimentxfeedback__revenue_median_pct_change_trend.csv
        - Aggregated percentage and absolute change
- data/03-fig
    - These are all HTML files created by BERTopic using Plotly
    - intertopic_distance_map.html
        - Show how closely related topics are
    - topics_over_time.html
        - Show how topics evolved over time with the frequency of certain words
    - topic_word_score.html
        - Show the score of words within a topic for the BERTopic model
    - Gacha Feedback_1_lag.png
        - Gacha feedback sentiment multiplied by feedback count, with a lag of 1
    - General Feedback_1_lag.png
        - General feedback sentiment multiplied by feedback count, with a lag of 1
    - Login Issues_2_lag.png
        - Login issue sentiment multiplied by feedback count, with a lag of 2
    - Power Creep_2_lag.png
        - Power creep sentiment multiplied by feedback count, with a lag of 2
    - StoryDialogue_3_lag.png
        - Story/Dialogue sentiment multiplied by feedback count, with a lag of 3
### Python files
- The following three files will give you a user-level menu to select the operations you wish to operate. 
- src/api_scrape_clean_sentiment.py
    - This file will get reviews from Google Play Store and save to reviews.csv
    - You can then clean the file and analyze the sentiment
- src/model.py
    - A model has already been created in bertopic_model. However, if you wish to make a new model, this code has been attached for you to do so.
    - The file will allow you to model topics from reviews_sentiment.csv created in api_scrape_clean_sentiment.py
    - You can then merge topics if there are duplicate topics within the model by directly modifying the Python code
    - You can also set topic labels by directly modifying the Python code
    - The final part of the code will transform your data from reviews_sentiment.csv and save them into three figures as well as CSVs
- src/merge_reviews_revenue.py
    - This merges the revenue and reviews to be used in Power BI
- The following two files do not give you a user-level menu
- src/granger_causality_tests.py
    - Test time lag via Granger causality tests
- src/granger_graph.py
    - Graph and get data for analysis
- src/wordcloud_reviews.ipynb
    - Word cloud of topics
### Other
- READMD.md
    - The current file
- requirements.txt
    - Required libraries to install
- .gitignore
    - Files for GitHub to ignore uploading