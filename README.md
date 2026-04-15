# Mentorship cohort dashboard

Streamlit app for side-by-side **mentee vs mentor** survey metrics (Likert averages, meeting frequency, monthly curriculum ratings).

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Data: place your export as `data/sample_survey.csv`, set `MENTORSHIP_CSV` to its path, or use **Upload CSV** in the sidebar. The bundled `data/sample_survey.csv` is synthetic demo data only.

## Push to GitHub (first time)

This folder is already a **git** repository on `main` with an initial commit. You only need to create the remote on GitHub and push.

1. On [github.com/new](https://github.com/new), create a **new repository** (any name, e.g. `mentorship-dashboard`). Choose **Public**. Do **not** add a README, `.gitignore`, or license (the repo must stay empty).
2. In PowerShell, from this project folder, run **one** of the following (replace the URL with yours):

```powershell
.\scripts\push-to-github.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
```

Or manually:

```powershell
& "C:\Program Files\Git\bin\git.exe" remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
& "C:\Program Files\Git\bin\git.exe" push -u origin main
```

GitHub will ask you to sign in (browser or token). After a successful push, your code is on GitHub.

You can also use **GitHub Desktop** or **Cursor’s Source Control** → **Publish Branch** if you prefer a GUI.

## Deploy on Streamlit Community Cloud (hosted URL)

1. Complete **Push to GitHub** above.
2. Sign in at [share.streamlit.io](https://share.streamlit.io/) with your GitHub account and authorize Streamlit if prompted.
3. Click **Create app** → select **this repository** and branch **`main`**.
4. Set **Main file path** to **`streamlit_app.py`** → **Deploy**.
5. Your public app URL will look like `https://YOUR_APP_NAME.streamlit.app`. Use **Manage app** in the Cloud dashboard to restart or view logs.

This app does not require **Secrets** unless you add API keys later. Users can upload a CSV from the sidebar, or you can replace `data/sample_survey.csv` in the repo and redeploy.
