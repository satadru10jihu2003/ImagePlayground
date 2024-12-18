import base64
from openai import OpenAI
from PIL import Image
import os

def compress_image(input_image_path, output_image_path, quality=20):
    # Open an image file
    with Image.open(input_image_path) as img:
        # Compress the image
        img.save(output_image_path, "JPEG", quality=quality)

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "math.jpeg"
# Compress the image
compress_image(image_path, "compressed.jpeg")
client = OpenAI()
# Getting the base64 string
base64_image = encode_image("compressed.jpeg")

response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "This image is from a student's diary. Print the text in the image",
        },
        {
          "type": "image_url",
          "image_url": {
            "url":  f"data:image/jpeg;base64,{base64_image}"
          },
        },
      ],
    }
  ],
)
# delete the compressed image
os.remove("compressed.jpeg")

print(response.choices[0].message.content)