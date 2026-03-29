import easyocr
from anthropic import Anthropic
from pydantic import BaseModel
from fastapi import FastAPI
import base64

class Output(BaseModel):
    translation: list[str]

class Input(BaseModel):
    image: str

system='You are an expert manhwa translator with world-class skill in translating Korean to English. You have strict attention to detail: you understand idiomatic Korean language patterns and can output equivalently idiomatic English translations in-context.'

input="""<input>
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
async def translate(input: Input) -> Output:
    img = base64.b64decode(input.image)

    ocr_result = reader.readtext(img, paragraph=True)
    bubbles = [row[1] for row in ocr_result]

    translation = client.messages.parse(
        max_tokens=1024,
        system=system,
        messages=[{'role': 'user', 'content': input.format(bubbles=bubbles)}],
        model='claude-sonnet-4-6',
        output_format=Output,
    )

    bounding_boxes = [row[0] for row in ocr_result]
    metadata = [it for it in zip(bounding_boxes, translation.parsed_output.translation)]
    # TODO: process the image here

    return translation.parsed_output
