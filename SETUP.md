# 🎬 Movie Recommender - Streamlit Deployment Guide (MovieLens Edition)

## Quick Overview

This guide walks you through deploying your MovieLens-based movie recommendation engine as an interactive Streamlit app using genre/tag similarity.

---

## Step 1: Generate Model Files from Your Colab Notebook

In your Colab notebook, **copy and paste this entire cell** after you've computed your similarity matrix:

```python
"""
Run this after you've computed:
- mv (DataFrame with combined features for vectorization)
- count_vectorizer (your fitted CountVectorizer)
- cosine_sim (your computed cosine similarity matrix)
- movies (your movies.csv data with movieId, title, genres)
"""

import pickle
import pandas as pd
from google.colab import files

print("📦 Preparing data for Streamlit deployment...\n")

# Create clean dataframe for the app
app_df = movies[['movieId', 'title']].copy()

# Add genres if available (optional but useful for context)
if 'genres' in movies.columns:
    app_df['genres'] = movies['genres']
    print("✓ Including genres for context")

# Verify data
print(f"\n📊 Data Summary:")
print(f"   - Total movies: {len(app_df)}")
print(f"   - Columns: {list(app_df.columns)}")
print(f"   - Similarity matrix shape: {cosine_sim.shape}")

# Verify alignment
if len(app_df) != cosine_sim.shape[0]:
    print(f"\n⚠️  WARNING: Movie count ({len(app_df)}) doesn't match similarity matrix size ({cosine_sim.shape[0]})")
    print("Make sure you're using the same movies DataFrame used in vectorization!")
else:
    print(f"   ✓ Movies and similarity matrix aligned")

# Save to pickle files
print("\n💾 Saving pickle files...\n")

with open('movie_data.pkl', 'wb') as f:
    pickle.dump(app_df, f)
print("✓ Saved: movie_data.pkl")

with open('similarity_matrix.pkl', 'wb') as f:
    pickle.dump(cosine_sim, f)
print("✓ Saved: similarity_matrix.pkl")

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(count_vectorizer, f)
print("✓ Saved: vectorizer.pkl")

print("\n" + "="*50)
print("📥 DOWNLOADING FILES")
print("="*50 + "\n")

files.download('movie_data.pkl')
files.download('similarity_matrix.pkl')
files.download('vectorizer.pkl')

print("\n✅ SUCCESS! Your files are ready for Streamlit deployment.")
print("\nNext steps:")
print("1. Download the 3 pickle files above")
print("2. Put them in the same folder as streamlit_app.py")
print("3. Run: streamlit run streamlit_app.py")
```

**Important:** Make sure your variable names match:
- `movies` = your movies DataFrame with movieId, title, genres
- `count_vectorizer` = your fitted CountVectorizer
- `cosine_sim` = your computed cosine similarity matrix

If they're named differently, just update the variable names in the code above.

---

## Step 2: Local Testing

### A. Download the files from Colab
After running the cell above, Colab will prompt you to download 3 files.

### B. Set up your local environment
```bash
# Create a project directory
mkdir movie-recommender
cd movie-recommender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install streamlit pandas scikit-learn numpy
```

### C. Organize your files
Place these in your `movie-recommender` folder:
- `streamlit_app_v2.py` (renamed to `streamlit_app.py`)
- `movie_data.pkl` (from Colab download)
- `similarity_matrix.pkl` (from Colab download)
- `vectorizer.pkl` (from Colab download)

### D. Run locally
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## Step 3: Deploy to Streamlit Cloud (Free)

### A. Prepare for GitHub
Create a `requirements.txt` file:
```
streamlit==1.28.1
pandas==2.0.3
scikit-learn==1.3.1
numpy==1.24.3
```

### B. Push to GitHub
```bash
git init
git add streamlit_app.py requirements.txt movie_data.pkl similarity_matrix.pkl vectorizer.pkl
git commit -m "Initial commit: MovieLens recommender"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/movie-recommender.git
git push -u origin main
```

### C. Deploy via Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your GitHub repo
4. Select branch: `main`
5. Set main file path: `streamlit_app.py`
6. Click "Deploy"

Your app will be live at a URL like: `https://your-app-xxxxx.streamlit.app`

---

## Step 4: (Optional) Deploy to Hugging Face Spaces

### A. Create a Space
1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Streamlit" as the SDK
4. Name it: `movie-recommender`

### B. Upload files
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/movie-recommender
cd movie-recommender

# Copy your files here
cp ~/movie-recommender/streamlit_app.py .
cp ~/movie-recommender/requirements.txt .
cp ~/movie-recommender/*.pkl .

git add .
git commit -m "Initial MovieLens recommender"
git push
```

Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/movie-recommender`

---

## What the App Does

✅ **Movie Selection** - Browse all movies in the MovieLens dataset
✅ **Similarity Scoring** - See how similar each recommendation is (0-100%)
✅ **Genre Display** - Shows genres for context
✅ **Adjustable Results** - Get 5-20 recommendations
✅ **Statistics** - Summary of average/min/max similarity
✅ **Responsive Design** - Works on desktop and mobile

---

## Troubleshooting

### "Model data files not found"
- Make sure these 3 files are in the same folder as `streamlit_app.py`:
  - `movie_data.pkl`
  - `similarity_matrix.pkl`
  - `vectorizer.pkl`

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Size mismatch error
- Verify that your similarity matrix shape matches your movie count
- Example: If you have 9,700 movies, similarity matrix should be (9700, 9700)
- In Colab, check: `print(cosine_sim.shape)` and `print(len(movies))`

### Large pickle files (~100+ MB)
- If your pickle files are very large, you may hit Streamlit Cloud limits
- Solution 1: Use a sparse matrix format (`scipy.sparse`)
- Solution 2: Deploy to Hugging Face Spaces instead (higher limits)

---

## Blog Post Ideas

Now that you have a working Streamlit app, here are angles for your PM blog series:

### Post 1: "From Jupyter to Production"
- Journey from Colab notebook to live web app
- No DevOps required
- Screenshots of the final product
- Time to deployment: ~30 minutes

### Post 2: "Content-Based Recommendation Systems for PMs"
- What are they and when to use them
- Trade-offs vs collaborative filtering
- Real-world examples
- How to measure success (diversity, freshness, accuracy)

### Post 3: "Building Recommendation Features: The Complete Guide"
- Data preparation
- Choosing similarity metrics
- Cold-start problems
- A/B testing recommendations
- Scaling considerations

### Post 4: "Deploying ML Models Without Data Science Team Help"
- Streamlit + pickle files approach
- Minimal infrastructure
- Cost ($0-5/month)
- Perfect for MVPs

---

## Quick Reference

| Task | Command |
|------|---------|
| Run locally | `streamlit run streamlit_app.py` |
| Install deps | `pip install -r requirements.txt` |
| Create requirements.txt | `pip freeze > requirements.txt` |
| Push to GitHub | `git push origin main` |
| View logs (Streamlit Cloud) | Check deployment settings |

---

## Next Steps

✅ Generate pickle files in Colab (Step 1)
✅ Test locally (Step 2)
✅ Push to GitHub (Step 3A-3B)
✅ Deploy to Streamlit Cloud (Step 3C)
✅ Share the public URL
✅ Write your blog post!

---

Good luck! 🚀