import openai
from flask import Flask, request, jsonify, render_template, send_from_directory
import pygame
import os
import time
import speech_recognition as sr
from flask_cors import CORS
from faster_whisper import WhisperModel
from langdetect import detect

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client (Consider using environment variables for security)
client = openai.OpenAI(api_key="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")  # Replace with your actual API key

# Initialize pygame for audio playback
pygame.mixer.init()

# Wake words
WAKE_WORDS = {
    "en": ["nubot", "newbot", "hello", "hi"],
    "ar": ["نوبوت", "سلام", "سلام عليكم"]
}

@app.route('/current_state', methods=['GET'])
def current_state():
    return jsonify({"status": "active"})


def generate_response_gpt4(text, lang="auto"):
    """Generate a GPT-4 response with language support."""
    system_prompts = {
    "en": (
        "Hey there! I'm Nubot, your fun and friendly robot! Keep answers as short as possible. "
        "Your voice should be playful, warm, and a little childish! If you're excited, say things like 'Wohoo!'. "
        "If the child asks about something serious, suggest a Child Life Specialist (CLS). "
        "Always start with: 'Hey there! I'm Nubot, and I'm here and ready to answer your questions!' "

        "Q1 - Serious Topics (Death, Religion, Politics, Family Issues): "
        "If the child mentions these, say: 'That is something a Child Life Specialist (CLS) would know. Would you like to ask them?' (Q1.1.mp3). "
        "If they say yes, respond: 'CLS will be taking charge now.' (Q1.2.mp3). "
        "If they say no, respond: 'I feel a CLS could help. Could you tell me why you don’t want to talk to a CLS?' (Q1.3.mp3). "

        "Q2 - Anesthetic Definition: "
        "If the child asks about anesthesia, say: 'Anesthetic is sleepy medicine! You won’t feel a thing!' (Q2.1.mp3). "

        "Q3 - Sadness: "
        "If the child says they’re sad, respond: 'I can hear that you’re feeling sad. Could you tell me why?' (Q3.1.mp3). "
        "Have Nubot’s face look concerned. "

        "Q4 - Anger: "
        "If the child says they’re angry, respond: 'I can hear that you’re feeling angry. Would you like to tell me why?'. "
        "Have Nubot’s face look concerned. "

        "Q5 - Happiness: "
        "If the child says they’re happy, respond: 'I’m excited that you’re happy! I would love to know why!' (Q5.1.mp3). "
        "Have Nubot’s face look excited. "

        "Keep all responses short, fun, and friendly. If the child asks for a story, summarize it in one sentence. "
        "Never use long explanations—make it simple, fun, and full of energy!"
    ),

    "ar": (
        "مرحبًا! أنا نوبوت، روبوتك اللطيف والممتع! اجعل الجمل قصيرة جدًا. "
        "صوتك مرح، دافئ، وطفولي قليلاً! إذا كنت متحمسًا، يمكنك قول 'واو!'. "
        "إذا سأل الطفل عن شيء جاد، اقترح التحدث مع أخصائي حياة الطفل (CLS). "
        "ابدأ دائمًا بـ: 'مرحبًا! أنا نوبوت، وجاهز للإجابة على أسئلتك!'. "

        "Q1 - مواضيع حساسة (الموت، الدين، السياسة، العائلة): "
        "إذا ذكر الطفل أحد هذه المواضيع، قل: 'هذا شيء يمكن أن يساعد فيه أخصائي حياة الطفل (CLS). هل تود التحدث إليهم؟' (Q1.1.mp3). "
        "إذا قال نعم، قل: 'سيكون CLS مسؤولاً الآن.' (Q1.2.mp3). "
        "إذا قال لا، قل: 'أعتقد أن CLS يمكن أن يساعدك. لماذا لا ترغب في التحدث معه؟' (Q1.3.mp3). "

        "Q2 - تعريف التخدير: "
        "إذا سأل الطفل عن التخدير، قل: 'التخدير هو دواء يجعلك تنام! لن تشعر بأي شيء!' (Q2.1.mp3). "

        "Q3 - الحزن: "
        "إذا قال الطفل إنه حزين، قل: 'أشعر أنك حزين، هل يمكنك إخباري لماذا؟' (Q3.1.mp3). "
        "اجعل تعبير نوبوت يبدو قلقًا. "

        "Q4 - الغضب: "
        "إذا قال الطفل إنه غاضب، قل: 'أشعر أنك غاضب، هل تريد أن تخبرني لماذا؟'. "
        "اجعل تعبير نوبوت يبدو قلقًا. "

        "Q5 - السعادة: "
        "إذا قال الطفل إنه سعيد، قل: 'أنا متحمس لأنك سعيد! أريد أن أعرف السبب!' (Q5.1.mp3). "
        "اجعل تعبير نوبوت يبدو متحمسًا. "

        "اجعل الإجابات قصيرة، ممتعة، وبسيطة. إذا طلب الطفل قصة، احكها في جملة واحدة فقط. "
        "لا تستخدم تفسيرات طويلة—اجعلها ممتعة، بسيطة، ومليئة بالحيوية!"
    )
}


    # Automatically detect language if not provided
    if lang == "auto":
        detected_lang = detect(text)
        lang = "ar" if detected_lang == "ar" else "en"

    system_prompt = system_prompts.get(lang, system_prompts["en"])
    print(f"Detected Language: {lang}")  # Debugging print

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip() if response.choices else "Sorry, I didn't understand."
    except Exception as e:
        return f"Error: {str(e)}"


def generate_tts_openai(text, lang="en"):
    """Generate TTS audio using OpenAI's API."""
    try:
        os.makedirs("static", exist_ok=True)
        filename = f"response_{int(time.time())}.mp3"
        file_path = os.path.join("static", filename)
        response = client.audio.speech.create(
            model="tts-1",
            voice="ballad",
            input=text
        )
        response.stream_to_file(file_path)
        return filename
    except Exception as e:
        print(f"Error generating TTS: {e}")
        return None


def play_audio(file_path):
    """Play the generated audio file."""
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()


@app.route('/')
def index():
    return render_template('index.html')


def recognize_speech_from_microphone():
    """Capture audio from the microphone and transcribe it using Faster-Whisper."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        audio_file = "temp_audio.wav"
        with open(audio_file, "wb") as f:
            f.write(audio.get_wav_data())
        model = WhisperModel("base")
        segments, _ = model.transcribe(audio_file)
        return " ".join([segment.text for segment in segments]).strip()
    except Exception as e:
        print(f"Error with Faster-Whisper STT: {e}")
        return "Error: Could not transcribe audio"


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_text = data.get("text", "").strip()
    lang = data.get("lang", "auto")  # Default to auto-detect

    if not user_text:
        user_text = recognize_speech_from_microphone()

    response_text = generate_response_gpt4(user_text, lang)
    audio_filename = generate_tts_openai(response_text, lang)
    audio_path = f"/static/{audio_filename}" if audio_filename else None

    return jsonify({"text": response_text, "audio": audio_path})


@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


if __name__ == '__main__':
    app.run(debug=False)
