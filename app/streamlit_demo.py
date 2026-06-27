from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]

EXAMPLES_PATHS = [
    ROOT / "outputs" / "postcorrection" / "byt5_arabic_turkic_512_2ep_examples.csv",
    ROOT / "docs" / "nlp_final_revision" / "samples" / "byt5_examples.csv",
]

MODEL_CANDIDATES = [
    ROOT / "models" / "byt5_arabic_turkic_512_2ep",
    ROOT / "outputs" / "postcorrection" / "byt5_arabic_turkic_512_2ep_model",
    ROOT / "checkpoints" / "byt5_arabic_turkic_512_2ep",
]


@st.cache_resource(show_spinner=False)
def load_model(model_dir: str):
    """Load a local HuggingFace seq2seq model if it exists.

    The course repository usually stores scripts and evaluation artifacts,
    while large model checkpoints may stay outside git. Therefore model loading
    is optional and the app can still run in demo/fallback mode.
    """
    if not model_dir:
        return None, None, "model_dir is empty"

    p = Path(model_dir)
    if not p.exists():
        return None, None, f"model_dir does not exist: {p}"

    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        import torch

        tokenizer = AutoTokenizer.from_pretrained(p)
        model = AutoModelForSeq2SeqLM.from_pretrained(p)
        model.eval()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        return tokenizer, model, f"loaded local model from {p} on {device}"
    except Exception as e:
        return None, None, f"could not load model from {p}: {e}"


def find_model_dir() -> Optional[Path]:
    env_path = os.environ.get("POSTCORRECTION_MODEL_DIR", "").strip()
    if env_path and Path(env_path).exists():
        return Path(env_path)

    for p in MODEL_CANDIDATES:
        if p.exists():
            return p

    return None


def simple_fallback(text: str) -> str:
    """Very conservative fallback.

    It does not pretend to be neural post-correction. It only normalizes
    repeated whitespace and keeps the text content unchanged.
    """
    return " ".join(text.split())


def predict_with_model(text: str, tokenizer, model, max_new_tokens: int = 256) -> str:
    import torch

    device = next(model.parameters()).device
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            num_beams=4,
            early_stopping=True,
        )

    return tokenizer.decode(out[0], skip_special_tokens=True)


@st.cache_data(show_spinner=False)
def load_examples() -> pd.DataFrame:
    for p in EXAMPLES_PATHS:
        if p.exists():
            df = pd.read_csv(p)
            cols = set(df.columns)
            if {"noisy", "clean"}.issubset(cols):
                return df
    return pd.DataFrame(columns=["noisy", "prediction", "clean"])


st.set_page_config(
    page_title="OCR post-correction demo",
    page_icon="📝",
    layout="wide",
)

st.title("Посткоррекция OCR для арабографичных тюркских текстов")
st.caption("Исследовательский демо-интерфейс к курсовой работе. Это не production OCR-система.")

with st.sidebar:
    st.header("Режим")
    model_dir = find_model_dir()
    manual_model_dir = st.text_input(
        "Путь к локальной модели",
        value=str(model_dir) if model_dir else "",
        help="Можно задать переменную POSTCORRECTION_MODEL_DIR или указать путь вручную.",
    )

    tokenizer, model, model_status = load_model(manual_model_dir)
    use_model = tokenizer is not None and model is not None

    if use_model:
        st.success(model_status)
    else:
        st.warning("Локальная модель не загружена. Демо работает в fallback-режиме.")
        st.caption(model_status)

    max_new_tokens = st.slider("max_new_tokens", 64, 512, 256, step=64)

examples = load_examples()

left, right = st.columns([1, 1])

with left:
    st.subheader("Входной OCR-текст")

    sample_idx = None
    if len(examples) > 0:
        sample_idx = st.selectbox(
            "Готовый пример",
            options=list(range(min(len(examples), 20))),
            format_func=lambda i: f"пример {i + 1}",
        )
        default_text = str(examples.iloc[sample_idx]["noisy"])
    else:
        default_text = ""

    text = st.text_area(
        "OCR/noisy text",
        value=default_text,
        height=260,
        label_visibility="collapsed",
    )

    run = st.button("Исправить", type="primary")

with right:
    st.subheader("Результат")

    if run:
        if not text.strip():
            st.info("Вставь OCR-текст слева.")
        elif use_model:
            prediction = predict_with_model(text, tokenizer, model, max_new_tokens=max_new_tokens)
            st.text_area("prediction", prediction, height=260, label_visibility="collapsed")
        else:
            saved_prediction = ""
            if sample_idx is not None and len(examples) > 0:
                saved_prediction = str(examples.iloc[sample_idx].get("prediction", "") or "").strip()

            if saved_prediction:
                prediction = saved_prediction
                st.text_area("saved prediction", prediction, height=260, label_visibility="collapsed")
                st.warning(
                    "Это demo-режим: локальная модель не загружена, поэтому показано сохранённое prediction из эксперимента для выбранного примера."
                )
            else:
                prediction = simple_fallback(text)
                st.text_area("fallback output", prediction, height=260, label_visibility="collapsed")
                st.warning(
                    "Это fallback-режим: нейросетевая модель не загружена, поэтому интерфейс показывает только безопасную нормализацию пробелов."
                )
    else:
        st.info("Нажми «Исправить», чтобы получить результат.")

if sample_idx is not None and len(examples) > 0:
    st.divider()
    st.subheader("Эталон и сохранённое предсказание из эксперимента")

    row = examples.iloc[sample_idx]
    c1, c2 = st.columns(2)

    with c1:
        st.caption("Эталонный clean text")
        st.text_area("clean", str(row.get("clean", "")), height=180, label_visibility="collapsed")

    with c2:
        st.caption("Сохранённое prediction из эксперимента")
        st.text_area(
            "saved prediction",
            str(row.get("prediction", "")),
            height=180,
            label_visibility="collapsed",
        )

st.divider()
st.markdown(
    """
**Ограничение.** Интерфейс демонстрирует исследовательскую постановку `OCR/noisy text → corrected text`.
Для реального архивного OCR модель требует адаптации на настоящих OCR/эталонных парах.
"""
)
