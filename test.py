from app import send_email, app  # Flaskアプリケーションをインポート

# Flaskアプリケーションコンテキストを設定
with app.app_context():
    # メール送信テスト
    send_email("cat", ".img/cat.png")
