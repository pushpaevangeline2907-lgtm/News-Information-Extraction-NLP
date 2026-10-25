
import re
from urllib.parse import quote

import feedparser
import nltk
import streamlit as st
import trafilatura

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


# NLTK Resource Setup
@st.cache_resource
def setup_nltk():
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]

    for resource_path, package in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package, quiet=True)


setup_nltk()


# Extract Article Text
def get_article_text(url):
    if not url:
        return ""

    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                favor_recall=True,
            )

            if text:
                return text.strip()

    except Exception:
        pass

    return ""


# Clean Text
def clean_text(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Generate NLP Summary
def generate_summary(text):
    text = clean_text(text)

    if not text:
        return "Summary not available."

    try:
        sentences = sent_tokenize(text)

        if not sentences:
            return "Summary not available."

        if len(sentences) <= 5:
            return "\n\n".join(sentences)

        stop_words = set(stopwords.words("english"))
        word_frequency = {}

        words = word_tokenize(text.lower())

        for word in words:
            if word.isalpha() and word not in stop_words:
                word_frequency[word] = (
                    word_frequency.get(word, 0) + 1
                )

        sentence_scores = {}

        for index, sentence in enumerate(sentences):
            sentence_words = word_tokenize(sentence.lower())

            score = sum(
                word_frequency.get(word, 0)
                for word in sentence_words
                if word.isalpha() and word not in stop_words
            )

            if sentence_words:
                score = score / len(sentence_words)

            sentence_scores[index] = score

        important_indices = sorted(
            sentence_scores,
            key=sentence_scores.get,
            reverse=True,
        )[:5]

        important_indices.sort()

        summary = [
            sentences[index] for index in important_indices
        ]

        return "\n\n".join(summary)

    except (LookupError, ValueError):
        return "Unable to generate summary."


# Search News
def search_news(topic, max_articles=5):
    search_url = (
        "https://news.google.com/rss/search?q="
        + quote(topic)
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    feed = feedparser.parse(search_url)

    if feed.bozo and not feed.entries:
        return []

    return feed.entries[:max_articles]


# Streamlit Page Configuration
st.set_page_config(
    page_title="News Article Information Extraction",
    page_icon="📰",
    layout="wide",
)

st.title("📰 Information Extraction from News Articles")

st.write(
    "Search for recent news articles and extract important "
    "information using Natural Language Processing."
)

st.divider()


# User Input
topic = st.text_input(
    "Enter a news topic",
    placeholder="Example: Virat Kohli",
)

max_articles = st.selectbox(
    "Number of articles",
    [3, 5, 8, 10],
    index=1,
)

if st.button("🔍 Search News", type="primary"):

    if not topic.strip():
        st.warning("Please enter a news topic.")

    else:
        with st.spinner("Searching for news articles..."):
            try:
                articles = search_news(
                    topic.strip(),
                    max_articles,
                )
            except Exception:
                articles = []

        if not articles:
            st.error(
                "No news articles found. Check your internet "
                "connection and try again."
            )

        else:
            st.success(
                f"Found {len(articles)} news articles."
            )

            download_results = []

            for index, article in enumerate(articles, start=1):

                title = clean_text(
                    article.get("title", "Title unavailable")
                )

                source_data = article.get("source", {})

                if hasattr(source_data, "get"):
                    source = source_data.get(
                        "title", "Unknown Source"
                    )
                else:
                    source = "Unknown Source"

                published = article.get(
                    "published", "Date not available"
                )

                article_link = article.get("link", "")

                st.divider()
                st.subheader(f"{index}. {title}")

                st.write(f"**Source:** {source}")
                st.write(f"**Date:** {published}")

                with st.spinner("Processing article..."):
                    article_text = get_article_text(article_link)

                st.markdown("#### 📝 NLP Summary")

                if article_text:
                    summary = generate_summary(article_text)
                    st.write(summary)

                    with st.expander("View Full Article Text"):
                        st.write(article_text)

                else:
                    description = clean_text(
                        article.get("summary", "")
                    )

                    if description:
                        st.write(description)
                        st.caption(
                            "Full article text unavailable. "
                            "Showing the available description."
                        )
                    else:
                        st.write("Summary not available.")

                if article_link.startswith(("https://", "http://")):
                    st.markdown(
                        f"[🔗 Read Original Article]({article_link})"
                    )

                download_results.append(
                    f"Article {index}\n"
                    f"Title: {title}\n"
                    f"Source: {source}\n"
                    f"Date: {published}\n"
                    f"Summary: "
                    f"{summary if article_text else description if description else 'Not available'}\n"
                    f"Link: {article_link}\n"
                )

            st.divider()

            st.download_button(
                label="⬇️ Download Search Results",
                data="\n\n".join(download_results),
                file_name="news_search_results.txt",
                mime="text/plain",
            )


# Footer
st.caption(
    "News: Google News RSS | Extraction: Trafilatura | "
    "NLP: NLTK | Interface: Streamlit"
)
