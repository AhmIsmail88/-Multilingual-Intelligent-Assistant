"""Multilingual Intelligent Assistant using Hugging Face pipelines.

Exposes a FastAPI endpoint that:
- Generates content about a topic
- Summarizes the generated content
- Translates the summary to French
- Answers a question based on the generated content
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field
from transformers import pipeline

app = FastAPI(title="Multilingual Intelligent Assistant")


class AssistantRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Topic to generate content about")
    question: str = Field(..., min_length=3, description="Question to answer")


class AssistantResponse(BaseModel):
    topic: str
    generated_text: str
    summary: str
    translated_summary_fr: str
    question_answer: Dict[str, Any]


@lru_cache(maxsize=1)
def get_text_generator():
    return pipeline(
        task="text-generation",
        model="Qwen/Qwen2.5-3B-Instruct",
    )


@lru_cache(maxsize=1)
def get_summarizer():
    return pipeline(
        task="summarization",
        model="facebook/bart-large-cnn",
        tokenizer="facebook/bart-large-cnn",
    )


@lru_cache(maxsize=1)
def get_translator():
    return pipeline(
        task="translation_en_to_fr",
        model="Helsinki-NLP/opus-mt-tc-big-en-fr",
    )


@lru_cache(maxsize=1)
def get_qa():
    return pipeline(
        task="question-answering",
        model="deepset/roberta-base-squad2",
        tokenizer="deepset/roberta-base-squad2",
    )


def generate_content(topic: str) -> str:
    generator = get_text_generator()
    prompt = (
        "Write a concise, informative paragraph (150-200 words) about: "
        f"{topic}."
    )
    output = generator(
        prompt,
        max_new_tokens=250,
        do_sample=True,
        temperature=0.8,
        top_p=0.95,
    )
    return output[0]["generated_text"]


def summarize_content(text: str) -> str:
    summarizer = get_summarizer()
    output = summarizer(
        text,
        max_length=100,
        min_length=30,
        do_sample=False,
    )
    return output[0]["summary_text"]


def translate_summary(summary: str) -> str:
    translator = get_translator()
    output = translator(summary)
    return output[0]["translation_text"]


def answer_question(question: str, context: str) -> Dict[str, Any]:
    qa = get_qa()
    return qa(question=question, context=context)


@app.post("/ai-assistant", response_model=AssistantResponse)
async def ai_assistant(payload: AssistantRequest) -> AssistantResponse:
    generated_text = generate_content(payload.topic)
    summary = summarize_content(generated_text)
    translated_summary = translate_summary(summary)
    answer = answer_question(payload.question, generated_text)

    return AssistantResponse(
        topic=payload.topic,
        generated_text=generated_text,
        summary=summary,
        translated_summary_fr=translated_summary,
        question_answer={
            "question": payload.question,
            "answer": answer.get("answer"),
            "score": answer.get("score"),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
