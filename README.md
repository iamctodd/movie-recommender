# 🎬 Movie Recommender Engine

A content-based movie recommendation system that discovers similar movies using genre and tag similarity. Built with Flask, scikit-learn, and TMDB API integration.

**[🚀 Live Demo](https://movie-reco.up.railway.app/)** | **[Blog Post](#)** | **[How It Works](#how-it-works)**

---

## Features

✨ **Core Features**
- 🎯 Content-based recommendations using cosine similarity
- 🖼️ Movie posters from TMDB API
- ⭐ TMDB ratings and metadata
- 🔗 Clickable cards linking to TMDB movie pages
- 🎨 Modern, responsive UI with dark theme
- 🔍 Autocomplete movie search

✅ **Technical Features**
- Fast similarity lookups with pre-computed matrices
- TMDB API integration for enriched data
- Serverless architecture (downloads data on startup)
- Production-ready Flask app
- Easy Railway/Netlify deployment

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (HTML/CSS/JavaScript)                       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              Flask REST API                             │
│  (/api/recommend, /api/movies)                          │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   MovieLens         Cosine Similarity   TMDB API
   Data (pkl)        Matrix (pkl)        Integration
```

### How Recommendations Work

1. **Data Preparation**
   - MovieLens dataset with ~10,000 movies
   - Genres combined into "combined" field
   - CountVectorizer converts genres → numerical vectors

2. **Similarity Calculation**
   - Cosine similarity computed between all movie pairs
   - Pre-computed and cached in `similarity_matrix.pkl`
   - O(1) lookup time for recommendations

3. **Ranking**
   - User selects a movie
   - System finds movies with highest similarity scores
   - Results enriched with TMDB poster/rating data
   - Displayed in responsive card grid

### Example

**User Input:** "Solo: A Star Wars Story"

**System Process:**
1. Find movie in database → index 1234
2. Get similarity scores from pre-computed matrix
3. Sort by similarity score (descending)
4. Return top 10 most similar movies
5. Fetch TMDB data (posters, ratings) for each
6. Display with clickable links to TMDB

**Output:** 10 cards with similar adventure/sci-fi movies

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML/CSS/JavaScript | Responsive UI, TMDB API calls |
| **Backend** | Flask 3.0 | REST API, movie recommendations |
| **ML** | scikit-learn | CountVectorizer, cosine similarity |
| **Data** | pandas, numpy | Data loading, matrix operations |
| **Enrichment** | TMDB API | Movie posters, ratings, metadata |
| **Deployment** | Railway | Production hosting |

---

## Installation & Setup

### Local Development

**Requirements:** Python 3.11+, pip

```bash
# Clone repository
git clone https://github.com/iamctodd/movie-recommender.git
cd movie-recommender

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python3 app.py
```

Visit `http://localhost:5000` in your browser.

**Note:** On first run, the app downloads pickle files (~725 MB) from GitHub releases. This takes 2-3 minutes.

### Deployment

#### Option 1: Railway (Recommended)

```bash
# Push to GitHub
git push origin main

# Deploy on Railway
# 1. Go to https://railway.app
# 2. Create new project → Import from GitHub
# 3. Select this repo
# 4. Railway auto-detects `requirements.txt` and deploys
# 5. Click "Generate Domain" for public URL
```

**Cost:** Free tier includes 125,000 function invocations/month

#### Option 2: Netlify (with Functions)

```bash
# Deploy using Netlify Functions (serverless Python)
netlify deploy --prod
```

See `NETLIFY_DEPLOYMENT.md` for detailed instructions.

---

## Project Structure

```
movie-recommender/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Frontend UI
├── data/                       # (Generated on first run)
│   ├── movie_data.pkl         # Movie titles, genres
│   ├── similarity_matrix.pkl   # Pre-computed cosine similarity
│   └── vectorizer.pkl         # CountVectorizer model
├── netlify/                    # Netlify Functions setup (optional)
│   ├── functions/
│   │   └── recommendations.py # Serverless endpoint
│   └── public/index.html      # Static frontend
├── README.md                   # This file
└── NETLIFY_DEPLOYMENT.md       # Netlify setup guide
```

---

## API Documentation

### GET `/api/movies`

Returns list of all available movies.

**Response:**
```json
{
  "movies": ["Star Wars: Episode IV - A New Hope (1977)", ...],
  "count": 9742
}
```

### POST `/api/recommend`

Get movie recommendations based on similarity.

**Request Body:**
```json
{
  "movie_title": "Solo: A Star Wars Story",
  "num_recommendations": 10
}
```

**Response:**
```json
{
  "success": true,
  "movie": "Solo: A Star Wars Story",
  "recommendations": [
    {
      "title": "Star Wars: Episode IV - A New Hope (1977)",
      "similarity": 0.667,
      "similarity_pct": 66.7,
      "genres": "Action|Adventure|Sci-Fi",
      "movieId": 11,
      "poster_url": "https://image.tmdb.org/t/p/w342/...",
      "overview": "Luke Skywalker joins...",
      "release_date": "1977-05-25",
      "rating": 8.2
    },
    ...
  ]
}
```

---

## Configuration

### TMDB API Key

The app uses a TMDB API key (embedded in `templates/index.html`) to fetch movie posters and ratings.

To use your own key:

1. Get free API key from https://www.themoviedb.org/settings/api
2. In `templates/index.html`, find:
   ```javascript
   const TMDB_API_KEY = "your_key_here";
   ```
3. Replace with your key

### Customization

**Change default recommendation count:**
```html
<!-- In templates/index.html -->
<input type="number" id="numRecommendations" min="1" max="20" value="5">
```
Change `value="5"` to your preferred default.

---

## How the Recommendation Algorithm Works

### Content-Based Filtering

This app uses **content-based filtering**, which recommends movies based on item similarity (not user behavior).

**Advantages:**
- ✅ No cold-start problem (works for new movies)
- ✅ Explainable (can show why movies are similar)
- ✅ Fast (pre-computed similarities)
- ✅ Doesn't need user data

**Limitations:**
- ❌ Can't discover unexpected recommendations
- ❌ Doesn't consider user preferences
- ❌ Quality/ratings not factored in
- ❌ Serendipity limited

### How Similarity is Calculated

1. **Feature Extraction:** Movie genres → vector of word frequencies
   ```
   Movie 1: [Action, Adventure, Sci-Fi]
   Vector:  [1, 1, 1, 0, 0, ...]
   ```

2. **Cosine Similarity:** Angle between genre vectors
   ```
   similarity = dot_product(v1, v2) / (||v1|| * ||v2||)
   Range: 0 (completely different) to 1 (identical)
   ```

3. **Ranking:** Sort movies by similarity score, return top N

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Movies in database | 9,742 |
| Similarity matrix size | 724 MB |
| Time to load data | ~30 seconds (first run) |
| Time to get recommendations | <100ms |
| Recommendation accuracy | Content-based (no ground truth) |

**Optimization notes:**
- Pre-computed similarity matrix enables O(1) lookups
- TMDB API calls cached in browser (5-minute TTL)
- Pickle files downloaded on startup (Railway cold start)

---

## Development & Contributing

### Running Tests

```bash
# No automated tests yet - contributions welcome!
python3 app.py  # Manual testing via browser
```

### Making Changes

1. Fork the repo
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes
4. Test locally: `python3 app.py`
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request

---

## Future Improvements

### Potential Enhancements

**🎯 Near-term (Easy)**
- [ ] Add release year filtering
- [ ] Show more movie metadata (director, cast)
- [ ] Add "Save favorites" feature
- [ ] Improve mobile responsiveness
- [ ] Add sharing button (copy URL)

**⚡ Medium-term (Moderate)**
- [ ] Implement collaborative filtering (user-based)
- [ ] Add user ratings/feedback loop
- [ ] Cache TMDB results in database
- [ ] Add pagination for large result sets
- [ ] Implement search by director/actor

**🚀 Long-term (Complex)**
- [ ] Hybrid recommendation system (content + collaborative)
- [ ] Machine learning model for quality prediction
- [ ] User profiles and personalized recommendations
- [ ] Real-time trending movies
- [ ] A/B testing framework for algorithms

**💾 Data & Infrastructure**
- [ ] Use sparse matrices for memory efficiency
- [ ] Add database (PostgreSQL) for user data
- [ ] Implement caching layer (Redis)
- [ ] Multi-region deployment
- [ ] Microservices architecture

---

## Data Sources

- **Movies & Genres:** [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/)
  - 25 million ratings from 162,000 users
  - ~63,000 movies with genre tags
  - Preprocessed to ~9,742 movies for this demo

- **Posters & Metadata:** [TMDB API](https://www.themoviedb.org/settings/api)
  - Real-time movie data
  - High-quality poster images
  - User ratings and reviews

---

## Troubleshooting

### "No such file or directory: 'data/movie_data.pkl'"

**Solution:** The app downloads pickle files on startup from GitHub releases. Make sure you have internet connection and the Railway logs show successful downloads.

### "TMDB API not returning results"

**Solution:** 
- Check TMDB API key in `templates/index.html`
- Verify API key is valid at https://www.themoviedb.org/settings/api
- Check browser console (F12) for API errors

### "Similarity matrix too large"

**Solution:** For production, consider:
- Using sparse matrix format (scipy.sparse)
- Storing matrix in database instead of pickle
- Breaking matrix into chunks
- Pre-filtering movies before loading

### App crashes on Railway

**Solution:** Check logs:
```bash
# In Railway dashboard
Service → Logs → View all logs
```

Most common issues:
- Missing pickle files (downloads should complete)
- Python version incompatibility
- Insufficient memory (similarity matrix is large)

---

## License

MIT License - feel free to use this project for learning, commercial, or any other purpose.

---

## Credits

**Created by:** [Your Name]

**Key Technologies:**
- [scikit-learn](https://scikit-learn.org/) - Machine learning
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [TMDB API](https://www.themoviedb.org/settings/api) - Movie data
- [MovieLens](https://grouplens.org/) - Dataset
- [Railway](https://railway.app/) - Deployment

---

## Questions?

- 📧 Open an issue on GitHub
- 💬 Check existing issues first
- 📝 See blog post for detailed explanation

**[Read the Blog Post](#)** for a complete walkthrough of how this was built!

---

**Last Updated:** December 2025
**Version:** 1.0.0
**Status:** ✅ Production Ready