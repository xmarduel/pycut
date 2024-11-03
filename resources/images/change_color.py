from PIL import Image

import math


picture = Image.open("media-record-red.png")

# Get the size of the image
width, height = picture.size

# -------------------------------------------------------------------------
picture = Image.open("media-record-red.png")
# Process every pixel
for x in range(width):
   for y in range(height):
       current_color = picture.getpixel( (x,y) )
       ####################################################################
       # Do your logic here and create a new (R,G,B) tuple called new_color
       r = math.floor(current_color[0] * 0.5)
       g = math.floor(current_color[1] * 0.5)
       b = math.floor(current_color[2] * 0.5)
       
       new_color = (r, g, b, current_color[3])
       ####################################################################
       picture.putpixel( (x,y), new_color)
       
picture.save("media-record-red-dark.png")

# -------------------------------------------------------------------------
picture = Image.open("media-record-red.png")
# Process every pixel
for x in range(width):
   for y in range(height):
       current_color = picture.getpixel( (x,y) )
       ####################################################################
       # Do your logic here and create a new (R,G,B) tuple called new_color
       r = current_color[1]
       g = current_color[0]
       b = current_color[2]
       
       new_color = (r, g, b, current_color[3])
       ####################################################################
       picture.putpixel( (x,y), new_color)
       
picture.save("media-record-green.png")

# -------------------------------------------------------------------------
picture = Image.open("media-record-red.png")
# Process every pixel
for x in range(width):
   for y in range(height):
       current_color = picture.getpixel( (x,y) )
       ####################################################################
       # Do your logic here and create a new (R,G,B) tuple called new_color
       r = math.floor(current_color[1] * 0.5)
       g = math.floor(current_color[0] * 0.5)
       b = math.floor(current_color[2] * 0.5)
       
       new_color = (r, g, b, current_color[3])
       ####################################################################
       picture.putpixel( (x,y), new_color)
       
picture.save("media-record-green-dark.png")

# -------------------------------------------------------------------------
picture = Image.open("media-record-red.png")
# Process every pixel
for x in range(width):
   for y in range(height):
       current_color = picture.getpixel( (x,y) )
       ####################################################################
       # Do your logic here and create a new (R,G,B) tuple called new_color
       r = current_color[2]
       g = current_color[1]
       b = current_color[0]
       
       new_color = (r, g, b, current_color[3])
       ####################################################################
       picture.putpixel( (x,y), new_color)
       
picture.save("media-record-blue.png")

# -------------------------------------------------------------------------
picture = Image.open("media-record-red.png")
# Process every pixel
for x in range(width):
   for y in range(height):
       current_color = picture.getpixel( (x,y) )
       ####################################################################
       # Do your logic here and create a new (R,G,B) tuple called new_color
       r = math.floor(current_color[2] * 0.5)
       g = math.floor(current_color[1] * 0.5)
       b = math.floor(current_color[0] * 0.5)
       
       new_color = (r, g, b, current_color[3])
       ####################################################################
       picture.putpixel( (x,y), new_color)
       
picture.save("media-record-blue-dark.png")