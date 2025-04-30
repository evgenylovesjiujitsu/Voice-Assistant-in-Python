import speech_recognition as sr
from datetime import datetime
import webbrowser
import os
from gtts import gTTS
from playsound import playsound
import time
import subprocess
import platform
import threading
import random

WAKE_WORD = "бот"  # Activation keyword

# Dictionary of common sites
SITES = {
    "ютуб": "https://youtube.com",
    "youtube": "https://youtube.com",
    "інстаграм": "https://instagram.com",
    "instagram": "https://instagram.com",
    "шахи": "https://www.chess.com/home",
    "chess": "https://www.chess.com/home",
    "гітхаб": "https://github.com/",
    "github": "https://github.com/"
}

# Database of jokes and interesting facts
JOKES_AND_FACTS = [
    "Чому програміст перейшов дорогу? Щоб дістатися до іншого боку!",
    "Знаєте, що кажуть дві функції, коли зустрічаються? Привіт, функція!",
    "Цікавий факт: перший комп'ютерний баг був реальною комахою - молем, що застряг у реле.",
    "Чому комп'ютер погано спить? Бо його постійно турбують баги!",
    "Цікавий факт: перша вебкамера була створена для того, щоб стежити за кавником у Кембриджі.",
    "Як програміст готує каву? while True: brew_coffee()",
    "Цікавий факт: пароль до комп'ютера, що запустив Apollo 11, був '0000'."
]

class Assistant:
    def __init__(self):
        self.active = True
        self.timer = None
        self.joke_interval = 300  # 5 minutes in seconds

    def listen_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Слухаю...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            
        try:
            query = r.recognize_google(audio, language='uk-UA').lower()
            print(f"Ви сказали: {query}")
            return query
        except sr.UnknownValueError:
            print("Не розпізнано команду")
            return ""
        except Exception as e:
            print(f"Помилка: {e}")
            return ""

    def speak(self, text):
        print(f"Бот: {text}")
        tts = gTTS(text=text, lang='uk')
        filename = "bot_response.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)

    def close_browser(self):
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["osascript", "-e", 'tell application "Safari" to close window 1'])
                subprocess.run(["osascript", "-e", 'tell application "Chrome" to close window 1'])
            elif system == "Windows":
                os.system("taskkill /im chrome.exe /f")
                os.system("taskkill /im msedge.exe /f")
            else:  # Linux
                subprocess.run(["pkill", "chrome"])
                subprocess.run(["pkill", "firefox"])
            self.speak("Браузер закрито")
        except Exception as e:
            self.speak("Не вдалося закрити браузер")
            print(f"Помилка: {e}")

    def tell_joke_or_fact(self):
        if self.active:
            joke_or_fact = random.choice(JOKES_AND_FACTS)
            self.speak(joke_or_fact)
            self.start_joke_timer()

    def start_joke_timer(self):
        self.timer = threading.Timer(self.joke_interval, self.tell_joke_or_fact)
        self.timer.start()

    def stop_joke_timer(self):
        if self.timer:
            self.timer.cancel()

    def handle_command(self, command):
        # Time
        if "година" in command or "час" in command or "котра година" in command:
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            
            time_text = f"Зараз {hour} година"
            if minute > 0:
                time_text += f" {minute} хвилин"
            
            self.speak(time_text)
        
        # Opening of sites
        elif "відкрий" in command or "відкрити" in command:
            for site_name, site_url in SITES.items():
                if site_name in command:
                    webbrowser.open(site_url)
                    self.speak(f"Відкриваю {site_name}")
                    return
            
            self.speak("Я не знаю такого сайту. Можу відкрити YouTube чи Instagram")
        
        # Closing the browser
        elif "закрий" in command or "закрити" in command:
            if "браузер" in command or "сайт" in command:
                self.close_browser()
            else:
                for site_name in SITES.keys():
                    if site_name in command:
                        self.close_browser()
                        return
                self.speak("Скажіть 'закрий браузер' або 'закрий сайт'")
        
        # Changing the joke interval
        elif "інтервал" in command or "частота" in command:
            try:
                if "хвилин" in command:
                    minutes = int(command.split()[command.split().index("хвилин")-1])
                    self.joke_interval = minutes * 60
                    self.stop_joke_timer()
                    self.start_joke_timer()
                    self.speak(f"Тепер я розповідатиму жарти кожні {minutes} хвилин")
                elif "секунд" in command:
                    seconds = int(command.split()[command.split().index("секунд")-1])
                    self.joke_interval = seconds
                    self.stop_joke_timer()
                    self.start_joke_timer()
                    self.speak(f"Тепер я розповідатиму жарти кожні {seconds} секунд")
            except:
                self.speak("Не зрозумів новий інтервал. Скажіть наприклад 'бот, зроби інтервал 5 хвилин'")

    def run(self):
        self.speak("Привіт, творцю і хозяіне! Я твоя голосова помічниця Бот. Кажи 'бот' і команду.")
        self.start_joke_timer()  # Starting the joke timer
        
        while self.active:
            text = self.listen_command()
            
            if WAKE_WORD in text:
                command = text.split(WAKE_WORD)[-1].strip()
                self.handle_command(command)
            elif text:
                print("Скажіть 'бот' перед командою")

if __name__ == "__main__":
    assistant = Assistant()
    try:
        assistant.run()
    except KeyboardInterrupt:
        assistant.stop_joke_timer()
        assistant.speak("До побачення!")
        print("\nБот вимкнений")
