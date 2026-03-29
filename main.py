
from post_processor import post
import numpy as np

metadata={}

metadata = [[[[114, 241], [292, 241], [292, 376], [114, 376]], "There's actually someone from the regular class stepping up alone?"],
 [[[445, 435], [595, 435], [595, 523], [445, 523]], 'Does he have a death wish?'],
 [[[186, 937], [394, 937], [394, 1072], [186, 1072]], "But doesn't that guy's equipment look kind of strange?"]]

post("manhwa.jpg",metadata)
