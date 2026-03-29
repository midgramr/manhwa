import easyocr
from anthropic import Anthropic
from pydantic import BaseModel
from fastapi import FastAPI
from base64 import b64decode, b64encode
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

from post_processor import post

class LlmOutput(BaseModel):
    translation: list[str]

class TranslationInput(BaseModel):
    image: str

class TranslationOutput(BaseModel):
    image: str

model_path = hf_hub_download(
    repo_id="ogkalu/comic-speech-bubble-detector-yolov8m",
    filename="comic-speech-bubble-detector.pt"
)

model = YOLO(model_path)

system='You are an expert manhwa translator with world-class skill in translating Korean to English. You have strict attention to detail: you understand idiomatic Korean language patterns and can output equivalently idiomatic English translations in-context.'

prompt="""<input>
{bubbles}
</input>

<instructions>
Translate the provided Korean manhwa text. Each row in the input array represents a separate speech/narraton bubble in a manhwa panel.

Your should parse each bubble separately, translate them, and put your responses into the "translation" output array.

You must make context-aware translations of the speech bubbles, i.e., if a phrase is ambiguous in Korean, use the surrounding context from the other speech bubbles to inform your translation.
</instructions>
"""

app = FastAPI()
client = Anthropic()
reader = easyocr.Reader(['ko','en'], gpu=False)

@app.get('/')
async def root():
    return {'message': 'hello world'}

@app.post('/translate')
async def translate(input: TranslationInput) -> TranslationOutput:
    img = b64decode(input.image)
    original_img = Image.open(BytesIO(img)).convert("RGB")

    ocr_result = reader.readtext(
        img,
        text_threshold=0.9,
        x_ths=0.5,
        paragraph=True,
        canvas_size=10000,
        slope_ths=0.02
    )
    bubbles = [row[1] for row in ocr_result]

    translation = client.messages.parse(
        max_tokens=1024,
        system=system,
        messages=[{'role': 'user', 'content': prompt.format(bubbles=bubbles)}],
        model='claude-sonnet-4-6',
        output_format=LlmOutput,
    )

    speech_results = model.predict(original_img, imgsz=1024, conf=0.25)
    speech_result = speech_results[0]

    speech_boxes = []
    for box in speech_result.boxes:
        x1, y1, x2, y2 = map(float, box.xyxy[0])

        x1 = int(round(x1))
        y1 = int(round(y1))
        x2 = int(round(x2))
        y2 = int(round(y2))

        speech_boxes.append([
            [x1, y1],
            [x2, y1],
            [x2, y2],
            [x1, y2],
        ])

    bounding_boxes = [row[0] for row in ocr_result]
    metadata = [it for it in zip(bounding_boxes, translation.parsed_output.translation)]
    try:
        processed_img = post(img, metadata, speech_boxes)
    except Exception as e:
        print(e)
        save_img = original_img.copy()
        my_uuid = uuid.uuid4()
        save_img.save(f"{my_uuid}.jpg", format="JPEG")


    save_img = Image.frombytes(
        "RGB",
        original_img.size,
        processed_img
    )

    buffer = BytesIO()
    save_img.save(buffer, format="JPEG")
    encoded_image = b64encode(buffer.getvalue()).decode("utf-8")

    return TranslationOutput(image=encoded_image)
