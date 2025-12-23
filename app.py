from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
import os
import requests
from functools import lru_cache
import sys

app = Flask(__name__)

# TMDB API Configuration
TMDB_API_KEY = "ba06236e32bcaff62fbbc545f8666f9d"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def ensure_data_files():
    """Download pickle files if they don't exist"""
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    files_needed = {
        'movie_data.pkl': 'https://github.com/iamctodd/movie-recommender/releases/download/v1.0.0/movie_data.pkl',
        'similarity_matrix.pkl': 'https://github.com/iamctodd/movie-recommender/releases/download/v1.0.0/similarity_matrix.pkl',
        'vectorizer.pkl': 'https://github.com/iamctodd/movie-recommender/releases/download/v1.0.0/vectorizer.pkl'
    }
    
    for filename, url in files_needed.items():
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⬇️  Downloading {filename}...")
            try:
                response = requests.get(url, timeout=300)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"✓ Downloaded {filename} ({file_size_mb:.1f} MB)")
            except Exception as e:
                print(f"✗ Failed to download {filename}: {e}")
                print(f"  Try uploading {filename} manually to a GitHub release")
                return False
        else:
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✓ Found {filename} ({file_size_mb:.1f} MB)")
    
    return True

# Load model data
def load_model_data():
    """Load pickle files"""
    with open('data/movie_data.pkl', 'rb') as f:
        movies_df = pickle.load(f)
    with open('data/similarity_matrix.pkl', 'rb') as f:
        similarity_matrix = pickle.load(f)
    
    return movies_df, similarity_matrix

# Ensure files exist on startup
print("Checking for data files...")
if not ensure_data_files():
    print("ERROR: Could not download required data files!")
    print("Please upload pickle files to GitHub releases or commit them manually")
    sys.exit(1)

# Cache the data on startup
try:
    movies_df, similarity_matrix = load_model_data()
    print(f"✓ Loaded {len(movies_df)} movies")
except FileNotFoundError as e:
    print(f"Error loading model data: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error loading model data: {e}")
    sys.exit(1)

@lru_cache(maxsize=500)
def get_tmdb_data(movie_title):
    """Fetch movie data from TMDB API"""
    try:
        # Clean the title: remove year in parentheses and clean up formatting
        # "Batman/Superman Movie, The (1998)" -> "Batman Superman Movie"
        import re
        clean_title = movie_title
        
        # Remove year in parentheses
        clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', clean_title)
        # Remove ", The" at the end
        clean_title = re.sub(r',\s*The\s*$', '', clean_title)
        # Replace slashes with spaces
        clean_title = clean_title.replace('/', ' ')
        # Remove commas
        clean_title = clean_title.replace(',', '')
        # Clean up extra spaces
        clean_title = ' '.join(clean_title.split())
        
        print(f"Searching TMDB for: '{clean_title}' (original: '{movie_title}')")
        
        # Search for movie
        search_url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": clean_title,
            "include_adult": False
        }
        
        response = requests.get(search_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            movie = data['results'][0]  # Get first result
            poster_path = movie.get('poster_path')
            print(f"✓ Found poster for '{movie_title}': {poster_path}")
            return {
                'poster_path': poster_path,
                'backdrop_path': movie.get('backdrop_path'),
                'overview': movie.get('overview'),
                'release_date': movie.get('release_date'),
                'vote_average': movie.get('vote_average'),
                'popularity': movie.get('popularity')
            }
        else:
            print(f"⚠ No TMDB results for '{clean_title}' ({movie_title})")
    except requests.exceptions.RequestException as e:
        print(f"✗ TMDB API error for '{movie_title}': {e}")
    except Exception as e:
        print(f"✗ Unexpected error for '{movie_title}': {e}")
    
    return None

def get_movie_poster_url(movie_title, poster_path=None):
    """Get poster URL for a movie"""
    if poster_path:
        return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    
    # Try to fetch from TMDB
    tmdb_data = get_tmdb_data(movie_title)
    if tmdb_data and tmdb_data.get('poster_path'):
        return f"{TMDB_IMAGE_BASE_URL}{tmdb_data['poster_path']}"
    
    # Return placeholder
    return f"https://via.placeholder.com/342x513/1e3c72/ffffff?text={movie_title.replace(' ', '+')}"

def get_movie_details(movie_title):
    """Get enriched movie details from TMDB"""
    tmdb_data = get_tmdb_data(movie_title)
    if tmdb_data:
        poster_url = None
        if tmdb_data.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w342{tmdb_data['poster_path']}"
            print(f"Poster URL: {poster_url}")
        
        return {
            'poster_url': poster_url,
            'overview': tmdb_data.get('overview'),
            'release_date': tmdb_data.get('release_date'),
            'rating': tmdb_data.get('vote_average'),
            'popularity': tmdb_data.get('popularity')
        }
    return {}

@app.route('/')
def index():
    """Home page"""
    if movies_df is None:
        return "Error: Model data not found", 500
    
    movie_list = sorted(movies_df['title'].tolist())
    return render_template('index.html', movies=movie_list)

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """API endpoint to get recommendations"""
    if movies_df is None or similarity_matrix is None:
        return jsonify({'error': 'Model data not loaded'}), 500
    
    data = request.json
    movie_title = data.get('movie_title')
    num_recommendations = int(data.get('num_recommendations', 10))
    
    try:
        # Find movie index
        movie_idx = movies_df[movies_df['title'] == movie_title].index[0]
        
        # Get similarity scores
        sim_scores = list(enumerate(similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:num_recommendations+1]
        
        # Get movie indices and scores
        movie_indices = [i[0] for i in sim_scores]
        similarity_values = [i[1] for i in sim_scores]
        
        # Build response with TMDB data
        recommendations = []
        for idx, sim_score in zip(movie_indices, similarity_values):
            movie_data = movies_df.iloc[idx]
            movie_title_rec = movie_data['title']
            
            # Get TMDB details
            tmdb_details = get_movie_details(movie_title_rec)
            
            recommendations.append({
                'title': movie_title_rec,
                'similarity': float(sim_score),
                'similarity_pct': round(float(sim_score) * 100, 1),
                'genres': movie_data.get('genres', ''),
                'movieId': int(movie_data['movieId']),
                'poster_url': tmdb_details.get('poster_url'),
                'overview': tmdb_details.get('overview'),
                'release_date': tmdb_details.get('release_date'),
                'rating': tmdb_details.get('rating')
            })
        
        return jsonify({
            'success': True,
            'movie': movie_title,
            'recommendations': recommendations
        })
    
    except IndexError:
        return jsonify({'error': f'Movie "{movie_title}" not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """API endpoint to get all movies"""
    if movies_df is None:
        return jsonify({'error': 'Model data not loaded'}), 500
    
    movies = sorted(movies_df['title'].tolist())
    return jsonify({'movies': movies, 'count': len(movies)})

if __name__ == '__main__':
    app.run(debug=True)