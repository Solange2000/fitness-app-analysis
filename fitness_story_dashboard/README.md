# Beyond the Download — Fitness Research Dashboard

A reproducible Streamlit storytelling dashboard based on the included 100-response Microsoft Forms workbook. No mock responses or cloud credentials.

## Quick start (Windows / VS Code)

1. Extract the ZIP and open the `fitness_story_dashboard` folder in VS Code.
2. Double-click `run_dashboard.bat` (or use the VS Code terminal).
3. Wait for dependencies to install. The browser opens at `http://localhost:8501`.

Manual alternative:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` then `.venv\Scripts\python.exe -m streamlit run app.py`.

macOS/Linux: `bash run_dashboard.sh`.

## Folder layout

- `app.py`: dashboard and narrative
- `analysis.py`: reusable statistical calculations
- `data/responses.xlsx`: original uploaded survey workbook
- `requirements.txt`: Python dependencies
- `run_dashboard.bat` / `.sh`: launch scripts

## Research safeguards

- Data are self-reported and cross-sectional; retrospective statements are not measured pre/post changes.
- All original records identify Strava; generalisation beyond this sample is not warranted.
- OLS treats a five-level ordinal return-frequency outcome as numeric for exploratory analysis. Robust SEs do not eliminate this limitation.
- Filtering recalculates all statistics and can lead to small-sample instability.
- Do not publish respondent-level data without appropriate research permissions.

## Statistical definitions

See the Data dictionary page in the dashboard. Spearman tests are two-sided. Regression uses OLS with HC3 heteroscedasticity-robust errors, predictors gamification/social support/pre-use orientation, and return frequency as outcome. Alpha uses complete cases and sample variances.
