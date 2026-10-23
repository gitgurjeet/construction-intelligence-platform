# Multimodal Construction Intelligence Platform

An AI-powered decision-support app for construction sites, built with Streamlit and Google Gemini (multimodal LLM).
Skill Wallet Capstone Project 1.

## Features

1. **Safety & PPE Audit**: upload a site photo; the AI checks helmet, vest, boots and harness, lists hazards with severity and fixes, and gives a safety score (0-100) as a downloadable JSON report.
2. **Crack Diagnostics**: upload a wall or concrete photo; the AI classifies the defect type, estimates crack width, severity, root causes, repairs and urgency.
3. **Planning & Valuation**: estimates total budget, spent amount, current asset value (in INR), and steel and cement requirements from structure type, area, location tier and completion %.
4. **Site Assistant**: weather-aware safety alerts (wind, rain, heat) plus a multi-turn construction engineering chatbot.

## Tech Stack

- Python 3.9+
- Streamlit (UI)
- Google Gemini API via `google-genai` (multimodal analysis)
- python-dotenv (API key handling)
- Strict JSON schemas for AI responses

## How to Run Locally

1. Clone the repo and open the folder.
2. Install dependencies:

3. Create a `.env` file in the project folder:

    (Get a free key at https://aistudio.google.com/apikey)
4. Start the app:



You can also paste an API key in the app sidebar instead of using `.env`.

## Sample Photos

`helmet.jpeg` and `wall.jpeg` are included for quick testing of the Safety and Crack tabs.

## Known Limitations

- Cost and valuation figures use approximate fixed rates, so they are estimates only.
- AI output depends on photo quality; unclear or non-construction images give low-confidence results.
- The free Gemini tier can be slow or return a temporary busy error; the app retries automatically.