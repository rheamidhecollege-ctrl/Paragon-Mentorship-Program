# Mentorship cohort dashboard

Streamlit app for side-by-side **mentee vs mentor** survey metrics (Likert averages, meeting frequency, monthly curriculum ratings).

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Data: place your export as `data/sample_survey.csv`, set `MENTORSHIP_CSV` to its path, or use **Upload CSV** in the sidebar. The bundled `data/sample_survey.csv` is synthetic demo data only.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (see below).
2. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/).
3. **New app** → pick this repo → branch `main` → Main file path **`streamlit_app.py`** → Deploy.
4. Optional: set a secret or use **Settings → Secrets** only if you add API keys later; this app does not require secrets for CSV upload.

## Push to GitHub

```bash
git init
git add .
git commit -m "Add mentorship Streamlit dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

Or use GitHub Desktop / the Cursor source control UI to publish the folder to a new repository.
