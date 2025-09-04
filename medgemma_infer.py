# medgemma_infer.py
import torch
from transformers import pipeline

# <<< set your local image path here >>>
IMAGE_PATH = r"C:\Users\GOLD mobile\Desktop\skin-check\lesion.jpg"

# Choose device/dtype
use_cuda = torch.cuda.is_available()
device = 0 if use_cuda else -1  # pipeline uses -1 for CPU
dtype = torch.bfloat16 if use_cuda else torch.float32

pipe = pipeline(
    task="image-text-to-text",
    model="google/medgemma-4b-it",   # instruction-tuned variant (recommended)
    torch_dtype=dtype,
    device=device
)

messages = [
    {"role": "system", "content": [{"type": "text", "text": "You are a careful dermatologist assistant."}]},
    {"role": "user", "content": [
        {"type": "text", "text": "Describe key features and provide non-diagnostic guidance."},
        {"type": "image", "image": IMAGE_PATH}
    ]}
]

out = pipe(text=messages, max_new_tokens=200)
print(out[0]["generated_text"][-1]["content"])
