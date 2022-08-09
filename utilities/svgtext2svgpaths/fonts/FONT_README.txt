Some units:
-----------

https://oreillymedia.github.io/Using_SVG/guide/units.html

px
    Pixel units, directly equivalent to SVG user units.

    For print, a px should be equal to 1/96th of an inch.
    For screens, a px should represent approximately the same distance in the user’s field of view (the same visual angle) as 1/96th of an inch at arm’s length.
    The px unit can be adjusted to represent an even number of actual screen pixels.

in
    Inches

    1in = 96px or user units
    1in = 2.54cm

    In modern software, inches and all other absolute units will be adjusted to match the px unit.

mm
    Millimeters

    1mm ≅ 3.7795px or user units

pt
    Points

    1pt ≅ 1.3333px or user units (1px = 0.75pt)
    1pt = 1/72in


Fonts stuff:
------------

https://iamvdo.me/en/blog/css-font-metrics-line-height-and-vertical-align


Inkscape example:
-----------------

doncument size in given in mm.

When writing text, the selected font size in the GUI is 30.0 pt 
(pt is indeed the unit, as saw in the tooltip of the GUI).

30.0 pt -> 40 px -> 10.5833 mm

we saw in the svg file font-size:10.5833px

and the char ('B', Arial) has an heigth of 7.5757 in the converted text to path svg data

Freetype example:
-----------------

pixel_size = point_size * resolution / 72
pixel_coord = grid_coord * pixel_size / EM_size

Arial, face.set_char_size(48*64)    3074

we see that the generated character ('B', Arial) has an height of 2240 "units" (which units?)


One Example:  ('B', Arial)

face = freetype.Face('Arial')
face.set_char_size(48 * 64)     # 3074
face.load_char('B', freetype.FT_LOAD_DEFAULT | freetype.FT_LOAD_NO_BITMAP)

we see that the size has an height (in grid units) of 2240

the properties of the face are

https://freetype-py.readthedocs.io/en/latest/size_metrics.html

ascender: 1854
descender: -434   independent of the chosen  set_char_size

height: 2355  ?? should it not be ascender - descender = 2288 ??

unit_per_EM = 2048  # the definition of the square whre the fonts are set-up

face.size : depending on the current character and the set_char_size values
  - ascender:  2816
  - descender: -704
  - height = 3520 = ascender - descender  OK
  - x_ppem: 48
  - y_ppem: 48
  - x_scale = 98304
  - y_scale = 98304  


if we set face.set_char_size = 2048  #  (32*64)
  - ascender:  1856
  - descender: -448
  - height = 2368 = ascender - descender  OK
  - x_ppem: 32   The width of the scaled EM square in pixels, hence the term ‘ppem’ (pixels per EM).
                 It is also referred to as ‘nominal height’.
  - y_ppem: 32   The height of the scaled EM square in pixels, hence the term ‘ppem’ (pixels per EM). 
                 It is also referred to as ‘nominal height’.

  - x_scale = 65536
  - y_scale = 65536





Example: is it the scaling solution ?
-------------------------------------

INKSCAPE: font-size = 30pt -> svg font-size = 10.5833px

FREETYPE: set_char_size = 2048 (as EM_size)

--> coeff = 2048 / 10.5833 = 193.51242

freetype decompose : B size = 1472.0
inkscape path :      B size = 7.5757

--> coeff = 1472.0 / 7.5757 = 194.30
            1466.0 / 7.5756 = 193.5137

Comclusion:
-----------
in Inkscape, give a text with a given size -> we know the svg font-size in px

To calculate the path, just generate the freetype path of the char, 
and then scale if with :

        coeff = inkscale_fontsize_px / freetype_char_size

But I would like to have the exact scaling !!!