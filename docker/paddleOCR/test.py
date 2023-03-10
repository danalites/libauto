import json
import base64
import requests

png_file = "./image1.png"

with open(png_file, 'rb') as f:
    base64_bytes = base64.b64encode(f.read())
    base64_string = base64_bytes.decode('utf-8')

# POST to server
url = 'http://localhost:8866/predict/ocr_system'
data = {'images': [base64_string]}

value = requests.post(url, json = data).text
print(value)