# 🎬 Flask Movie Recommender - Deployment Guide

Much simpler than Streamlit! This is a lightweight Flask app that deploys easily.

## Quick Start - Local Testing

### 1. Folder structure
```
movie-recommender-flask/
├── app.py
├── requirements_flask.txt
├── data/
│   ├── movie_data.pkl
│   ├── similarity_matrix.pkl
│   └── vectorizer.pkl
└── templates/
    └── index.html
```

### 2. Install & run locally
```bash
# Create folder
mkdir movie-recommender-flask
cd movie-recommender-flask

# Copy files:
# - app.py
# - requirements_flask.txt
# - templates/index.html
# - data/*.pkl (your pickle files)

# Create virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_flask.txt

# Run
python app.py
```

Visit: `http://localhost:5000`

---

## Deployment Option 1: Railway (Easiest - 5 minutes)

Railway is the simplest. You get a free tier and can deploy without credit card initially.

### Steps:
1. Go to https://railway.app/
2. Click "New Project" → "Deploy from GitHub"
3. Connect your GitHub account
4. Select your `movie-recommender` repo
5. Railway auto-detects it's Python
6. Set environment:
   - `FLASK_ENV=production`
   - Add `data/` folder with your pickle files
7. Click Deploy

Your app gets a URL like: `https://movie-recommender-xxxxx.up.railway.app`

**Note:** The pickle files need to be in the repo. Since they're large:
- Option A: Use `.gitignore` and upload via Railway's dashboard
- Option B: Commit them to GitHub (some services allow 500MB repos)

---

## Deployment Option 2: Render.com (5-10 minutes)

Similar to Railway, very simple.

### Steps:
1. Go to https://render.com/
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Set:
   - **Name:** movie-recommender
   - **Environment:** Python 3
   - **Build command:** `pip install -r requirements_flask.txt`
   - **Start command:** `gunicorn app:app`
5. Add environment variable: `FLASK_ENV=production`
6. Deploy

Your app gets a URL like: `https://movie-recommender-xxxxx.onrender.com`

---

## Deployment Option 3: Heroku (Works but paid now)

Heroku used to be free but now requires a credit card. Still simple though.

### Steps:
1. Install Heroku CLI: `brew install heroku` (or download for Windows)
2. Login: `heroku login`
3. Create app: `heroku create movie-recommender`
4. Push code: `git push heroku main`
5. Open: `heroku open`

---

## Deployment Option 4: Fly.io (Free tier available)

Good alternative, similar to Railway.

### Steps:
1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Login: `flyctl auth login`
3. Create app: `flyctl launch` (in your repo directory)
4. Deploy: `flyctl deploy`

---

## Recommended: Railway

**Why Railway?**
- Simplest setup
- Free tier is generous
- Auto-deploys from GitHub
- Good docs
- Supports large files

---

## Handling Large Pickle Files

If your `similarity_matrix.pkl` (724 MB) is too big for GitHub:

### Option A: Use Git LFS
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes
git commit -m "Add LFS"
git push
```

### Option B: Upload to Railway directly
1. After deploying to Railway
2. Go to your project settings
3. Add a "Volume" for persistent storage
4. Upload pickle files via Railway dashboard

### Option C: Compress the matrix
Use sparse matrix format in your Colab notebook:
```python
from scipy.sparse import csr_matrix
# Convert dense to sparse
sparse_sim = csr_matrix(cosine_sim)
# Save sparse version (much smaller)
import pickle
with open('similarity_matrix_sparse.pkl', 'wb') as f:
    pickle.dump(sparse_sim, f)
```

Then update `app.py` to load sparse matrix:
```python
similarity_matrix = pickle.load(f)  # Works with sparse too!
```

This reduces 724 MB → ~50-100 MB.

---

## File Structure for Deployment

```
movie-recommender/
├── app.py
├── requirements_flask.txt
├── templates/
│   └── index.html
├── data/
│   ├── movie_data.pkl
│   ├── similarity_matrix.pkl
│   └── vectorizer.pkl (optional)
├── .gitignore
├── .git/
└── README.md
```

### .gitignore (optional, if pkl files too large)
```
*.pkl
data/
venv/
__pycache__/
```

---

## Testing Before Deploy

```bash
# Install locally
pip install -r requirements_flask.txt

# Run
python app.py

# Visit http://localhost:5000
# Try selecting a movie and getting recommendations
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot find pickle files" | Make sure `data/` folder is in same directory as `app.py` |
| "Module not found" | Run `pip install -r requirements_flask.txt` |
| App crashes on load | Check that similarity matrix is correct shape/format |
| Slow load time | Normal on first request; similarity matrix is 724 MB |

---

## Blog Post Content

Now you have a working demo! You can:

1. **Embed the app in your blog** (if on same domain) or link to it
2. **Screenshot the interface** for the post
3. **Show the architecture:**
   - Flask backend with pickle-loaded model
   - Simple REST API
   - Clean HTML/JS frontend
   - No database needed

---

## Next Steps

1. Test locally: `python app.py`
2. Choose deployment: Railway recommended
3. Push to GitHub
4. Deploy in 5 minutes
5. Write your blog post with working demo!

---

Good luck! 🚀