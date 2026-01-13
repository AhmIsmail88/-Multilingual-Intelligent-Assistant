# -Multilingual-Intelligent-Assistant

A simple FastAPI app for multilingual content generation, summarization, translation, and Q&A using Hugging Face pipelines.

## Features
- Generates content about a topic (text-generation)
- Summarizes the generated content (summarization)
- Translates the summary to French (translation_en_to_fr)
- Answers questions based on the generated content (question-answering)

## Requirements
- Python 3.8+
- Dependencies in `requirements.txt`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API
```bash
python multilingual_intelligent_assistant.py
```

The API is available at `http://localhost:8000`.

## Example Request
```bash
curl -X POST http://localhost:8000/ai-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Artificial Intelligence in Education",
    "question": "How does AI improve personalized learning?"
  }'
```
