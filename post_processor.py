from PIL import Image, ImageFont, ImageDraw, ImageColor
import numpy as np

class TextType(Enum):
    SPEECHBUBBLE = auto()
    FREETEXT = auto()

def post(path_name, metadata, type=TextType.SPEECHBUBBLE, modified_name='modified.png'):
    img = Image.open(path_name).convert('RGBA')
    data = np.array(img)

    erase_text(data, metadata['bounding_box'], type, metadata['background_color'])
    replace_text(data, metadata['bounding_box'], metadata['orientation'], metadata['translated_text'])
            
    new_img = Image.fromarray(data)
    new_img.save(modified_name)
    return modified_name

def get_text_color(text_color, variance=5):
        low_text_col = np.copy(text_color)
        low_text_col[:3] -= variance
        low_text_col = np.clip(low_text_col, a_min=0, a_max=None)

        high_text_col = np.copy(text_color)
        high_text_col[:3] += variance
        high_text_col = np.clip(high_text_col, a_min=None, a_max=255)

        return (low_text_col, high_text_col)

def erase_text(data, bounding_box, type, text_color=[0,0,0,255], background_color=[255,255,255,255]):
        low_text_col, high_text_col = get_text_color(text_color)
        match type:
            case TextType.FREETEXT:
                #here do concave hull stuff
                print("TODO")
            case _:
                #since speechbubble, skip calculating wrap
                for x in range(bounding_box.lowX, bounding_box.highX):
                    for y in range(bounding_box.lowY, bounding_box.highY):
                        if(low_text_col < data[x,y] < high_text_col):
                            data[x, y] = background_color

def replace_text(data, translated_text, bounding_box, orientation="None", font_filepath="arial.ttf", font_color=[0,0,0,255]):
    draw = ImageDraw.Draw(data)
    
    position = (bounding_box.lowX, bounding_box.highY)

    font_size = 100
    size = None
    while (size is None or size[0] > bounding_box.height or size[1] > bounding_box.width and font_size > 0):
        font = ImageFont.truetype("Tests/fonts/FreeMono.ttf", font_size)
        size = draw.multiline_textbbox(position, translated_text, font)
        font_size -= 1

    draw.multiline_text(position, translated_text, fill=font_color[:3], font=font)


# this is for when doing non speech bubble text
# def calculate_k_means_cluster():
# def calculate_concave_hull():