import easyocr
from pprint import pprint

reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
result = reader.readtext('chinese.jpg')

pprint(result)
