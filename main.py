from PyQt5.QtCore import Qt, QTimer, QSize, QPoint
from PyQt5.QtGui import QIcon, QPainter, QColor, QBrush, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
import sys
import threading
import datetime
import wikipedia
import pywhatkit
import speech_recognition as sr
import pyttsx3
import requests

API_KEY = "your_openweathermap_api_key_here"

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


def talk(text):
    engine.say(text)
    engine.runAndWait()

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        temp = response['main']['temp']
        desc = response['weather'][0]['description']
        return f"It's {temp} °C with {desc} in {city}."
    except:
        return "Couldn't retrieve weather."

def take_command(callback):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        callback("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        callback(f"You said: {command}")
        return command
    except:
        callback("Sorry, I didn’t understand.")
        return ""

def run_assistant(update_callback):
    command = take_command(update_callback)
    response = ""

    if 'time' in command:
        response = f"The time is {datetime.datetime.now().strftime('%I:%M %p')}."
    elif 'date' in command:
        response = f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
    elif 'weather' in command:
        city = "Mumbai"
        if 'in' in command:
            city = command.split('in')[-1].strip()
        response = get_weather(city)
    elif 'who is' in command:
        person = command.replace('who is', '')
        response = wikipedia.summary(person, sentences=2)
    elif 'search' in command:
        query = command.replace('search', '')
        pywhatkit.search(query)
        response = f"Searching for {query}"
    elif 'open youtube' in command:
        pywhatkit.playonyt("YouTube")
        response = "Opening YouTube"
    elif 'exit' in command or 'stop' in command:
        response = "Goodbye!"
        talk(response)
        sys.exit()
    else:
        response = "Sorry, I can’t do that yet."

    update_callback(response)
    talk(response)

class AssistantBubble(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(220, 220)
        self.move(50, 50)

        self.mic_button = QPushButton(self)
        self.mic_button.setGeometry(85, 85, 50, 50)
        self.mic_button.setStyleSheet("border-radius:25px; background-color:#00ffc3;")
        self.mic_button.setIcon(QIcon("mic.png"))
        self.mic_button.setIconSize(QSize(30, 30))
        self.mic_button.clicked.connect(self.on_mic_click)

        self.status_label = QLabel("Say something...", self)
        self.status_label.setGeometry(30, 150, 160, 20)
        self.status_label.setStyleSheet("color:white; font: 10pt 'Segoe UI';")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_pulse)
        self.radius = 25
        self.grow = True
        self.timer.start(80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(0, 255, 195, 100)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(QPoint(110, 110), self.radius, self.radius)

    def animate_pulse(self):
        if self.grow:
            self.radius += 1
            if self.radius >= 35:
                self.grow = False
        else:
            self.radius -= 1
            if self.radius <= 25:
                self.grow = True
        self.update()

    def on_mic_click(self):
        threading.Thread(target=run_assistant, args=(self.update_status,)).start()

    def update_status(self, text):
        self.status_label.setText(text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    bubble = AssistantBubble()
    bubble.show()
    sys.exit(app.exec_())
