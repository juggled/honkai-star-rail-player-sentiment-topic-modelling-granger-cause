# Import required libraries
import pandas as pd
import numpy as np
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.dimensionality import BaseDimensionalityReduction
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from umap import UMAP

# Function to model topics
def model_topic(file_path):
    # Let the user know the function started
    print(f"Starting modeling of {file_path}!")

    # Load data
    df = pd.read_csv(file_path)

    #
    # Bertopic model setup
    #
    # Select embedding model
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2" 

    # Intialize UMAP model to reduce dimensionality and select random_state for reproducibility 
    umap_model = UMAP(n_components=5, random_state=42)

    # Intialize km for clustering
    km = KMeans()

    # Intialize ctfidf model to reduce the weight of frequent words
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

    # Seed topics for semi-supervised learning
    seed_topic = [
        # Positive aspects
        ['fun', 'satisfying', 'smooth', 'fluid', 'strategic', 'balanced',
        'rewarding', 'engaging', 'polished', 'dynamic', 'hype', 'epic', 'clutch',
        'beautiful', 'awesome', 'love', 'perfect', 'best', 'favorite', 'amazing',
        'cute', 'husbando', 'waifu', 'design', 'animation', 'voice', 'generous', 'f2p',
        'value', 'reward', 'primos', 'jades', 'pulls', 'luck', 'pity', 'earned',
        'farmable', 'abundance', 'love'],
        # Negative
        # Gameplay
        ['grind', 'boring', 'repetitive', 'annoying', 'difficult', 'unbalanced',
        'powercreep', 'weak', 'useless', 'nerf', 'rng', 'artifact', 'relic'],
        # Dissapointment about game or kits
        ['ugly', 'bad', 'hate', 'worst', 'disappointing', 'clunky', 'bugged',
        'skip', 'copium', 'mid', 'niche', 'boring', 'kit'],
        # Payment
        ['expensive', 'costly', 'greedy', 'scam', 'stingy', 'drought',
        'farm', 'resin', 'trailblaze', 'refill', 'whale', 'p2w', 'rigged'],
        # Optimization
        ['lag', 'crash', 'bug', 'glitch', 'freeze', 'disconnect', 'unplayable',
        'optimize', 'optimization', 'stutter', 'fps', 'frame', 'drop', 'loading']
        ]

    # Intialize BERTopic Model
    topic_model= BERTopic(
        umap_model=umap_model,
        hdbscan_model=km,
        ctfidf_model=ctfidf_model,
        seed_topic_list=seed_topic,
        embedding_model=embedding_model
        )

    # Fit the model
    topics, probs = topic_model.fit_transform(df['content'])
    topic_info = topic_model.get_topic_info()

    # Print topic info for the user
    print(topic_info)

    # Ask user if they want to save the model, save if yes, if not don't save. User will need to rerun to make a model.
    response = input("Do you want to save the topic model? (y/n): ")
    if response == 'y':
        topic_model.save("bertopic_model", serialization="safetensors", save_ctfidf=True, save_embedding_model=embedding_model)
    else:
        print("Topic model not saved. Rerun the program to create a new model.")

    # Nothing to return
    return None

# Function to merge topics in the model
def merge_model(topic_model, df):
    # Let the user know the function started
    print("Starting to merge topics!")
    # Setup embedding model
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

    # Input your topics to merge
    # Cyrene was split into 2 topics, 6 and 7, so we merge them here
    topics_to_merge = [6, 7]

    # Merge topics
    topic_model.merge_topics(df['content'], topics_to_merge)

    # Save the merged model
    topic_model.save("bertopic_model", serialization="safetensors", save_ctfidf=True, save_embedding_model=embedding_model)

    # Let the user know it's saved
    print("Merged and saved to bertopic_model!")

    # Nothing to return
    return None

# Function to set topic labels
def set_model(topic_model, df):
    # Let the user know the function started
    print("Starting relabelling topics!")
    # Labels we want to set
    labels = {
        0: "Power Creep",
        1: "Optimization Feedback",
        2: "Gacha Feedback",
        3: "General Feedback",
        4: "Login Issues",
        5: "Story/Dialogue",
        6: "Cyrene Feedback"
    }

    # Set the topic labels
    topic_model.set_topic_labels(labels)

    # Save the model with new labels
    topic_model.save("bertopic_model", serialization="safetensors", save_ctfidf=True, save_embedding_model="sentence-transformers/all-MiniLM-L6-v2")
    
    # Grab the topic info, print for user, and let them know it's saved
    topic_info = topic_model.get_topic_info()
    print(topic_info)
    print("Set topic labels and saved to bertopic_model!")
    return None

# Function to model reviews and save results
def model_reviews(topic_model, df):
    # Let the user know the function started
    print("Starting to model dataframe!")
    # Grab topic info and print for the user
    topic_info = topic_model.get_topic_info()
    print(topic_info)
    
    # Transform the dataframe to assign them to topics
    topics, probs = topic_model.transform(df['content'])

    # Manually save topics to topics column
    df['topics'] = topics

    # Model over time, save to CSV and let the user know
    topics_over_time = topic_model.topics_over_time(
        df['content'], 
        df['Year_Month_Date'], 
        datetime_format="%Y-%m")
    topics_over_time.to_csv('data/02-processed/topics_over_time.csv', index=False)
    print("Saved topics over time to data/02-processed/topics_over_time.csv!")

    # Get document info
    info = topic_model.get_document_info(df['content'])

    # Concat into original dataframe, save to CSV and let the user know
    df = pd.concat([df, info], axis=1)
    df.to_csv('data/02-processed/modeled_reviews.csv', index=False)
    print("Saved to data/02-processed/modeled_reviews.csv!")

    #
    # Visualizations
    #
    # Figure 1 Visualization, Topics over Time
    fig1 = topic_model.visualize_topics_over_time(topics_over_time, title='<b>Topics over Time</b>', custom_labels = True, width=1920, height=930)
    fig1.write_html("data/03-fig/topics_over_time.html")
    print("Saved topics over time figure to data/03-fig/topics_over_time.html!")
    
    # Figure 2 Visualization, Topic Word Scores
    fig2 = topic_model.visualize_barchart(title='<b>Topics Word Scores</b>', custom_labels = True, autoscale=True, width=475, height=450)
    fig2.write_html("data/03-fig/topic_word_score.html")
    print("Saved topic word score figure to data/03-fig/topic_word_score.html!")

    # Figure 3 Visualization, Intertopic Distance Map
    fig3 = topic_model.visualize_topics(title='<b>Intertopic Distance Map</b>', custom_labels = True, width=1900, height=900)
    fig3.write_html("data/03-fig/intertopic_distance_map.html")
    print("Saved intertopic distance map figure to data/03-fig/intertopic_distance_map.html!")
    return None

# Function to load saved model
def load_model():
    # Let the user know the function started
    print("Loading saved BERTopic Model!")
    topic_model = BERTopic.load("bertopic_model", embedding_model="sentence-transformers/all-MiniLM-L6-v2")
    print("Loading complete!")
    return topic_model

# Intialize needed data
df = pd.read_csv('data/02-processed/reviews_sentiment.csv')
df['Year_Month_Date'] = pd.to_datetime(df['Year_Month_Date'], format='%Y-%m-%d')
topic_model = load_model()

# Main level user input
print("""Please note that one model is already made and saved in bertopic_model.
1) Model Topics
2) Merge Topics
3) Set Topic Labels
4) Model Reviews and Save Results
Please select which step you would like to run:\n> 
""", end = "")

# Grab user input
user = input()

# Run function based on input
match user:
    case '1':
        model_topic('data/02-processed/reviews_sentiment.csv')
    case '2':
        merge_model(topic_model, df)
    case '3':
        set_model(topic_model, df)
    case '4':
        model_reviews(topic_model, df)