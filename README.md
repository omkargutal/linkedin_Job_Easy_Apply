# LinkedIn AI Auto Job Applier 🤖

An automated LinkedIn Easy Apply bot (Python + Selenium) that searches for relevant jobs, answers application questions, customizes resumes using job details, and submits applications at scale.

Contents
- Quick start
- Install
- Configuration
- Running
- Contributing
- Features
- Documentation

Quick start
1. Configure your settings in the `/config` folder (see below).
2. Install dependencies.
3. Run the bot:
```bash
python runAiBot.py
```

Install
- Requires: Python 3.10+ and Google Chrome.
- Recommended virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or use the single-line install below
```
- Quick install (basic dependencies):
```bash
pip install undetected-chromedriver pyautogui setuptools openai flask-cors flask
```
- If `stealth_mode = True` in `config/settings.py`, a separate chromedriver may not be required. Otherwise download a matching Chrome for Testing binary: https://googlechromelabs.github.io/chrome-for-testing/

Configuration
- Edit `config/personals.py` — your personal details used for applications.
- Edit `config/questions.py` — preset answers and resume path (`default_resume_path`).
- Edit `config/search.py` — job search filters and preferences.
- Edit `config/secrets.py` — LinkedIn credentials and optional OpenAI API key (optional: if left blank, the bot will attempt to use an existing browser profile).
- Edit `config/settings.py` — behavior settings (timings, stealth mode, run in background, etc.).

Running
- Run the bot:
```bash
python runAiBot.py
```
- Optional UI for applied jobs history:
```bash
python app.py
# then open http://localhost:5000
```

Contributing
- Fork and submit pull requests to the `community-version` branch.
- Follow code guidelines in the repository for function naming, docstrings, and config validation.

Features
- Automated job search and applying (Easy Apply).
- Auto-fill and answer application questions from `config/questions.py`.
- Optional resume tailoring using OpenAI (if API key provided).
- Performance and smart selectors in `modules/` to improve reliability.

Documentation
- See [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) for full docs and optimizations.
- Quick start: [docs/OPTIMIZATION_START_HERE.md](docs/OPTIMIZATION_START_HERE.md)

Files of interest
- `runAiBot.py` — main runner
- `app.py` — applied jobs UI
- `config/` — user configuration files
- `modules/` — helper modules and optimizations

If you'd like a more detailed rewrite or to add a `requirements.txt`, I can add that next.
