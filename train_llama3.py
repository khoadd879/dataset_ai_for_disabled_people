import os
import torch

# 1. Cài đặt thư viện tự động ngay trong code
print("Đang cài đặt Unsloth và các thư viện cần thiết...")
os.system('pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"')
os.system('pip install --no-deps xformers trl peft accelerate bitsandbytes datasets')

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# 2. Tải Llama 3 8B
print("Đang tải Llama 3...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit",
    max_seq_length = 2048,
    dtype = None,
    load_in_4bit = True,
)

# 3. Gắn mô-đun LoRA
print("Cấu hình LoRA...")
model = FastLanguageModel.get_peft_model(
    model, r=16, 
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16, lora_dropout=0, bias="none", use_gradient_checkpointing="unsloth"
)

# 4. Chuẩn bị dữ liệu (Dùng file Đa vật thể hóc búa nhất)
print("Chuẩn bị dữ liệu...")
tokenizer = get_chat_template(
    tokenizer, chat_template="llama-3",
    mapping={"role": "role", "content": "content", "user": "user", "assistant": "assistant"}
)

def formatting_func(examples):
    texts = [tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False) for convo in examples["messages"]]
    return {"text": texts}

# Đảm bảo tên file .jsonl khớp với tên file bạn đã tạo
dataset = load_dataset("json", data_files="llama3_dataset_multi_obj.jsonl", split="train")
dataset = dataset.map(formatting_func, batched=True)

# 5. Huấn luyện
print("BẮT ĐẦU HUẤN LUYỆN!")
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset, dataset_text_field="text",
    max_seq_length=2048, dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=2, gradient_accumulation_steps=4,
        warmup_steps=5, max_steps=60, # max_steps=60 để test, khi train thật tăng lên 200
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(), bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1, optim="adamw_8bit", seed=3407, output_dir="outputs"
    ),
)
trainer.train()

# 6. Lưu kết quả
model.save_pretrained("lora_model_dan_duong")
print("HOÀN TẤT! Mô hình đã được lưu tại thư mục 'lora_model_dan_duong'.")