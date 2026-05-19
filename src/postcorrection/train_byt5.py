"""
Fine-tune ByT5-small for OCR post-correction.

Example:
python src/train_byt5.py \
  --train data/processed/train.csv \
  --valid data/processed/valid.csv \
  --output_dir models/byt5-small-ocr \
  --epochs 3

For weak laptops, use fewer epochs and small batch size.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from datasets import Dataset


def load_dataset(path: Path) -> Dataset:
    df = pd.read_csv(path)
    df = df[["noisy", "clean"]].fillna("").astype(str)
    return Dataset.from_pandas(df, preserve_index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--valid", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--model_name", type=str, default="google/byt5-small")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--max_source_length", type=int, default=256)
    parser.add_argument("--max_target_length", type=int, default=256)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)

    train_ds = load_dataset(args.train)
    valid_ds = load_dataset(args.valid)

    def preprocess(batch):
        model_inputs = tokenizer(
            batch["noisy"],
            max_length=args.max_source_length,
            truncation=True,
        )
        labels = tokenizer(
            text_target=batch["clean"],
            max_length=args.max_target_length,
            truncation=True,
        )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    train_tok = train_ds.map(preprocess, batched=True, remove_columns=train_ds.column_names)
    valid_tok = valid_ds.map(preprocess, batched=True, remove_columns=valid_ds.column_names)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(args.output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        predict_with_generate=True,
        logging_steps=20,
        save_total_limit=2,
        fp16=False,
        report_to="none",
    )

    collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=valid_tok,
        processing_class=tokenizer,
        data_collator=collator,
    )

    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    print(f"Saved model to {args.output_dir}")


if __name__ == "__main__":
    main()
