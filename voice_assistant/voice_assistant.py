import os
import sys
import json
import time
import datetime
import webbrowser
import threading
import smtplib
import random
import subprocess
import requests
import speech_recognition as sr
import wikipedia
import psutil
import pyttsx3
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class VoiceAssistant:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.name = self.config.get("assistant_name", "Jarvis")
        self.voice = self.config.get("voice_model", "en-US-ChristopherNeural")
        
        self.offline_engine = pyttsx3.init()
        self.offline_engine.setProperty('rate', 175)
        
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.5
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = False
        self.is_calibrated = False

    def load_config(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                return json.load(file)
        return {"assistant_name": "Jarvis", "custom_commands": {}}

    def speak(self, text):
        print(f"[{self.name}]: {text}")
        
        try:
            cmd = [
                "edge-tts",
                "--text", text,
                "--voice", self.voice
            ]
            
            p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p2 = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-i", "pipe:0"],
                stdin=p1.stdout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            p1.stdout.close()
            p2.communicate()
            
            if p2.returncode != 0:
                raise Exception("Streaming failed")
                
        except Exception:
            self.offline_engine.say(text)
            self.offline_engine.runAndWait()

    def listen(self):
        try:
            with sr.Microphone() as source:
                if not self.is_calibrated:
                    print("[Calibrating microphone background noise...]")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.is_calibrated = True
                
                print("\n[Listening...]")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                print("[Recognizing...]")
                
                query = self.recognizer.recognize_google(audio)
                print(f"[User]: {query}")
                return query.lower()
                
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception:
            print("\n[Mic Inactive — Type command below]")
            query = input("[User Input]: ")
            return query.lower()

    def ask_gemini_ai(self, prompt):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": f"You are {self.name}, a helpful voice assistant. Answer concisely in 1 to 2 conversational sentences without any bullet points or symbols: {prompt}"}]}]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=4)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                clean_text = text.replace("*", "").replace("#", "").replace("-", "").strip()
                return clean_text
        except Exception:
            return None
        return None

    def query_web_knowledge(self, query):
        if any(keyword in query for keyword in ["search", "google", "look up", "find", "on google"]):
            cleaned = query.replace("search google for", "").replace("search for", "").replace("search", "").replace("google", "").replace("on google", "").replace("look up", "").replace("find", "").strip()
            self.speak(f"Searching Google for {cleaned}")
            webbrowser.open(f"https://www.google.com/search?q={cleaned}")
            return True

        ai_response = self.ask_gemini_ai(query)
        if ai_response:
            self.speak(ai_response)
            return True

        if any(q_word in query for q_word in ["who is", "what is", "tell me about", "explain"]):
            cleaned_query = query.replace("tell me about", "").replace("what is", "").replace("who is", "").replace("explain", "").strip()
            if cleaned_query:
                try:
                    summary = wikipedia.summary(cleaned_query, sentences=1)
                    self.speak(f"According to Wikipedia: {summary}")
                    return True
                except Exception:
                    pass

        default_responses = [
            "I'm listening. How can I help you?",
            "I'm here! What would you like to do?",
            "How can I assist you right now?"
        ]
        self.speak(random.choice(default_responses))
        return True

    def get_system_status(self):
        cpu_usage = psutil.cpu_percent(interval=0.2)
        memory = psutil.virtual_memory()
        ram_usage = memory.percent
        status_msg = f"CPU is at {cpu_usage} percent, and RAM utilization is at {ram_usage} percent."
        self.speak(status_msg)

    def get_ip_info(self):
        try:
            res = requests.get('https://api.ipify.org?format=json', timeout=2).json()
            ip_address = res['ip']
            self.speak(f"Your public IP address is {ip_address}")
        except Exception:
            self.speak("Failed to retrieve IP address.")

    def fetch_weather(self, city=None):
        api_key = os.getenv("OPENWEATHER_API_KEY")
        target_city = city or self.config.get("city", "Vadodara")

        url = f"http://api.openweathermap.org/data/2.5/weather?q={target_city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url, timeout=2).json()
            if response.get("cod") == 200:
                temp = response["main"]["temp"]
                desc = response["weather"][0]["description"]
                self.speak(f"Weather in {target_city} is {desc} with {temp} degrees Celsius.")
            else:
                self.speak(f"Could not find weather data for {target_city}.")
        except Exception:
            self.speak("Unable to connect to weather service.")

    def get_time_and_date(self):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d")
        self.speak(f"Today is {date_str}, and the time is {time_str}.")

    def set_reminder(self, duration_seconds, task_name):
        def timer_thread():
            time.sleep(duration_seconds)
            self.speak(f"REMINDER ALERT: {task_name}")

        threading.Thread(target=timer_thread, daemon=True).start()
        self.speak(f"Reminder set for '{task_name}' in {duration_seconds} seconds.")

    def send_email(self, recipient_email, subject, body):
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            self.speak("Email credentials not configured.")
            return

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            self.speak("Email sent successfully!")
        except Exception:
            self.speak("Failed to send email.")

    def parse_intent_and_execute(self, query):
        if not query:
            return True

        clean_query = query.replace("jarvis", "").strip()
        words = clean_query.split()

        shutdown_triggers = ["shutdown", "turn off", "switch off", "go to sleep", "power off", "exit", "quit", "stop", "bye"]
        if any(trigger in query for trigger in shutdown_triggers):
            self.speak("Shutting down system. Have a great day!")
            sys.exit(0)

        elif clean_query in ["hello", "hi", "hey", "hey there", "hello there"] or any(w in words for w in ["hello", "hi", "hey"]):
            greetings = [
                f"Hello! I am {self.name}. How can I help you today?",
                "Hey there! What can I do for you?",
                "Hello! Ready for your commands."
            ]
            self.speak(random.choice(greetings))

        elif "how are you" in query:
            self.speak("I am functioning at full capacity! How are you doing?")

        elif "who are you" in query or "what is your name" in query:
            self.speak(f"I am {self.name}, your voice assistant built in Python.")

        elif "system status" in query or "cpu" in query or "ram" in query:
            self.get_system_status()

        elif "ip address" in query or "my ip" in query:
            self.get_ip_info()

        elif "time" in query or "date" in query:
            self.get_time_and_date()

        elif "weather" in query:
            city_words = query.split()
            if "in" in city_words:
                city = city_words[city_words.index("in") + 1]
                self.fetch_weather(city)
            else:
                self.fetch_weather()

        elif "remind" in query or "reminder" in query:
            self.speak("What should I remind you about?")
            task = self.listen()
            if task:
                self.speak("In how many seconds?")
                sec_str = self.listen()
                try:
                    seconds = int(''.join(filter(str.isdigit, sec_str)))
                    self.set_reminder(seconds, task)
                except ValueError:
                    self.speak("Invalid duration.")

        elif "send email" in query or "send an email" in query:
            self.speak("Who is the recipient email address?")
            recipient = input("Type Recipient Email: ")
            self.speak("What is the subject?")
            subject = self.listen()
            self.speak("What is the message body?")
            body = self.listen()
            if recipient and subject and body:
                self.send_email(recipient, subject, body)

        elif "open" in query and any(cmd in query for cmd in self.config.get("custom_commands", {})):
            for cmd, url in self.config["custom_commands"].items():
                if cmd in query:
                    self.speak(f"Opening {cmd}")
                    webbrowser.open(url)
                    break

        else:
            self.query_web_knowledge(query)

        return True

    def run(self):
        self.speak(f"{self.name} initialized.")
        running = True
        while running:
            query = self.listen()
            running = self.parse_intent_and_execute(query)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()