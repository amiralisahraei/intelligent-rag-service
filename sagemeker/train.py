from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer
)
from huggingface_hub import login
import torch
import os


login("you-HF-token")  # Replace with your Hugging Face token

# Load dataset directly from Hugging Face Hub
print("Loading dataset from Hugging Face Hub...")
finetuning_dataset = load_dataset("AmiraliSH/my-qa-dataset")
train_dataset = finetuning_dataset["train"]

# Load tokenizer and model
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def tokenize_function(examples):
    text = [q + a for q, a in zip(examples["question"], examples["answer"])]
    tokenizer.truncation_side = "left"
    return tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=1024
    )

tokenized_train_dataset = train_dataset.map(
    tokenize_function,
    batched=True,
    batch_size=32,
    remove_columns=train_dataset.column_names,
)

tokenized_train_dataset = tokenized_train_dataset.add_column(
    "labels", tokenized_train_dataset["input_ids"]
)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# SageMaker expects models to be saved to /opt/ml/model
output_dir = "/opt/ml/model" if "SM_MODEL_DIR" in os.environ else "./model"

training_args = TrainingArguments(
    learning_rate=1e-5,
    num_train_epochs=4,
    per_device_train_batch_size=1,
    output_dir=output_dir,
    overwrite_output_dir=True,
    save_steps=200,
    logging_strategy="epoch",
    optim="adamw_torch",
    gradient_accumulation_steps=4,
    gradient_checkpointing=False,
    save_total_limit=1,
    fp16=torch.cuda.is_available(),
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    data_collator=data_collator,
)

print("Starting training...")
trainer.train()

print("Saving model and tokenizer...")
# Save both model AND tokenizer
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)  # This line was missing!
print("Training completed!")