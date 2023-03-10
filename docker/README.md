## Server-side

### Bark server
- Optional: this is only needed if you want to send notifications to your iPhone/iPads. 
- Bark server gets HTTP requests and send notifications to APN servers (which is later forwarded to your iPhones/iPads). You can also use the public server: https://api.day.app

### UI-detection
- Optional: this is only needed if you want to use programming-by-demonstration (PBD) to generate UI-located actions (i.e., `os.record(name-of-recorded-action, {{ {'mode':'icon'} }})`). In the icon mode, our app will automatically detect the UI elements that you click (the image is saved and use to find location next time).

### Speech Recognition
- Speech-recognition: a light-weight speech recognition server based on Flask and SpeechRecognition package. It supports English only.

### PaddleSpeech
- Optional: the image size can by huge. https://aistudio.baidu.com/aistudio/projectdetail/4354592?channelType=0&channel=0
- Docker image: https://hub.docker.com/r/paddlecloud/paddlespeech
