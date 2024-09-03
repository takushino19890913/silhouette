from PIL import Image, ImageDraw, ImageFont
import io
import base64

def make_answer(image_data, answer):
    image_data = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")
    font_path = "./Kaisotai-Next-UP-B.ttf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(image)
    answer_bbox = draw.textbbox((0, 0), answer, font=font)
    answer_width = answer_bbox[2] - answer_bbox[0]
    answer_height = answer_bbox[3] - answer_bbox[1]
    width, height = image.size
    new_height = height + answer_height + 20
    new_image = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))
    new_image.paste(image, (0, 0))
    draw = ImageDraw.Draw(new_image)
    answer_position = ((width - answer_width) // 2, new_height - answer_height - 10)
    draw.text(answer_position, answer, font=font, fill=(255, 255, 255, 255), anchor="lt")
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # バイナリデータをBase64エンコードして返す
    return base64.b64encode(img_byte_arr).decode('ascii')