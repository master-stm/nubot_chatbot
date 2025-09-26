# 🤖 Nubot - Interactive Child-Friendly Robot

Nubot is an interactive voice-controlled robot designed for children, featuring speech recognition, text-to-speech, emotion detection, and educational games. The system supports both online and offline operation and is optimized for Raspberry Pi deployment.

## ✨ Features

### Core Functionality
- **Voice Recognition**: Real-time speech-to-text in English and Arabic
- **Text-to-Speech**: High-quality voice responses with offline fallback
- **Emotion Detection**: Analyzes emotional tone and responds accordingly
- **Multilingual Support**: Full English and Arabic language support
- **LED Control**: RGB LED indicators for emotional states (Raspberry Pi)

### Educational Games
- 🎵 **Guess the Animal Sound**: Audio-based animal recognition
- ⭕ **Tic-Tac-Toe**: Voice-controlled strategy game
- 🧮 **Magic Math**: Interactive math problems
- 📚 **Story Spinner**: Random story generation
- 🧠 **Memory Echo**: Memory training game
- 🐾 **Animal Facts Quiz**: Educational trivia
- 🔢 **Guess the Number**: Number guessing game

### Hardware Integration
- **Raspberry Pi Support**: Full GPIO control for LEDs and sensors
- **Offline Mode**: Works without internet connection
- **Notification System**: Alerts for emotional triggers
- **Audio Processing**: Real-time audio capture and playback

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Microphone and speakers
- (Optional) Raspberry Pi 4/5 with GPIO accessories

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nubot_chatbot
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Configure environment**
   ```bash
   # Edit .env file with your API keys
   nano .env
   ```

4. **Test the system**
   ```bash
   python test_system.py
   ```

5. **Start the server**
   ```bash
   python app.py
   ```

## 📋 Manual Installation

### System Dependencies

#### Ubuntu/Debian (including Raspberry Pi)
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv espeak espeak-data
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y libasound2-dev git
```

#### macOS
```bash
brew install espeak portaudio
```

#### Windows
- Install espeak manually from [espeak website](http://espeak.sourceforge.net/)
- Install Visual Studio Build Tools for Python packages

### Python Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=8080

# Hardware Configuration (Raspberry Pi)
LED_PIN_RED=18
LED_PIN_GREEN=23
LED_PIN_BLUE=24
BUZZER_PIN=25

# Audio Configuration
DEFAULT_VOICE=en
OFFLINE_MODE=False
AUDIO_SAMPLE_RATE=22050

# Game Configuration
MAX_GAME_LEVELS=5
DEFAULT_LANGUAGE=en

# Emotion Detection
EMOTION_SENSITIVITY=0.7
NOTIFICATION_ENABLED=True
```

### Hardware Setup (Raspberry Pi)

#### Required Components
- Raspberry Pi 4/5
- MicroSD card (32GB+)
- USB microphone
- Speaker or 3.5mm audio output
- RGB LED (common cathode)
- Resistors (220Ω x 3)
- Breadboard and jumper wires

#### Wiring Diagram
```
Raspberry Pi GPIO:
- Pin 18 (GPIO 24) → Red LED (220Ω resistor)
- Pin 23 (GPIO 16) → Green LED (220Ω resistor)  
- Pin 24 (GPIO 18) → Blue LED (220Ω resistor)
- Ground → LED common cathode
```

## 🎮 Usage

### Starting the System
```bash
# Method 1: Direct Python
python app.py

# Method 2: Using startup script
./start_nubot.sh  # Linux/macOS
start_nubot.bat   # Windows
```

### Web Interface
1. Open browser to `http://localhost:8080`
2. Allow microphone permissions
3. Start speaking to Nubot
4. Use language toggle (AR/EN) for Arabic support

### Voice Commands
- **"Hello Nubot"** - Basic greeting
- **"I want to play a game"** - Access games menu
- **"I'm feeling sad"** - Emotional support
- **"Tell me a story"** - Story spinner
- **"Let's do math"** - Magic math game

### Game Controls
- **"Start"** - Begin any game
- **"Go back"** - Return to main menu
- **"Yes/No"** - Answer prompts
- **"I give up"** - End current game

## 🔧 API Endpoints

### Core Endpoints
- `POST /get_response` - Main voice interaction
- `GET /api/status` - System status
- `GET /api/notifications` - Recent notifications
- `GET /api/test-led` - Test LED functionality

### Game Endpoints
- `GET /games` - Games menu
- `GET /games/guess-animal` - Animal sound game
- `GET /games/tic-tac-toe` - Tic-tac-toe game
- `GET /games/magic-math` - Math game
- `GET /games/story-spinner` - Story game
- `GET /games/animal-facts-quiz` - Quiz game
- `GET /games/memory-echo` - Memory game
- `GET /games/guess-the-number` - Number game

### Management Endpoints
- `POST /api/offline-mode` - Toggle offline mode
- `GET /api/emotion/<emotion>` - Set LED emotion

## 🧪 Testing

### Run System Tests
```bash
python test_system.py
```

### Test Individual Components
```bash
# Test server connection
curl http://localhost:8080/api/status

# Test voice response
curl -X POST http://localhost:8080/get_response \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello Nubot", "lang": "en"}'

# Test LED control
curl http://localhost:8080/api/test-led
```

## 🔧 Troubleshooting

### Common Issues

#### Audio Problems
```bash
# Check audio devices
arecord -l  # List recording devices
aplay -l   # List playback devices

# Test microphone
arecord -f cd -d 5 test.wav
aplay test.wav
```

#### Permission Issues (Raspberry Pi)
```bash
# Add user to audio and gpio groups
sudo usermod -a -G audio $USER
sudo usermod -a -G gpio $USER
# Logout and login again
```

#### Python Package Issues
```bash
# Reinstall problematic packages
pip uninstall pyaudio
pip install pyaudio

# For Raspberry Pi
sudo apt install portaudio19-dev
pip install pyaudio
```

#### GPIO Issues
```bash
# Check GPIO permissions
ls -l /dev/gpiomem
sudo chmod 666 /dev/gpiomem
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_DEBUG=True
python app.py
```

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 1.2 GHz ARM or x86
- **RAM**: 1GB
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows 10+

### Recommended (Raspberry Pi)
- **Model**: Raspberry Pi 4B (4GB+)
- **OS**: Raspberry Pi OS (64-bit)
- **Storage**: 32GB+ microSD card
- **Audio**: USB microphone + speaker

### Performance Notes
- **Online Mode**: Requires stable internet connection
- **Offline Mode**: Uses local TTS (espeak/pyttsx3)
- **Memory Usage**: ~200MB base, +100MB per game session
- **CPU Usage**: 10-30% during voice processing

## 🔒 Security Considerations

### API Keys
- Store API keys in `.env` file (never commit to version control)
- Use environment variables in production
- Rotate keys regularly

### Network Security
- Run on local network only in production
- Use HTTPS for external access
- Implement authentication for admin endpoints

### Data Privacy
- Voice data is processed locally when possible
- OpenAI API calls are logged (check their privacy policy)
- No personal data is permanently stored

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_system.py`
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions
- Include tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 and TTS APIs
- Raspberry Pi Foundation for hardware platform
- espeak project for offline TTS
- Flask community for web framework
- All contributors and testers

## 📞 Support

### Getting Help
- Check the troubleshooting section above
- Review test results: `test_results.json`
- Check logs in the terminal output
- Open an issue on GitHub

### Reporting Bugs
When reporting bugs, please include:
- System information (OS, Python version)
- Error messages and logs
- Steps to reproduce
- Expected vs actual behavior

---

**Made with ❤️ for children's education and entertainment**
