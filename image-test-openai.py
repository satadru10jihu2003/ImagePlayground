from fastapi import FastAPI, File, UploadFile
import base64
from openai import OpenAI
from PIL import Image
import os
import shutil
import uvicorn

app = FastAPI()

def compress_image(input_image_path, output_image_path, quality=20):
    # Open an image file
    with Image.open(input_image_path) as img:
        # Compress the image
        img.save(output_image_path, "JPEG", quality=quality)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    input_image_path = file.filename
    output_image_path = "compressed.jpeg"
    
    with open(input_image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    compress_image(input_image_path, output_image_path)
    client = OpenAI()
    base64_image = encode_image(output_image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            },
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "This image is from a student's diary. Read the text in the image. Then Please review the text in prompt for any grammar or spelling errors. \
                                If you find any errors, please provide a list with the following information for each error: \
                                Type of error: (e.g., Spelling, Grammar, Punctuation) \
                                Incorrect word/phrase: (The original word/phrase) \
                                Correct word/phrase: (The suggested correction) \
                                Explanation: (A brief explanation of the error and why the correction is better) \
                                Lastly please provide a corrected version of the text."
                    }
                ]
            }
        ],
    )
    
    os.remove(output_image_path)
    os.remove(input_image_path)
    
    return {"result": response.choices[0].message.content}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)