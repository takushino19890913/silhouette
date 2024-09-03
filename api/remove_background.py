import cv2
import numpy as np
from PIL import Image
import io
import base64

def remove_background(image_data):
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)

    mask = np.zeros(img.shape[:2], np.uint8)
    cv2.drawContours(mask, [max_contour], 0, (255), -1)

    transparent = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    transparent[:, :, 3] = mask

    pil_image = Image.fromarray(cv2.cvtColor(transparent, cv2.COLOR_BGRA2RGBA))

    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # バイナリデータをBase64エンコードして返す
    return base64.b64encode(img_byte_arr).decode('ascii')