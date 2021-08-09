# Created by kor_a at 05/08/2021
from PIL import Image
import sys

images = [Image.open(x) for x in ['elon1.jpg', 'elon2.jpg', 'elon3.jpg']]
widths, heights = zip(*(i.size for i in images))

total_width = sum(widths)
max_height = max(heights)

new_im = Image.new('RGB', (total_width, max_height))

x_offset = 0
for im in images:
  new_im.paste(im, (x_offset,0))
  x_offset += im.size[0]

new_im.save('elon_final.jpg')