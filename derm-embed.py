# derm_embed.py
from huggingface_hub import from_pretrained_keras
from PIL import Image
from io import BytesIO
import tensorflow as tf
import numpy as np
import os

# <<< set your local image path here >>>
IMAGE_PATH = r"C:\Users\GOLD mobile\Desktop\skin-check\test_gradient1.png"

# Load & bytes-encode the image as expected by the model
img = Image.open(IMAGE_PATH).convert("RGB")
buf = BytesIO()
img.save(buf, "PNG")
image_bytes = buf.getvalue()

# Wrap as TF Example (the model expects tf.train.Example with 'image/encoded')
example = tf.train.Example(
    features=tf.train.Features(
        feature={"image/encoded": tf.train.Feature(bytes_list=tf.train.BytesList(value=[image_bytes]))}
    )
).SerializeToString()

# Load the Keras SavedModel directly from the Hub
model = from_pretrained_keras("google/derm-foundation")  # gated repo; make sure you accepted terms
infer = model.signatures["serving_default"]

# Run inference to get the embedding
output = infer(inputs=tf.constant([example]))
embedding = output["embedding"].numpy().flatten()

print("Embedding shape:", embedding.shape)
print("First 10 values:", np.array2string(embedding[:10], precision=4))
