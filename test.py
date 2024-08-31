from app import send_email,app,make_answer  # Flaskアプリケーションをインポート


def save_img(image_data, folder_path,image_name):
    if not os.path.exists(f"./img/{folder_path}/"):
        os.makedirs(f"./img/{folder_path}/")
    with open(f"./img/{folder_path}/{image_name}.png", "wb") as file:
        file.write(image_data)

# Flaskアプリケーションコンテキストを設定
with app.app_context():
    # メール送信テスト
    # send_email("cat", ".img/cat.png")
    import os

    image_path = os.path.join("./img", "dog_en", "dog_answer.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        save_img(make_answer(image_data, "It's a dog!!"), "dog_en", "dog_answer")
    else:
        print(f"Error: File not found - {image_path}")

