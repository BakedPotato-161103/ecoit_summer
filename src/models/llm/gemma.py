from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import uvicorn
from typing import Optional

# Path to your downloaded model directory
MODEL_PATH = "google/gemma-3-4b-it"

# Request schema
class GenRequest(BaseModel):
    prompt: str
    max_new_tokens: Optional[int] = 128
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.95
    top_k: Optional[int] = 50

# Init FastAPI
app = FastAPI(title="Gemma-4B Transformers API")

# Load tokenizer + model
print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

device = 0 if torch.cuda.is_available() else -1
dtype = torch.float16

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    torch_dtype=dtype,
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)

@app.post("/generate")
def generate(req: GenRequest):
    out = pipe(
        req.prompt,
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        top_k=req.top_k,
        do_sample=True,
        return_full_text=False,
    )
    return {"generated_text": out[0]["generated_text"]}

@app.get("/health")
def health():
    return {"status": "ok", "device": "cuda" if device == 0 else "cpu"}

if __name__ == "__main__":
    uvicorn.run("gemma:app", host="127.0.0.1", port=8000, log_level="info")
