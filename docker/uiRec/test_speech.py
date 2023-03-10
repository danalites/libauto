import json
import base64
import requests

mp3_file = "./tmp/sample.mp3"
with open(mp3_file, 'rb') as f:
    base64_bytes = base64.b64encode(f.read())
    base64_string = base64_bytes.decode('utf-8')

# POST to server
url = 'http://localhost:8867/speech'
data = {'audio': base64_string}

value = requests.post(url, json = data).text
print(json.loads(value))