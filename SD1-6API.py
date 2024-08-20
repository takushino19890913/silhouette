import requests

# APIエンドポイントとAPIキーを設定
api_url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-6/text-to-image"
api_key = "sk-vJYBm2xsbmVby7nbFxQMLE2KkRc0JTUR032Rj7jzfek10Hgj"  # 自分のAPIキーに置き換えてください

# リクエストヘッダーとデータを設定
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "text_prompts": [
        {
            "text": "A futuristic city skyline at sunset",  # プロンプトを指定
            "weight": 1.0
        }
    ],
    "cfg_scale": 7.0,  # クリエイティブな生成の制御
    "clip_guidance_preset": "FAST_BLUE",  # CLIPガイダンスのプリセット
    "height": 512,  # 生成する画像の高さ
    "width": 512,   # 生成する画像の幅
    "samples": 1,   # 生成する画像のサンプル数
    "steps": 50     # ステップ数
}

# リクエストを送信
response = requests.post(api_url, headers=headers, json=data)

# デバッグのためのレスポンスの内容を確認
if response.status_code == 200:
    response_json = response.json()


    artifacts = response_json.get("artifacts", [])

    for i, artifact_group in enumerate(artifacts):
        print(f"\nProcessing artifact_group {i}: {artifact_group}")
        if isinstance(artifact_group, list):
            for j, artifact in enumerate(artifact_group):
                print(f"Processing artifact {j}: {artifact}")  # 各アーティファクトの内容を出力
                if isinstance(artifact, dict):
                    if artifact.get("finishReason") == "SUCCESS":
                        img_data = artifact.get("base64")
                        if img_data:
                            # base64データをデコードしてファイルに保存
                            with open(f"output_image_{i}_{j}.png", "wb") as img_file:
                                img_file.write(base64.b64decode(img_data))
                            print(f"Image {i}_{j} saved successfully!")
                    elif artifact.get("finishReason") == "CONTENT_FILTERED":
                        print(f"Image {i}_{j} was content filtered and not saved.")
                else:
                    print(f"Unexpected data structure in artifact: {artifact}")
        else:
            print(f"Unexpected data structure in artifact_group {i}: {artifact_group}")
else:
    print(f"Failed to generate image. Status code: {response.status_code}")
    print("Response Text:")
    print(response.text)