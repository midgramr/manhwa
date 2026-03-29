from PIL import Image, ImageFont, ImageDraw, ImageColor
import numpy as np
from enum import Enum
import base64
from io import BytesIO

class TextType(Enum):
    SPEECHBUBBLE = 1
    FREETEXT = 2

class BoundingBox:
    def __init__(self, lowX, highX, lowY, highY):
        self.lowX = lowX
        self.highX = highX
        self.lowY = lowY
        self.highY = highY
        self.width = highX - lowX
        self.height = highY - lowY

def generate_bounds(points):
    points = np.array(points)
    if points.shape != (4, 2):
        raise ValueError("Input must be a (4, 2) array of points")

    x_coords = points[:, 0]
    y_coords = points[:, 1]

    lowX = np.min(x_coords)
    highX = np.max(x_coords)
    lowY = np.min(y_coords)
    highY = np.max(y_coords)

    return BoundingBox(lowX, highX, lowY, highY)

def post(img_bytes: bytes, metadata, type=TextType.SPEECHBUBBLE):
    image_stream = BytesIO(img_bytes)

    # open image in pillow
    #img = Image.open().convert("RGB")
    img = Image.open(image_stream).convert("RGB")

    for idx in range(0, len(metadata)):
        bounding_box = generate_bounds(metadata[idx][0])
        text = metadata[idx][1]

        data = np.array(img)
        erase_text(data, bounding_box, type)
        img = Image.fromarray(data) # convert back to img for drawing new text
        replace_text(img, text, bounding_box)

    return img.tobytes()

def get_text_color(text_color, variance=50):
        low_text_col = np.copy(text_color)
        low_text_col[:3] -= variance
        low_text_col = np.clip(low_text_col, a_min=0, a_max=None)

        high_text_col = np.copy(text_color)
        high_text_col[:3] += variance
        high_text_col = np.clip(high_text_col, a_min=None, a_max=255)

        return (low_text_col, high_text_col)

def erase_text(data, bounding_box, type, text_color=[0,0,0], background_color=[255,255,255]):
        low_text_col, high_text_col = get_text_color(text_color)

        match type:
            case TextType.FREETEXT:
                #here do concave hull stuff
                print("TODO")
            case _:
                #since speechbubble, skip calculating wrap and colors
                for x in range(bounding_box.lowX, bounding_box.highX):
                    for y in range(bounding_box.lowY, bounding_box.highY):
                        data[y, x] = background_color

def replace_text(img, translated_text, bounding_box, orientation="None", font_filepath="fonts/ShadowsIntoLight-Regular.ttf", font_color=[0,0,0]):
    draw = ImageDraw.Draw(img)

    position = (bounding_box.lowX, bounding_box.lowY)
    max_font_size = 40
    min_font_size = 10
    spacing = 4

    font_size = max_font_size
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_filepath, font_size)
        words = translated_text.split()
        lines = []
        current_line = ""
        w = 0
        h = 0
        total_height = 0

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            ps = draw.textbbox(position, test_line, font=font)
            w =  ps[2]-ps[0]
            h = ps[3]-ps[1]
            if w <= bounding_box.width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    total_height += h + spacing
                current_line = word
        if current_line:
            lines.append(current_line)
            total_height += h

        # check if total height fits
        if total_height <= bounding_box.height:
            break
        font_size -= 2

    # center text vertically
    text_y = max(bounding_box.lowY, bounding_box.lowY + (bounding_box.height - total_height) // 2) - font_size // 5 - 5 # vertical center

    for line in lines:
        ps = draw.textbbox(position, line, font=font)
        w =  ps[2]-ps[0]
        text_x = max(bounding_box.lowX, bounding_box.lowX + (bounding_box.width - w) // 2)  # horizontal center
        draw.text((text_x, text_y), line, font=font, fill=tuple(font_color[:3]))
        text_y += h + spacing


# this is for when doing non speech bubble text
# def calculate_k_means_cluster():
# def calculate_concave_hull():
