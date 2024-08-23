from flask  import Flask, request, jsonify, send_file
import requests
import base64
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail, Attachment, FileContent, FileName, FileType, Disposition
from dotenv import load_dotenv

# silhouette, rembg
from PIL import Image, ImageDraw, ImageFont
import io
from rembg import remove
import zipfile

# .envファイルを読み込み
load_dotenv()

app = Flask(__name__)

def generate_image(prompt):
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
    api_key = os.getenv('STABILITY_API_KEY')  # 環境変数からAPIキーを取得

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "text_prompts": [
            {
                "text": f"{prompt} with a white background",
                "weight": 1.0
            }
        ],
        "cfg_scale": 7.0,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 50
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        artifacts = response_json.get("artifacts", [])
        if artifacts:
            artifact = artifacts[0]
            if artifact.get("finishReason") == "SUCCESS":
                img_data = artifact.get("base64")
                return base64.b64decode(img_data)
    return None

def remove_background(image_data):
    # 画像データをPIL Imageオブジェクトに変換
    input_image = Image.open(io.BytesIO(image_data))
    
    # rembgを使用して背景を削除
    output_image = remove(input_image)
    
    # 結果の画像をバイトデータに変換
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def make_quiz(image_data, hint, quiz):
    # Load the image from image_data
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")

    # Load a font
    font_path = "./Kaisotai-Next-UP-B.ttf"  # MacOS用のフォントパス
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text sizes
    draw = ImageDraw.Draw(image)
    hint_bbox = draw.textbbox((0, 0), hint, font=font)
    quiz_bbox = draw.textbbox((0, 0), quiz, font=font)
    hint_height = hint_bbox[3] - hint_bbox[1]
    quiz_height = quiz_bbox[3] - quiz_bbox[1]

    # Calculate new image size
    width, height = image.size
    new_height = height + hint_height + quiz_height + 20  # 20 is for padding

    # Create a new image with the new size and a transparent background
    new_image = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))

    # Paste the original image in the center of the new image
    paste_position = (0, hint_height + 10)  # 10 is for padding
    new_image.paste(image, paste_position)

    # Create black silhouette
    datas = new_image.getdata()
    new_data = []
    for item in datas:
        if item[3] > 0:
            new_data.append((0, 0, 0, 255))
        else:
            new_data.append((0, 0, 0, 0))
    new_image.putdata(new_data)

    # Draw text on the image
    draw = ImageDraw.Draw(new_image)

    # Calculate text positions
    hint_position = ((width - (hint_bbox[2] - hint_bbox[0])) // 2, 5)
    quiz_position = ((width - (quiz_bbox[2] - quiz_bbox[0])) // 2, new_height - quiz_height - 5)

    # Draw the text on the image
    draw.text(hint_position, hint, font=font, fill=(255, 255, 255, 255))
    draw.text(quiz_position, quiz, font=font, fill=(255, 255, 255, 255))

    # Convert the image to bytes
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr

def make_answer(image_data, answer):
    #make_quizを参考に、でもシルエット化せずに、フォントサイズを大きくして、下に表示
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")
    font_path = "./Kaisotai-Next-UP-B.ttf"  # MacOS用のフォントパス
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(image)
    answer_bbox = draw.textbbox((0, 0), answer, font=font)
    answer_width = answer_bbox[2] - answer_bbox[0]
    answer_height = answer_bbox[3] - answer_bbox[1]
    width, height = image.size
    new_height = height + answer_height + 20  # 20 is for padding
    new_image = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))
    new_image.paste(image, (0, 0))
    draw = ImageDraw.Draw(new_image)  # Create a new draw object for the new image
    answer_position = ((width - answer_width) // 2, new_height - answer_height - 10)
    draw.text(answer_position, answer, font=font, fill=(255, 255, 255, 255), anchor="lt")
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def send_email(image_data, image_name):
    # もし image_data が str 型で渡された場合、bytes 型に変換
    if isinstance(image_data, str):
        image_data = image_data.encode('utf-8')

    # SendGrid APIを使用してメールを送信
    message = SendGridMail(
        from_email=os.getenv('MAIL_DEFAULT_SENDER'),
        to_emails=os.getenv('MAIL_DEFAULT_SENDER'),
        subject="Generated Image",
        plain_text_content="Please find the attached generated image."
    )
    
    # 添付ファイルの追加
    encoded_file = base64.b64encode(image_data).decode()
    attached_file = Attachment(
        FileContent(encoded_file),
        FileName(image_name),
        FileType('image/png'),
        Disposition('attachment')
    )
    message.attachment = attached_file

    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def make_zip(image_datas, image_names):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image_data, image_name in zip(image_datas, image_names):
            zip_file.writestr(image_name, image_data)
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        prompt = data.get('prompt_always_in_English')
        image_name = data.get('image_name_always_in_English')
        hint = data.get('hint')
        quiz = data.get('quiz')
        answer = data.get('answer')
        locale = data.get('locale')
        # if image name in img folder, then just return the zip of img file
        if os.path.exists(f"./img/{image_name}_{locale}/"):
            image_files = os.listdir(f"./img/{image_name}_{locale}/")
            image_datas = []
            image_names = []
            for file_name in image_files:
                with open(f"./img/{image_name}_{locale}/{file_name}", "rb") as file:
                    image_datas.append(file.read())
                image_names.append(file_name)
            zip_buffer = make_zip(image_datas, image_names)
            return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f"{image_name}.zip")
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        image_data = generate_image(prompt)
        if image_data:
            image_pathname_quiz= image_name + "_quiz.png"
            image_pathname_answer= image_name + "_answer.png"
            print("make quiz")
            image_datas = []
            image_names = [image_pathname_quiz, image_pathname_answer]
            image_datas.append(make_quiz(remove_background(image_data), hint, quiz))
            image_datas.append(make_answer(remove_background(image_data), answer))
            print("make zip")
            zip_buffer = make_zip(image_datas, image_names)
            send_email(zip_buffer.getvalue(), f"{image_name}.zip")
            return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f"{image_name}.zip")
        else:
            return jsonify({"error": "Failed to generate image"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/generate_answer', methods=['POST'])
def generate_answer():
    pass

if __name__ == '__main__':
    app.run(debug=True)
