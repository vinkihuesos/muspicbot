from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import os
from io import BytesIO

def round_corners(im, radius, round_left=True, round_right=True):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size

    if round_left:
        alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    if round_right:
        alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
        alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))

    im.putalpha(alpha)
    return im

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}" if line else word
        if font.getlength(test_line) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return "\n".join(lines)

def draw_text_with_shadow(draw, position, text, font, fill="white", shadow_color="black", shadow_offset=(2, 2), spacing=0, multiline=False):
    x, y = position
    shadow_x, shadow_y = shadow_offset
    shadow_position = (x + shadow_x, y + shadow_y)

    if multiline:
        draw.multiline_text(shadow_position, text, font=font, fill=shadow_color, spacing=spacing)
        draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing)
    else:
        draw.text(shadow_position, text, font=font, fill=shadow_color)
        draw.text((x, y), text, font=font, fill=fill)

def generate_images(cover_path, background_path, artists, release, lyrics, bot_username):
    WIDTH, HEIGHT = 1080, 1080
    COVER_WIDTH = 400
    COVER_HEIGHT = int(HEIGHT * 0.8)
    PADDING_Y = (HEIGHT - COVER_HEIGHT) // 2
    RADIUS = 60

    full_bg = Image.open(background_path).convert("RGB").resize((WIDTH * 2, HEIGHT))
    blurred_bg = full_bg.filter(ImageFilter.GaussianBlur(20))
    blurred_bg_left = blurred_bg.crop((0, 0, WIDTH, HEIGHT))
    blurred_bg_right = blurred_bg.crop((WIDTH, 0, WIDTH * 2, HEIGHT))

    full_cover = Image.open(cover_path).convert("RGB").resize((880, 880))
    left_cover = full_cover.crop((0, 0, 440, 880)).resize((COVER_WIDTH, COVER_HEIGHT))
    right_cover = full_cover.crop((440, 0, 880, 880)).resize((COVER_WIDTH, COVER_HEIGHT))

    left_cover = round_corners(left_cover, RADIUS, round_left=True, round_right=False)
    right_cover = round_corners(right_cover, RADIUS, round_left=False, round_right=True)

    font_large = ImageFont.truetype("fonts/gont.ttf", 48)
    font_medium = ImageFont.truetype("fonts/gont.ttf", 42)
    font_small = ImageFont.truetype("fonts/gont.ttf", 32)

    # Слайд 1
    slide1 = blurred_bg_left.copy()
    slide1.paste(left_cover, (WIDTH - COVER_WIDTH, PADDING_Y), mask=left_cover)
    draw1 = ImageDraw.Draw(slide1)

    draw_text_with_shadow(draw1, (60, 50), f"BOT: {bot_username}", font=font_medium)

    artist_wrapped = wrap_text(artists, font_large, WIDTH - COVER_WIDTH - 80)
    release_wrapped = wrap_text(release, font_large, WIDTH - COVER_WIDTH - 80)

    artist_bbox = draw1.multiline_textbbox((0, 0), artist_wrapped, font=font_large, spacing=10)
    artist_height = artist_bbox[3] - artist_bbox[1]

    release_bbox = draw1.multiline_textbbox((0, 0), release_wrapped, font=font_large, spacing=10)
    release_height = release_bbox[3] - release_bbox[1]

    spacing_between = 40
    total_height = artist_height + spacing_between + release_height
    y_text = (HEIGHT - total_height) // 2

    draw_text_with_shadow(draw1, (60, y_text), artist_wrapped, font=font_large, spacing=10, multiline=True)
    draw_text_with_shadow(draw1, (60, y_text + artist_height + spacing_between), release_wrapped, font=font_large, spacing=10, multiline=True)
    draw_text_with_shadow(draw1, (60, HEIGHT - 100), "t.me/chmpns_music", font=font_small)

    output1 = BytesIO()
    slide1.save(output1, format="JPEG")
    output1.seek(0)

    # Слайд 2
    slide2 = blurred_bg_right.copy()
    slide2.paste(right_cover, (0, PADDING_Y), mask=right_cover)
    draw2 = ImageDraw.Draw(slide2)

    lyrics_wrapped = wrap_text(lyrics.upper(), font=font_medium, max_width=WIDTH - COVER_WIDTH - 80)
    lyrics_bbox = draw2.multiline_textbbox((0, 0), lyrics_wrapped, font=font_medium, spacing=10)
    lyrics_height = lyrics_bbox[3] - lyrics_bbox[1]
    lyrics_y = (HEIGHT - lyrics_height) // 2

    draw_text_with_shadow(draw2, (COVER_WIDTH + 60, lyrics_y), lyrics_wrapped, font=font_medium, spacing=10, multiline=True)

    output2 = BytesIO()
    slide2.save(output2, format="JPEG")
    output2.seek(0)

    return output1, output2
