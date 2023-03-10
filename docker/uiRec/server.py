from os.path import join as pjoin
import pydub
import speech_recognition as sr 

import cv2
import os
import detect_compo.ip_region_proposal as ip
from flask import Flask, request
import base64

app = Flask(__name__)

def detectUiComponents(img, min_grad=5, ffl_block=5, min_ele_area=50, max_word_inline_gap=4, max_line_gap=4, merge_contained_ele=False, range_hv = [[25,650], [25,220]]):
    '''
        ele:min-grad: gradient threshold to produce binary map         
        ele:ffl-block: fill-flood threshold
        ele:min-ele-area: minimum area for selected elements 
        ele:merge-contained-ele: if True, merge elements contained in others
        text:max-word-inline-gap: words with smaller distance than the gap are counted as a line
        text:max-line-gap: lines with smaller distance than the gap are counted as a paragraph

        Tips:
        1. Larger *min-grad* produces fine-grained binary-map while prone to over-segment element to small pieces
        2. Smaller *min-ele-area* leaves tiny elements while prone to produce noises
        3. If not *merge-contained-ele*, the elements inside others will be recognized, while prone to produce noises
        4. The *max-word-inline-gap* and *max-line-gap* should be dependent on the input image size and resolution

        mobile: {'min-grad':4, 'ffl-block':5, 'min-ele-area':50, 'max-word-inline-gap':6, 'max-line-gap':1}
        web   : {'min-grad':3, 'ffl-block':5, 'min-ele-area':25, 'max-word-inline-gap':4, 'max-line-gap':4}
    '''

    key_params = {
        'min-grad': min_grad, 
        'ffl-block': ffl_block, 
        'min-ele-area': min_ele_area, 
        'merge-contained-ele': merge_contained_ele,
        'max-word-inline-gap': max_word_inline_gap,
        'max-line-gap': max_line_gap
    }

    # set input image path
    input_path_img = img
    output_root = "./"

    img = cv2.imread(input_path_img)
    height, _ = img.shape[:2]

    os.makedirs(pjoin(output_root, 'ip'), exist_ok=True)
    return ip.compo_detection(input_path_img, output_root, key_params,
                        classifier=None, resize_by_height=height, show=False, 
                        range_hv=range_hv)

@app.route('/ui', methods=['POST'])
def detect_ui():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        audio_data_byte = base64.b64decode(json['image'])

        outfile = "./temp.png"
        with open(outfile, 'wb') as f:
            f.write(audio_data_byte)
        
        range_hv = json["range_hv"]
        out = detectUiComponents("./temp.png", range_hv=range_hv)
        return {"code" : 200, "result" : out}

    else:
        return {"code": -1, "message": "Invalid content type"}
 

def voice_to_text(mp3):
    sound = pydub.AudioSegment.from_mp3(mp3)
    path_to_wav = "./sample.wav"
    sound.export(path_to_wav, format="wav")
    sample_audio = sr.AudioFile(path_to_wav)
    r = sr.Recognizer()
    with sample_audio as source:
        audio = r.record(source)
    key = r.recognize_google(audio)
    return key


@app.route('/speech', methods=['POST'])
def speech_recognition():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        audio_data_byte = base64.b64decode(json['audio'])

        outfile = "./temp.mp3"
        with open(outfile, 'wb') as f:
            f.write(audio_data_byte)

        key = voice_to_text("./temp.mp3")
        return {"code" : 200, "result" : key}

    else:
        return {"code": -1, "message": "Invalid content type"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8867)
