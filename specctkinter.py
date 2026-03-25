import speech_recognition
import pyttsx3
import os
import datetime
import webbrowser
import time
import tkinter as tk
from threading import Thread

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume 0-1

# Recognizer instance
recognizer = speech_recognition.Recognizer()

# GUI window setup
root = tk.Tk()
root.title("AI Assistant for Visually Impaired")
root.geometry("500x300")
root.configure(bg="black")

output_label = tk.Label(root, text="Welcome to the AI Assistant!", fg="white", bg="black", wraplength=400, font=("Arial", 14))
output_label.pack(pady=20)

# Speak Function
def speak(text):
    output_label.config(text=text)
    engine.say(text)
    engine.runAndWait()

# Listen Function
def listen():
    with speech_recognition.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        return command.lower()
    except speech_recognition.UnknownValueError:
        speak("Sorry, I didn't catch that. Please repeat.")
        return ""
    except speech_recognition.RequestError:
        speak("Speech recognition service is down.")
        return ""

# Command Handler
def handle_command(command):
    if 'time' in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")

    elif 'date' in command:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today}.")

    elif 'open notepad' in command:
        os.system("notepad")
        speak("Opening Notepad.")

    elif 'open calculator' in command:
        os.system("calc")
        speak("Opening Calculator.")

    elif 'read file' in command:
        speak("Please say the file name with extension.")
        filename = listen()
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                content = file.read()
                speak("Reading file.")
                speak(content[:500])  # Read first 500 chars
        else:
            speak("File not found.")

    elif 'search' in command:
        speak("What should I search for?")
        query = listen()
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        speak(f"Searching for {query} on Google.")

    elif 'weather' in command:
        webbrowser.open("https://www.google.com/search?q=weather")
        speak("Opening weather report.")

    elif 'news' in command:
        webbrowser.open("https://news.google.com")
        speak("Here are the latest news headlines.")

    elif 'set reminder' in command:
        speak("What is the reminder?")
        reminder = listen()
        speak("In how many seconds should I remind you?")
        try:
            seconds = int(listen())
            speak(f"Reminder set for {seconds} seconds from now.")
            time.sleep(seconds)
            speak(f"Reminder: {reminder}")
        except ValueError:
            speak("Invalid time input.")

    elif 'exit' in command or 'quit' in command:
        speak("Goodbye! Have a nice day.")
        root.quit()

    else:
        speak("I didn't understand the command.")

# Thread function to avoid GUI freeze
def assistant_loop():
    speak("Hello! I am your AI assistant. How can I help you?")
    while True:
        command = listen()
        if command:
            handle_command(command)

# Start assistant in a separate thread
Thread(target=assistant_loop, daemon=True).start()

# Run GUI
root.mainloop()
