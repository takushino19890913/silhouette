from PIL import Image, ImageDraw, ImageFont
import io
import base64

def make_quiz(image_data, hint, quiz):
    image_data = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")

    font_path = "./Kaisotai-Next-UP-B.ttf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)

    draw = ImageDraw.Draw(image)
    hint_bbox = draw.textbbox((0, 0), hint, font=font)
    quiz_bbox = draw.textbbox((0, 0), quiz, font=font)
    hint_height = hint_bbox[3] - hint_bbox[1]
    quiz_height = quiz_bbox[3] - quiz_bbox[1]

    width, height = image.size
    new_height = height + hint_height + quiz_height + 20

    new_image = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))
    paste_position = (0, hint_height + 10)
    new_image.paste(image, paste_position)

    datas = new_image.getdata()
    new_data = []
    for item in datas:
        if item[3] > 0:
            new_data.append((0, 0, 0, 255))
        else:
            new_data.append((0, 0, 0, 0))
    new_image.putdata(new_data)

    draw = ImageDraw.Draw(new_image)

    hint_position = ((width - (hint_bbox[2] - hint_bbox[0])) // 2, 5)
    quiz_position = ((width - (quiz_bbox[2] - quiz_bbox[0])) // 2, new_height - quiz_height - 5)

    draw.text(hint_position, hint, font=font, fill=(255, 255, 255, 255))
    draw.text(quiz_position, quiz, font=font, fill=(255, 255, 255, 255))

    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # バイナリデータをBase64エンコードして返す
    return base64.b64encode(img_byte_arr).decode('ascii')