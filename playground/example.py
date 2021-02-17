"""
Copyright © 2021
Vangeepuram Sreekesari

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from sys import argv
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# If you are developing an API
# just change the parameters
# in your convenient way!

global vc_size, profile_pic_size, overlay_location, watermark_location, uname_fntsz, other_fntsz

vc_size, profile_pic_size = (700, 400), (90, 90)
overlay_location = (vc_size[0] // 2 - profile_pic_size[0] // 2,
                    vc_size[1] // 2 - profile_pic_size[1] // 2)
uname_fntsz, other_fntsz = 20, 12

profile_pic_path = argv[1]
color = argv[2]

# --------------------------------------------------

username = "<username>"
user_handle = f"@{'<userhandle>'}"
user_location = "<user-location>"

# --------------------------------------------------

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    offset = 5
    return pil_img.crop(((img_width - crop_width) // 2 + offset,
                         (img_height - crop_height) // 2 + offset,
                         (img_width + crop_width) // 2 + offset,
                         (img_height + crop_height) // 2 + offset))

crop_max_square = lambda pil_img: crop_center(pil_img, min(pil_img.size), min(pil_img.size))

def mask_circle_transparent(pil_img, blur_radius, offset=0):
    "Returns a card after masking the profile pic"
    offset += blur_radius * 2
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill = 255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius)) # Filtering the mask
    result = pil_img.copy() # Buffer of same type to add alpha-gradient with mask
    result.putalpha(mask)
    return result

def render_text(image, text, text_location, font_size):
    "Returns a card by rendering the given text"
    card = ImageDraw.Draw(image)
    font_path = "../etc/General-Medium.ttf"

    if "|" not in text:
        card.text(text_location, text, font=ImageFont.truetype(font_path, font_size))
    else:
        card.text(text_location, text.split("|")[0], font=ImageFont.truetype(font_path, font_size))
        width, height = card.textsize(text.split("|")[0], font=ImageFont.truetype(font_path, font_size))
        n_spaces = width // len(text.split("|")[0]) + 2 # since word-size is diff. based on font-style

        card.text((text_location[0] + width + n_spaces, text_location[1] + height // 5),
        text.split("|")[1], font=ImageFont.truetype(font_path, other_fntsz))
    return image

def create_broder(image, y):
    "Returns a card by rendering border line to text"
    card = ImageDraw.Draw(image)
    x1, x2 = 0, vc_size[0] # To vary the length of the border-line
    y1 = y2 = y # To drag down the border-line
    line_segment, line_color = [(x1, y1), (x2, y2)], (255,255,255,128)
    card.line(line_segment, fill = line_color, width=1)
    return image

def stamp_watermark(image, filepath_of_watermark):
    "Returns the card by stamping the watermark at bottom right corner"
    offset = -1 # Distance between image border and watermark
    watermark = Image.open(filepath_of_watermark).convert("RGBA")
    wm_size = (watermark.size[0] // (offset + 5), watermark.size[1] // (offset + 5))
    watermark = watermark.resize(wm_size)

    watermark_location = (vc_size[0] - wm_size[0] - offset,
                          vc_size[1] - wm_size[1] - offset) # Bottom right corner

    image.paste(watermark, watermark_location, mask=watermark)
    watermark.close()
    return image

visual_card = Image.new("RGBA", vc_size, color)
visual_card = stamp_watermark(visual_card, "../etc/watermark.png")
profile_pic = Image.open(profile_pic_path)

profile_pic = crop_max_square(profile_pic).resize((profile_pic_size), Image.LANCZOS)
# In fn-call of `mask_circle_transparent`, increase 2nd arg to create blur effect at border
profile_pic = mask_circle_transparent(profile_pic, 1)

visual_card.paste(profile_pic, overlay_location, mask=profile_pic) # Overlay profile-pic on visual-card

visual_card = render_text(visual_card, f'{username}|{user_handle}', (uname_fntsz - 10, 10), uname_fntsz)
visual_card = render_text(visual_card, user_location, (uname_fntsz - 10, 35), other_fntsz)
visual_card = create_broder(visual_card, 60)

#visual_card.show()
visual_card.save("./visual_card.png")
