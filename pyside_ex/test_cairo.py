import cairo

def text_extent(font, font_size, text, *args, **kwargs):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
    ctx = cairo.Context(surface)
    ctx.select_font_face(font, *args, **kwargs)
    ctx.set_font_size(font_size)
    return ctx.text_extents(text)

text='Example'
font="Sans"
font_size=55.0
font_args=[cairo.FONT_SLANT_NORMAL]
(x_bearing, y_bearing, text_width, text_height,
 x_advance, y_advance) = text_extent(font, font_size, text, *font_args)
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(text_width), int(text_height))
ctx = cairo.Context(surface)
ctx.select_font_face(font, *font_args)
ctx.set_font_size(font_size)
ctx.move_to(-x_bearing, -y_bearing)
ctx.text_path(text)
ctx.set_source_rgb(0.47, 0.47, 0.47)
ctx.fill_preserve()
ctx.set_source_rgb(1, 0, 0)
ctx.set_line_width(1.5)
ctx.stroke()

surface.write_to_png("/tmp/out.png")

