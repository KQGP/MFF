# MFF — AI Multimodal Fashion Finder

A **Streamlit app** that analyzes uploaded clothing photos with **Gemini**, searches fashion retailers via **Exa**, scrapes product pages with **Firecrawl**, grades matches, and converts prices to **Yemeni Rial (YR)** (rate 530 YR/USD).

## ✨ Features

- 📤 Multi-product image upload
- 🤖 Gemini vision → search query generation
- 🔎 Exa search on target domains (Shein, Namshi, Boutiqaat, Styli, Ounass)
- 🕷️ Firecrawl page scraping
- 📊 Multi-factor grading (Identical / Very Similar / Low-Quality Replica)
- 💱 Price conversion to YR market price
- 🔑 API keys via sidebar

## 🧱 Tech Stack

- Python, Streamlit
- Google GenAI (Gemini 2.5 Flash)
- Exa (search)
- Firecrawl (scraping)

## 📁 Project Structure

```
app.py     # Streamlit application
run.bat    # Launch script (streamlit run app.py)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+

### Install
```bash
pip install streamlit google-genai exa-py firecrawl-py
```

### Run
```bash
streamlit run app.py
# or
run.bat
```

### Configure
Enter your Gemini, Exa, and Firecrawl API keys in the sidebar.

> ⚠️ The bundled code contains hardcoded API keys. Move them to environment variables / secrets before sharing.
