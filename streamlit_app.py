import streamlit as st
import pandas as pd
import pickle
import os
from pathlib import Path

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .genre-badge {
        display: inline-block;
        background-color: #e8f4f8;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        margin-right: 0.5rem;
        font-size: 0.85rem;
        color: #0066cc;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 Movie Recommendation Engine")
st.markdown("Discover movies similar to ones you love using content-based filtering")

# Sidebar for information
with st.sidebar:
    st.header("ℹ️ About This App")
    st.markdown("""
    This app uses **content-based filtering** to recommend movies based on genre and tag similarity.
    
    **How it works:**
    1. Movie genres and tags are vectorized using CountVectorizer
    2. Cosine similarity measures how similar movies are
    3. Top recommendations are ranked by similarity score
    
    **Dataset:** MovieLens dataset
    
    **Tech Stack:**
    - Scikit-learn for vectorization & similarity
    - Pandas for data handling
    - Streamlit for the interface
    """)
    
    st.divider()
    st.markdown("### 📊 Dataset Info")
    st.markdown("- Database: MovieLens")
    st.markdown("- Features: Genres & Tags")
    
    with st.expander("How recommendations work"):
        st.markdown("""
        This is a **content-based recommendation system**:
        
        1. **Vectorization**: Each movie's genres/tags are converted to a numerical vector
        2. **Similarity**: We calculate cosine similarity between all movie vectors
        3. **Ranking**: When you select a movie, we find the most similar ones
        
        **Why this approach?**
        - No cold-start problem (works for new movies)
        - Explainable (you see why movies are recommended)
        - Fast (pre-computed similarity matrix)
        
        **Limitations:**
        - Can't discover surprising recommendations
        - Won't know about quality differences
        - Misses collaborative signals
        """)

@st.cache_resource
def load_model_data():
    """Load pre-computed recommendation data"""
    # Try to load from pickle files (pre-computed from notebook)
    try:
        with open('data/movie_data.pkl', 'rb') as f:
            movies_df = pickle.load(f)
        with open('data/similarity_matrix.pkl', 'rb') as f:
            similarity_matrix = pickle.load(f)
        with open('data/vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        return movies_df, similarity_matrix, vectorizer
    except FileNotFoundError as e:
        st.error("⚠️ Model data files not found.")
        st.info("Expected files in the same data folder: `movie_data.pkl`, `similarity_matrix.pkl`, `vectorizer.pkl`")
        st.stop()

# Load data
with st.spinner("Loading recommendation model..."):
    movies_df, similarity_matrix, vectorizer = load_model_data()

st.success("✓ Model loaded successfully!")

# Get list of available movies, sorted by title
available_movies = sorted(movies_df['title'].tolist())

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Find Similar Movies")
    selected_movie = st.selectbox(
        "Select a movie you like:",
        available_movies,
        help="Choose a movie to get personalized recommendations"
    )

with col2:
    num_recommendations = st.slider(
        "Number of recommendations:",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )

# Get recommendations
if selected_movie:
    try:
        # Find index of selected movie
        movie_idx = movies_df[movies_df['title'] == selected_movie].index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(similarity_matrix[movie_idx]))
        
        # Sort by similarity (excluding the movie itself at index 0)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:num_recommendations+1]
        
        # Get movie indices and scores
        movie_indices = [i[0] for i in sim_scores]
        similarity_values = [i[1] for i in sim_scores]
        
        # Get recommended movies
        recommendations = movies_df.iloc[movie_indices].copy()
        recommendations['similarity_score'] = similarity_values
        
        # Display results
        st.divider()
        st.subheader(f"📺 Top {num_recommendations} Movies Similar to '{selected_movie}'")
        
        # Display as cards in a grid
        cols = st.columns(2)
        for idx, (_, row) in enumerate(recommendations.iterrows()):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"### {idx + 1}. {row['title']}")
                    
                    # Display similarity score as progress bar
                    similarity_pct = row['similarity_score'] * 100
                    st.metric(
                        "Genre Similarity",
                        f"{similarity_pct:.1f}%"
                    )
                    
                    # Display genres if available
                    if 'genres' in row and pd.notna(row['genres']):
                        genres_text = row['genres']
                        # If genres are pipe-separated (like "Action|Adventure|Sci-Fi")
                        if isinstance(genres_text, str):
                            genres_list = [g.strip() for g in genres_text.split('|')]
                            st.markdown("**Genres:** " + " ".join([f"`{g}`" for g in genres_list]))
                    
                    # Display movie ID for reference
                    if 'movieId' in row:
                        st.caption(f"MovieID: {row['movieId']}")
        
        # Show statistics
        st.divider()
        st.subheader("📊 Recommendation Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg. Similarity", f"{recommendations['similarity_score'].mean()*100:.1f}%")
        with col2:
            st.metric("Max Similarity", f"{recommendations['similarity_score'].max()*100:.1f}%")
        with col3:
            st.metric("Min Similarity", f"{recommendations['similarity_score'].min()*100:.1f}%")
        with col4:
            st.metric("Total Analyzed", f"{len(movies_df):,}")
        
        # Show similar movie selection for deeper exploration
        st.divider()
        st.subheader("🔍 Explore Further")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top recommended movie:**")
            top_movie = recommendations.iloc[0]
            st.write(f"**{top_movie['title']}** (Similarity: {top_movie['similarity_score']*100:.1f}%)")
        
        with col2:
            if st.button("🔄 Get recommendations for top match"):
                st.session_state['selected_movie'] = top_movie['title']
                st.rerun()
            
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        st.caption("Make sure the selected movie exists in the dataset")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 0.85rem; margin-top: 2rem;'>
    Built with Streamlit • Content-based filtering using cosine similarity
    </div>
    """, unsafe_allow_html=True)