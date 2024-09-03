from flask import Flask, request, jsonify, send_file
import requests
import os
import io
import zipfile
import base64
from dotenv import load_dotenv
from api.generate_image import generate_image
from api.remove_background import remove_background
from api.make_quiz import make_quiz
from api.make_answer import make_answer
from api.send_email import send_email

load_dotenv()

app = Flask(__name__)

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def make_zip(image_datas, image_names):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image_data, image_name in zip(image_datas, image_names):
            zip_file.writestr(image_name, base64.b64decode(image_data))
    zip_buffer.seek(0)
    return base64.b64encode(zip_buffer.getvalue()).decode('ascii')

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # 必要なデータが存在するか確認
        required_fields = ['prompt_always_in_English', 'image_name_always_in_English', 'hint', 'quiz', 'answer', 'locale']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        if os.path.exists(f"./img/{data['image_name_always_in_English']}_{data['locale']}/"):
            image_files = os.listdir(f"./img/{data['image_name_always_in_English']}_{data['locale']}/")
            image_datas = []
            image_names = []
            for file_name in image_files:
                with open(f"./img/{data['image_name_always_in_English']}_{data['locale']}/{file_name}", "rb") as file:
                    image_datas.append(file.read())
                image_names.append(file_name)
            zip_buffer = make_zip(image_datas, image_names)
            return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f"{data['image_name_always_in_English']}.zip")

        if not data['prompt_always_in_English']:
            return jsonify({"error": "Prompt is required"}), 400

        # Call generate_image API
        response = requests.post(f'{BASE_URL}/api/generate_image', json={'prompt': data['prompt_always_in_English']})
        if response.status_code != 200:
            return jsonify({"error": "Failed to generate image"}), 500
        image_data = response.content

        # Call remove_background API
        response = requests.post(f'{BASE_URL}/api/remove_background', data=image_data)
        if response.status_code != 200:
            return jsonify({"error": "Failed to remove background"}), 500
        image_data_no_bg = response.content

        # Call make_quiz API
        response = requests.post(f'{BASE_URL}/api/make_quiz', 
                                 json={'image_data': image_data_no_bg.decode('latin-1'), 'hint': data['hint'], 'quiz': data['quiz']})
        if response.status_code != 200:
            return jsonify({"error": "Failed to make quiz"}), 500
        quiz_image = response.content

        # Call make_answer API
        response = requests.post(f'{BASE_URL}/api/make_answer', 
                                 json={'image_data': image_data_no_bg.decode('latin-1'), 'answer': data['answer']})
        if response.status_code != 200:
            return jsonify({"error": "Failed to make answer"}), 500
        answer_image = response.content

        image_pathname_quiz = data['image_name_always_in_English'] + "_quiz.png"
        image_pathname_answer = data['image_name_always_in_English'] + "_answer.png"
        image_datas = [quiz_image, answer_image]
        image_names = [image_pathname_quiz, image_pathname_answer]

        zip_data = make_zip(image_datas, image_names)
        print(f"Zip data length: {len(zip_data)}")

        # Call send_email API
        email_response, status_code = send_email(zip_data, data['image_name_always_in_English'])
        if status_code != 200:
            return jsonify(email_response), status_code

        return jsonify({"message": "Quiz generated and email sent successfully"}), 200

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_image', methods=['POST'])
def generate_image_route():
    data = request.get_json()
    prompt = data.get('prompt')
    return generate_image(prompt)

@app.route('/api/remove_background', methods=['POST'])
def remove_background_route():
    image_data = request.data
    return remove_background(image_data)

@app.route('/api/make_quiz', methods=['POST'])
def make_quiz_route():
    data = request.get_json()
    return make_quiz(data['image_data'], data['hint'], data['quiz'])

@app.route('/api/make_answer', methods=['POST'])
def make_answer_route():
    data = request.get_json()
    return make_answer(data['image_data'], data['answer'])

@app.route('/api/send_email', methods=['POST'])
def send_email_route():
    data = request.get_json()
    return send_email(data['zip_data'], data['image_name'])

if __name__ == '__main__':
    app.run(debug=True)
