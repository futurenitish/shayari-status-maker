import os
import random
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)

# Register the Mukta font
FONT_PATH = "Mukta-Bold.ttf"
FINAL_SIZE = (1080, 1080)
PADDING = 40
TEXT_COLOR = (255, 255, 255)
SHADOW_BG_COLOR = (0, 0, 0, 180)
TEXT_AREA_WIDTH = FINAL_SIZE[0] // 2 - PADDING * 2
LINE_SPACING = 10
RADIUS = 20

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_status():
    # Get the input text for Shayari or use a random one
    shayari_input = request.form.get('shayari', '').strip()
    if not shayari_input:
        shayari_input = get_random_shayari()

    # Generate the image
    bg_path = os.path.join("static", "backgrounds", random.choice(os.listdir("static/backgrounds")))
    bg = Image.open(bg_path).convert("RGB")
    width, height = bg.size
    min_side = min(width, height)
    left = (width - min_side) // 2
    top = (height - min_side) // 2
    bg = bg.crop((left, top, left + min_side, top + min_side)).resize(FINAL_SIZE, Image.LANCZOS)
    draw = ImageDraw.Draw(bg, "RGBA")

    # Load fonts
    font_large = ImageFont.truetype(FONT_PATH, 70)
    font_medium = ImageFont.truetype(FONT_PATH, 50)
    font_small = ImageFont.truetype(FONT_PATH, 40)

    # Generate header
    gm_text = get_greeting()
    date_text = datetime.now().strftime("%d %B %Y")
    draw_combined_header(draw, gm_text, date_text, font_large, font_medium, PADDING, PADDING)

    # Add Shayari text
    draw_text_block(draw, shayari_input, font_medium, PADDING, FINAL_SIZE[1] // 2, TEXT_AREA_WIDTH)

    # Add user image
    user_img = Image.open("static/user2.png").convert("RGBA")
    max_width = FINAL_SIZE[0] // 2 - PADDING
    aspect = user_img.height / user_img.width
    user_img_resized = user_img.resize((max_width, int(max_width * aspect)), Image.LANCZOS)

    x_img = FINAL_SIZE[0] - user_img_resized.width - PADDING // 2
    y_img = (FINAL_SIZE[1] - user_img_resized.height) // 2
    bg.paste(user_img_resized, (x_img, y_img), user_img_resized)

    # Add "Bhim Singh" text below the user image
    text_x = x_img
    text_y = y_img + user_img_resized.height + 20
    draw_text_block(draw, "Babli Devi Shekhawat", font_small, text_x, text_y, user_img_resized.width)
    draw_text_block(draw, "Babli Devi Shekhawat", font_small, PADDING, FINAL_SIZE[1] - 80, TEXT_AREA_WIDTH)

    # Save the generated image
    output_path = "static/output/status_output.jpg"
    bg.convert("RGB").save(output_path, "JPEG", quality=85)

    return render_template('index.html', output_image=output_path)

@app.route('/download/<filename>')
def download_image(filename):
    return send_from_directory('static/output', filename)

# Helper functions for generating content

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 21:
        return "Good Evening"
    else:
        return "Good Night"

def get_random_shayari():
    with open("shayari.txt", "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = [block.strip() for block in content.split("\n\n") if block.strip()]
    return random.choice(blocks)

def draw_rounded_rectangle(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)

def draw_text_block(draw, text, font, x, y_center, max_width):
    lines = []
    for line in text.split("\n"):
        words = line.split()
        if not words:
            lines.append("")
            continue
        temp_line = ""
        for word in words:
            test_line = temp_line + word + " "
            w = draw.textlength(test_line, font=font)
            if w <= max_width:
                temp_line = test_line
            else:
                lines.append(temp_line.strip())
                temp_line = word + " "
        lines.append(temp_line.strip())

    total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] + LINE_SPACING for line in lines)
    y = y_center - total_height // 2

    max_line_width = max(draw.textlength(line, font=font) for line in lines)
    bg_box = (x - PADDING // 2, y - PADDING // 2, x + max_line_width + PADDING // 2, y + total_height + PADDING // 2)
    draw_rounded_rectangle(draw, bg_box, RADIUS, SHADOW_BG_COLOR)

    for line in lines:
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += font.getbbox(line)[3] - font.getbbox(line)[1] + LINE_SPACING

def draw_combined_header(draw, gm_text, date_text, font1, font2, x, y_top):
    gm_w = draw.textlength(gm_text, font=font1)
    date_w = draw.textlength(date_text, font=font2)
    max_width = max(gm_w, date_w)

    gm_h = font1.getbbox(gm_text)[3] - font1.getbbox(gm_text)[1]
    date_h = font2.getbbox(date_text)[3] - font2.getbbox(date_text)[1]
    total_h = gm_h + date_h + LINE_SPACING * 2

    bg_box = (x - PADDING // 2, y_top - PADDING // 2, x + max_width + PADDING // 2, y_top + total_h + PADDING // 2)
    draw_rounded_rectangle(draw, bg_box, RADIUS, SHADOW_BG_COLOR)

    draw.text((x, y_top), gm_text, font=font1, fill=TEXT_COLOR)
    draw.text((x, y_top + gm_h + LINE_SPACING * 2), date_text, font=font2, fill=TEXT_COLOR)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, ssl_context=('cert.pem', 'key.pem'))
