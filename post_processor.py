from PIL import Image
import numpy as np

class TextType(Enum):
    SPEECHBUBBLE = auto()
    FREETEXT = auto()

def post(path_name, metadata, type=TextType.SPEECHBUBBLE, modified_name='modified.png'):
    img = Image.open(path_name).convert('RGBA')
    data = np.array(img)
    # Set top-left pixel to red (R, G, B, A)
    # data[0, 0] = [255, 0, 0, 255]

    match type:
        case TextType.FREETEXT:
            print("hehe")
        case _:
            print("hehe")
            #this is Speech-bubble text, so can skip cutting ops
            erase_text(data, metadata['bounding_box'], metadata['background_color'])
            replace_text(data, metadata['bounding_box'], metadata['orientation'], metadata['translated_text'])
            
    new_img = Image.fromarray(data)
    new_img.save(modified_name)
    return modified_name

def erase_text(data, bounding_box, text_color=[0,0,0,255], background_color=[255,255,255,255]):
    low_text_col = np.copy(text_color)
    low_text_col[:3] -= 5
    low_text_col = np.clip(low_text_col, a_min=0, a_max=None)
    high_text_col = np.copy(text_color)
    high_text_col[:3] += 5
    high_text_col = np.clip(high_text_col, a_min=None, a_max=255)
    
    for x in range(bounding_box.lowX, bounding_box.highX):
        for y in range(bounding_box.lowY, bounding_box.highY):
            if(low_text_col < data[x,y] < high_text_col):
                data[x, y] = background_color

def replace_text(data, bounding_box, orientation, translated_text):
    print("hehe")


# this is for when doing non speech bubble text
# def calculate_concave_hull():
# def calculate_k_means_cluster():