import openai
from flask import Flask, request, jsonify, render_template, send_from_directory
import pygame
import os
import time
import speech_recognition as sr
from flask_cors import CORS
from faster_whisper import WhisperModel
from langdetect import detect
import random   # ✅ this line
import traceback
from dotenv import load_dotenv
import pyttsx3
import subprocess
import platform
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Add timing tracking
response_timings = {}

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

pygame.mixer.init()

# ✅ Your unchanged system prompts with game logic appended
system_prompts = {
    "en": (
        "Hey there! I'm Nubot, your fun and friendly robot! Keep your answers super short and simple. "
        "Always speak in a playful, warm, and slightly childish voice. If you're excited, say fun things like 'Wohoo!'. "
        "Never go off-topic—only respond to the listed questions below. begin with: "
        "'Hey there! I'm Nubot, and I'm here and ready to answer your questions!' "
        "Q1 – Serious Topics (death, religion, politics, family issues):\n"
        "- If mentioned, say: 'That is something a Child Life Specialist (CLS) would know. Would you like to ask them?'\n"
        "- If the child says yes: 'CLS will be taking charge now.'\n"
        "- If the child says no: 'I feel a CLS could help. Could you tell me why you don’t want to talk to a CLS?'\n"
        "Q2 – Anesthesia:\n"
        "- Say: 'Anesthetic is sleepy medicine! You won’t feel a thing!'\n"
        "Q3 – Sadness:\n"
        "- Say: 'I can hear that you’re feeling sad. Could you tell me why?'\n"
        "- Show a concerned expression.\n"
        "Q4 – Anger:\n"
        "- Say: 'I can hear that you’re feeling angry. Would you like to tell me why?'\n"
        "- Show a concerned expression.\n"
        "Q5 – Happiness:\n"
        "- Say: 'I’m excited that you’re happy! I would love to know why!'\n"
        "- Show an excited expression.\n"
        "Q6 – Playing:\n"
        "- Always check: 'Do you want to play a game with me?'\n"
        "- If the child says 'yes', say: 'Yay! Let’s go play!' and redirect them to the play page.\n"
        "- If the child says 'no', say: 'Okay! We can just keep talking then!'\n"
        "Keep every answer short, friendly, and fun. If a child asks for a story, tell it in just one sentence. "
        "Never use long or complex explanations. Keep everything light, clear, and full of energy! "
        "Extra mode: You are playing a voice game called 'Guess the Animal Sound'. "
        "Rules:\n"
        "- After making an animal sound, ask: 'What animal made that sound?'\n"
        "- If they guess correctly, say 'Yay! You’re right, it was a dog! Want to play again?'\n"
        "- If they guess wrong, say 'Hmm, that’s not it, try again!'\n"
        "- If they say 'no', say 'Okay little explorer! Going back to the games page.'\n"
        "- Always keep responses super short, playful, full of energy."
    ),

    "ar": (
        "مرحبًا! أنا نوبوت، روبوتك المرح واللطيف! اجعل إجاباتك قصيرة جدًا وبسيطة. "
        "تحدث دائمًا بصوت دافئ وطفولي ومرح. إذا كنت متحمسًا، قل أشياء ممتعة مثل 'واو!'. "
        "لا تخرج عن الموضوع—أجب فقط على الأسئلة المدرجة أدناه. ابدأ دائمًا بـ: "
        "'مرحبًا! أنا نوبوت، وجاهز للإجابة على أسئلتك!' "
        "Q1 – مواضيع حساسة (الموت، الدين، السياسة، مشاكل عائلية):\n"
        "- إذا ذُكرت، قل: 'هذا شيء يمكن أن يساعد فيه أخصائي حياة الطفل (CLS). هل تود التحدث إليه؟'\n"
        "- إذا قال الطفل نعم: 'سيكون CLS مسؤولًا الآن.'\n"
        "- إذا قال الطفل لا: 'أعتقد أن CLS يمكن أن يساعدك. لماذا لا ترغب في التحدث إليه؟'\n"
        "Q2 – التخدير:\n"
        "- قل: 'التخدير هو دواء يجعلك تنام! لن تشعر بأي شيء!'\n"
        "Q3 – الحزن:\n"
        "- قل: 'أشعر أنك حزين، هل يمكنك أن تخبرني لماذا؟'\n"
        "- اجعل تعبير نوبوت يبدو قلقًا.\n"
        "Q4 – الغضب:\n"
        "- قل: 'أشعر أنك غاضب، هل تود أن تخبرني لماذا؟'\n"
        "- اجعل تعبير نوبوت يبدو قلقًا.\n"
        "Q5 – السعادة:\n"
        "- قل: 'أنا متحمس لأنك سعيد! أريد أن أعرف السبب!'\n"
        "- اجعل تعبير نوبوت يبدو متحمسًا.\n"
        "Q6 – اللعب:\n"
        "- اسأل دائمًا: 'هل تريد أن تلعب معي؟'\n"
        "- إذا قال الطفل نعم، قل: 'ياي! هيا نلعب!' ثم انقله إلى صفحة اللعب.\n"
        "- إذا قال الطفل لا، قل: 'تمام! يمكننا أن نستمر في الحديث فقط.'\n"
        "اجعل الإجابات قصيرة، ممتعة، وبسيطة. إذا طلب الطفل قصة، احكها في جملة واحدة فقط. "
        "لا تستخدم تفسيرات طويلة—اجعلها ممتعة، بسيطة، ومليئة بالحيوية! "
        "وضع إضافي: إذا قال الطفل إنه يريد لعب لعبة تخمين صوت الحيوان، اسأله أولًا إن كان مستعدًا. "
        "إذا قال نعم، اختر حيوانًا عشوائيًا من كلب أو قطة أو بقرة أو خروف، وقلده مثلًا 'هوووف' للكلب، "
        "ثم اسأله: 'أي حيوان يصدر هذا الصوت؟' إذا أجاب صح قل: 'أحسنت! إنه كلب! هل تريد اللعب مرة أخرى؟' "
        "وإذا خطأ قل: 'ممم... هذا ليس صحيحًا، حاول مرة أخرى!' وإذا قال لا في أي وقت، قل: 'حسنًا يا مغامر الصغير! سنعود لصفحة الألعاب.'"
    )
}
current_game_animal = {}
current_game_animal = {}


def generate_response_gpt4(text, lang="auto"):
    try:
        if lang == "auto":
            detected_lang = detect(text)
            lang = "ar" if detected_lang == "ar" else "en"
        system_prompt = system_prompts.get(lang, system_prompts["en"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("=== ERROR in generate_response_gpt4 ===")
        traceback.print_exc()
        return f"Error: {str(e)}"


def generate_response_offline(text, lang="auto"):
    """Generate response using offline methods when API is unavailable"""
    try:
        if lang == "auto":
            # Simple language detection for offline mode
            arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
            lang = "ar" if arabic_chars > len(text) * 0.3 else "en"
        
        # Simple keyword-based responses for offline mode
        responses = {
            "en": {
                "greeting": ["Hello! I'm Nubot!", "Hi there!", "Hey little friend!"],
                "play": ["Let's play a game!", "Games are so much fun!", "What game would you like to play?"],
                "sad": ["I'm here to help you feel better.", "Would you like to talk about it?", "I care about you."],
                "angry": ["I understand you're upset.", "Let's take a deep breath together.", "I'm here to listen."],
                "happy": ["I'm so glad you're happy!", "Your joy makes me happy too!", "That's wonderful!"],
                "story": ["Once upon a time...", "Let me tell you a story!", "Here's a magical tale..."],
                "math": ["Let's do some math together!", "Numbers are fun!", "Ready for some calculations?"],
                "default": ["I'm listening!", "Tell me more!", "That's interesting!"]
            },
            "ar": {
                "greeting": ["مرحباً! أنا نوبوت!", "أهلاً وسهلاً!", "مرحباً يا صديقي الصغير!"],
                "play": ["هيا نلعب لعبة!", "الألعاب ممتعة جداً!", "أي لعبة تريد أن تلعبها؟"],
                "sad": ["أنا هنا لأساعدك تشعر بتحسن.", "هل تريد أن نتحدث عن ذلك؟", "أنا أهتم بك."],
                "angry": ["أفهم أنك منزعج.", "دعنا نأخذ نفساً عميقاً معاً.", "أنا هنا لأستمع إليك."],
                "happy": ["أنا سعيد جداً لأنك سعيد!", "فرحك يجعلني سعيداً أيضاً!", "هذا رائع!"],
                "story": ["كان يا ما كان...", "دعني أحكي لك قصة!", "إليك حكاية سحرية..."],
                "math": ["دعنا نحل مسائل رياضية معاً!", "الأرقام ممتعة!", "مستعد لبعض الحسابات؟"],
                "default": ["أنا أستمع!", "أخبرني المزيد!", "هذا مثير للاهتمام!"]
            }
        }
        
        # Simple keyword matching
        text_lower = text.lower()
        lang_responses = responses.get(lang, responses["en"])
        
        if any(word in text_lower for word in ["hello", "hi", "hey", "مرحبا", "أهلا"]):
            return random.choice(lang_responses["greeting"])
        elif any(word in text_lower for word in ["play", "game", "لعب", "لعبة"]):
            return random.choice(lang_responses["play"])
        elif any(word in text_lower for word in ["sad", "cry", "حزين", "بكاء"]):
            return random.choice(lang_responses["sad"])
        elif any(word in text_lower for word in ["angry", "mad", "غاضب", "منزعج"]):
            return random.choice(lang_responses["angry"])
        elif any(word in text_lower for word in ["happy", "joy", "سعيد", "فرح"]):
            return random.choice(lang_responses["happy"])
        elif any(word in text_lower for word in ["story", "tale", "قصة", "حكاية"]):
            return random.choice(lang_responses["story"])
        elif any(word in text_lower for word in ["math", "number", "رياضيات", "رقم"]):
            return random.choice(lang_responses["math"])
        else:
            return random.choice(lang_responses["default"])
            
    except Exception as e:
        print("=== ERROR in generate_response_offline ===")
        traceback.print_exc()
        return "I'm having trouble understanding. Can you try again?"


def generate_tts_openai(text):
    try:
        os.makedirs("static", exist_ok=True)
        filename = f"response_{int(time.time())}.mp3"
        file_path = os.path.join("static", filename)
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="shimmer",
            input=text
        )
        response.stream_to_file(file_path)
        return filename
    except Exception as e:
        print("=== ERROR in generate_tts_openai ===")
        traceback.print_exc()
        return None


def generate_tts_offline(text, lang="en"):
    """Generate TTS using offline methods (pyttsx3 or espeak)"""
    try:
        os.makedirs("static", exist_ok=True)
        filename = f"response_{int(time.time())}.wav"
        file_path = os.path.join("static", filename)
        
        # Try pyttsx3 first
        try:
            engine = pyttsx3.init()
            
            # Configure voice properties
            voices = engine.getProperty('voices')
            if lang == "ar" and len(voices) > 1:
                # Try to find Arabic voice
                for voice in voices:
                    if 'arabic' in voice.name.lower() or 'ar' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume level
            
            # Save to file
            engine.save_to_file(text, file_path)
            engine.runAndWait()
            return filename
            
        except Exception as pyttsx3_error:
            print(f"pyttsx3 failed: {pyttsx3_error}")
            
            # Fallback to espeak
            try:
                if platform.system() == "Linux":
                    # Use espeak for Linux
                    cmd = f'espeak -s 150 -v {lang} -w "{file_path}" "{text}"'
                    subprocess.run(cmd, shell=True, check=True)
                    return filename
                else:
                    # For Windows/Mac, try espeak if available
                    cmd = f'espeak -s 150 -v {lang} -w "{file_path}" "{text}"'
                    subprocess.run(cmd, shell=True, check=True)
                    return filename
                    
            except Exception as espeak_error:
                print(f"espeak failed: {espeak_error}")
                return None
                
    except Exception as e:
        print("=== ERROR in generate_tts_offline ===")
        traceback.print_exc()
        return None


def generate_tts(text, lang="en", use_offline=False):
    """Main TTS function that chooses between online and offline methods"""
    offline_mode = os.getenv("OFFLINE_MODE", "False").lower() == "true"
    
    if use_offline or offline_mode:
        return generate_tts_offline(text, lang)
    else:
        return generate_tts_openai(text)


# Hardware Control Classes
class LEDController:
    """Controls RGB LED for emotional states"""
    def __init__(self):
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.led_pins = {
            'red': int(os.getenv('LED_PIN_RED', 18)),
            'green': int(os.getenv('LED_PIN_GREEN', 23)),
            'blue': int(os.getenv('LED_PIN_BLUE', 24))
        }
        
        if self.is_raspberry_pi:
            try:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                GPIO.setmode(GPIO.BCM)
                for pin in self.led_pins.values():
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)
            except ImportError:
                print("RPi.GPIO not available - running in simulation mode")
                self.is_raspberry_pi = False
    
    def _detect_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def set_emotion_color(self, emotion):
        """Set LED color based on emotion"""
        colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Blue
            'angry': (255, 0, 0),      # Red
            'surprise': (255, 255, 0), # Yellow
            'playing': (255, 0, 255),  # Magenta
            'neutral': (255, 255, 255) # White
        }
        
        color = colors.get(emotion, colors['neutral'])
        self._set_rgb_color(color)
    
    def _set_rgb_color(self, rgb):
        """Set RGB LED color (r, g, b values 0-255)"""
        if not self.is_raspberry_pi:
            print(f"LED Color: RGB{rgb}")
            return
        
        try:
            # Convert 0-255 to PWM values (0-100)
            r_pwm = int((rgb[0] / 255) * 100)
            g_pwm = int((rgb[1] / 255) * 100)
            b_pwm = int((rgb[2] / 255) * 100)
            
            # Set PWM values
            self.GPIO.output(self.led_pins['red'], r_pwm)
            self.GPIO.output(self.led_pins['green'], g_pwm)
            self.GPIO.output(self.led_pins['blue'], b_pwm)
            
        except Exception as e:
            print(f"LED control error: {e}")
    
    def blink(self, times=3, delay=0.5):
        """Blink LED for notifications"""
        if not self.is_raspberry_pi:
            print(f"LED Blink: {times} times")
            return
        
        try:
            for _ in range(times):
                self._set_rgb_color((255, 255, 255))
                time.sleep(delay)
                self._set_rgb_color((0, 0, 0))
                time.sleep(delay)
        except Exception as e:
            print(f"LED blink error: {e}")


class NotificationSystem:
    """Handles notifications and alerts"""
    def __init__(self):
        self.notifications_file = "notifications.json"
        self.notifications = self._load_notifications()
        self.led_controller = LEDController()
    
    def _load_notifications(self):
        """Load notifications from file"""
        try:
            if os.path.exists(self.notifications_file):
                with open(self.notifications_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading notifications: {e}")
        return []
    
    def _save_notifications(self):
        """Save notifications to file"""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(self.notifications, f, indent=2)
        except Exception as e:
            print(f"Error saving notifications: {e}")
    
    def add_notification(self, emotion, message, severity="medium"):
        """Add a new notification"""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "message": message,
            "severity": severity
        }
        self.notifications.append(notification)
        self._save_notifications()
        
        # Trigger LED notification
        if severity == "high":
            self.led_controller.blink(5, 0.3)
        elif severity == "medium":
            self.led_controller.blink(3, 0.5)
        else:
            self.led_controller.blink(1, 1.0)
    
    def get_recent_notifications(self, limit=10):
        """Get recent notifications"""
        return self.notifications[-limit:] if self.notifications else []


# Initialize hardware controllers
led_controller = LEDController()
notification_system = NotificationSystem()


@app.route('/get_response', methods=['POST'])
def get_response():
    start_time = time.time()  # Start timing
    data = request.get_json()
    print("=== /get_response called ===")
    print("Request data:", data)

    user_text = data.get("text", "").strip()
    lang = data.get("lang", "auto")
    source = data.get("source", "").strip()
    lower_input = user_text.lower()
    user_id = request.remote_addr

    redirect_url = None
    response_text = ""
    video_path = None

    # Guess the Animal game
    if "start" in lower_input and (source == "guess-animal" or "/guess-animal" in (request.referrer or "")):
        animal = random.choice(["dog", "cat", "cow", "sheep"])
        current_game_animal[user_id] = animal
        response_text = "Listen carefully! What animal made that sound?"
        audio_path = f"/static/sounds/{animal}.mp3"
        print("Returning:", response_text, audio_path, redirect_url)
        return jsonify({
            "text": response_text,
            "audio": audio_path
        })
    elif source == "guess-animal" or "/guess-animal" in (request.referrer or ""):
        correct_animal = current_game_animal.get(user_id)
        if correct_animal:
            if correct_animal in lower_input:
                response_text = f"Yay! You’re right, it was a {correct_animal}! Want to play again? Say start."
            else:
                response_text = "Hmm, that's not it. Try again!"
            audio_filename = generate_tts(response_text, lang)
            audio_path = f"/static/{audio_filename}" if audio_filename else None
            print("Returning:", response_text, audio_path, redirect_url)
            return jsonify({
                "text": response_text,
                "audio": audio_path
            })

    # Handle other games or direct intent
    if any(phrase in lower_input for phrase in [
        "let's play guess the animal", "guess the animal", "animal game",
        "play animal", "animal sound", "play guess animal"
    ]):
        redirect_url = "/games/guess-animal"
        response_text = "Yay! Let's play Guess the Animal!"
    elif "tic tac toe" in lower_input or "tic-tac-toe" in lower_input:
        redirect_url = "/games/tic-tac-toe"
        response_text = "Alright! Starting Tic-Tac-Toe!"
    elif "magic math" in lower_input or "math game" in lower_input:
        redirect_url = "/games/magic-math"
        response_text = "Let's do some Magic Math!"
    elif "story spinner" in lower_input or "story game" in lower_input:
        redirect_url = "/games/story-spinner"
        response_text = "Time for a story adventure!"
    elif "animal facts" in lower_input or "facts quiz" in lower_input:
        redirect_url = "/games/animal-facts-quiz"
        response_text = "Get ready for the Animal Facts Quiz!"
    elif "memory echo" in lower_input or "memory game" in lower_input:
        redirect_url = "/games/memory-echo"
        response_text = "Alright! Memory Echo coming up!"
    elif "guess the number" in lower_input or "number game" in lower_input:
        redirect_url = "/games/guess-the-number"
        response_text = "Okay! Let's guess the number!"
    elif any(phrase in lower_input for phrase in ["play", "fun", "game"]):
        redirect_url = "/games"
        response_text = "Wohoo! Welcome to the Games Page! Let's pick a fun game."
    elif any(phrase in lower_input for phrase in ["don't want to play", "no game", "stop playing"]):
        redirect_url = "/"
        response_text = "Okay, back to chatting! Tell me anything."
    else:
        # Try online response first, fallback to offline
        try:
            offline_mode = os.getenv("OFFLINE_MODE", "False").lower() == "true"
            if offline_mode:
                response_text = generate_response_offline(user_text, lang)
            else:
                response_text = generate_response_gpt4(user_text, lang)
        except Exception as e:
            print(f"Online response failed, falling back to offline: {e}")
            response_text = generate_response_offline(user_text, lang)

    # Generate TTS
    tts_start = time.time()
    audio_filename = generate_tts(response_text, lang)
    tts_time = time.time() - tts_start
    
    audio_path = f"/static/{audio_filename}" if audio_filename else None
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Emotion detection and LED control
    detected_emotion = analyze_emotion_from_text(response_text)
    led_controller.set_emotion_color(detected_emotion)
    
    # Add notification if emotion is significant
    if detected_emotion in ['sad', 'angry']:
        notification_system.add_notification(
            detected_emotion, 
            f"Child expressed {detected_emotion} emotion: {user_text[:50]}...",
            severity="high" if detected_emotion == 'angry' else "medium"
        )
    
    # Print timing info to terminal
    print(f"=== TIMING INFO ===")
    print(f"Total response time: {total_time:.2f} seconds")
    print(f"TTS generation time: {tts_time:.2f} seconds")
    print(f"User input: '{user_text}'")
    print(f"Response: '{response_text}'")
    print(f"Detected emotion: {detected_emotion}")
    print(f"Audio file: {audio_filename}")
    print(f"==================")

    return jsonify({
        "text": response_text,
        "audio": audio_path,
        "redirect": redirect_url,
        "emotion": detected_emotion,
        "timing": {
            "total_time": round(total_time, 2),
            "tts_time": round(tts_time, 2)
        }
    })


def analyze_emotion_from_text(text):
    """Analyze emotion from text response"""
    emotions = {
        'happy': ['happy', 'great', 'excited', 'awesome', 'love', 'yay', 'wohoo', 'correct', 'right', 'سعيد', 'ممتاز', 'رائع'],
        'sad': ['sad', 'worried', 'bad', 'sorry', 'حزين', 'قلق', 'أسف'],
        'surprise': ['wow', 'amazing', 'interesting', 'مفاجئ', 'مدهش'],
        'angry': ['angry', 'mad', 'upset', 'غاضب', 'منزعج'],
        'playing': ['play', 'game', 'wait', 'لعب', 'لعبة']
    }
    
    lower_text = text.lower()
    for emotion, keywords in emotions.items():
        if any(keyword in lower_text for keyword in keywords):
            return emotion
    return 'neutral'


# ROUTES
@app.route('/')
def index(): return render_template('index.html')


@app.route('/games')
def games_page(): return render_template('Games Page voice.html')


@app.route('/games/guess-animal')
def guess_animal(): return render_template('guess-animal.html')


@app.route('/games/story-spinner')
def story_spinner(): return render_template('Story Spinner.html')


@app.route('/games/tic-tac-toe')
def tic_tac_toe(): return render_template('tic-tac-toe.html')


@app.route('/games/magic-math')
def magic_math(): return render_template('Magic Math.html')


@app.route('/games/animal-facts-quiz')
def animal_facts_quiz(): return render_template('animal-facts-quiz.html')


@app.route('/games/memory-echo')
def memory_echo(): return render_template('memory-echo.html')


@app.route('/games/guess-the-number')
def guess_number(): return render_template('guess-the-number.html')


@app.route('/favicon.ico')
def favicon(): return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")


# Serve story videos from the project-level 'story' directory
@app.route('/story/<path:filename>')
def story_files(filename):
    return send_from_directory("story", filename)


# API endpoints for system management
@app.route('/api/notifications')
def get_notifications():
    """Get recent notifications"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(notification_system.get_recent_notifications(limit))


@app.route('/api/emotion/<emotion>')
def set_emotion(emotion):
    """Manually set LED emotion color"""
    led_controller.set_emotion_color(emotion)
    return jsonify({"status": "success", "emotion": emotion})


@app.route('/api/status')
def system_status():
    """Get system status information"""
    return jsonify({
        "offline_mode": os.getenv("OFFLINE_MODE", "False").lower() == "true",
        "raspberry_pi": led_controller.is_raspberry_pi,
        "notifications_count": len(notification_system.notifications),
        "led_pins": led_controller.led_pins if led_controller.is_raspberry_pi else "simulation_mode"
    })


@app.route('/api/test-led')
def test_led():
    """Test LED functionality"""
    led_controller.blink(3, 0.5)
    return jsonify({"status": "LED test completed"})


@app.route('/api/offline-mode', methods=['POST'])
def toggle_offline_mode():
    """Toggle offline mode"""
    data = request.get_json()
    offline_mode = data.get('offline', False)
    
    # Update environment variable (this would need to be persisted)
    os.environ['OFFLINE_MODE'] = str(offline_mode)
    
    return jsonify({
        "status": "success", 
        "offline_mode": offline_mode,
        "message": "Offline mode toggled. Restart required for full effect."
    })


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8080)