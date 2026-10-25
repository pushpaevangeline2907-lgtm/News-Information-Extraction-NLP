# Information Extraction from News Articles

A Streamlit app that searches Google News (RSS) for a topic, downloads the
top 4 articles, extracts the main text with Trafilatura, and produces a
5-sentence extractive summary using NLTK (word-frequency sentence scoring).
If an article cannot be downloaded, the RSS description is shown instead.

## Project structure

```
news_extraction_app/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/config.toml
└── README.md
```

## Requirements

- Python 3.9 or newer
- Internet connection (news feed, article pages, first-run NLTK data download)

## Installation

```bash
cd news_extraction_app
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open http://localhost:8501 if it does not open automatically.

## Usage

1. Enter a topic (e.g. `Virat Kohli`).
2. Click **Search News**.
3. Read the source, date, NLP summary, and link for each article.

## Notes

- NLTK data (`punkt`, `punkt_tab`, `stopwords`) downloads automatically on first run.
- No API keys are needed; `.env.example` is included only as a placeholder.
- Some publishers block automated downloads or Google News redirect links may
  not resolve; the app then falls back to the RSS description.

## Credits

News data: Google News RSS | Extraction: Trafilatura | NLP: NLTK | UI: Streamlit
