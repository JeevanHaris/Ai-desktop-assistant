import speech_recognition
import pyttsx3
import os
import datetime
import webbrowser
import time
import tkinter as tk
from threading import Thread
import requests
import json

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1.0)  # Volume 0-1

# Recognizer instance
recognizer = speech_recognition.Recognizer()

# GUI window setup
root = tk.Tk()
root.title("AI Assistant for Visually Impaired with ChatGPT")
root.geometry("600x400")
root.configure(bg="black")

output_label = tk.Label(root, text="Welcome to the Enhanced AI Assistant!", 
                       fg="white", bg="black", wraplength=500, font=("Arial", 14))
output_label.pack(pady=20)

# Conversation history for context
conversation_history = []

# ChatGPT Integration (replace with your preferred AI service)
def get_ai_response(user_input):
    """
    Replace this function with your preferred AI service integration.
    Options:
    1. OpenAI GPT API (requires API key)
    2. Hugging Face Transformers (local models)
    3. Google Bard API
    4. Anthropic Claude API
    5. Local LLM like Ollama
    """
    
    # Example 1: OpenAI GPT API (uncomment and add your API key)
    """
    import openai
    openai.api_key = "your-api-key-here"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for visually impaired users. Provide clear, concise responses."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't process that request. Error: {str(e)}"
    """
    
    # Example 2: Local AI using Ollama (requires Ollama to be installed)
    """
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   'model': 'llama2',
                                   'prompt': user_input,
                                   'stream': False
                               })
        if response.status_code == 200:
            return response.json()['response']
        else:
            return "Sorry, I couldn't connect to the local AI service."
    except Exception as e:
        return f"Sorry, there was an error: {str(e)}"
    """
    
    # Example 3: Hugging Face API (free tier available)
    """
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_TOKEN"}
    
    try:
        response = requests.post(API_URL, 
                               headers=headers, 
                               json={"inputs": user_input})
        result = response.json()
        return result[0]['generated_text'] if result else "Sorry, no response generated."
    except Exception as e:
        return f"Sorry, there was an error: {str(e)}"
    """
    
    # Placeholder response (replace with actual AI integration)
    responses = {
        "hello": "Hello! I'm your AI assistant. How can I help you today?",
        "how are you": "I'm doing well, thank you for asking! I'm here to help you with anything you need.",
        "what can you do": "I can help you with time, date, opening applications, reading files, searching the web, setting reminders, and having conversations. I can also answer questions and provide information on various topics.",
        "thank you": "You're very welcome! I'm happy to help.",
        "goodbye": "Goodbye! Have a wonderful day!",
    }
    
    # Simple keyword matching (replace with actual AI)
    user_lower = user_input.lower()
    for keyword, response in responses.items():
        if keyword in user_lower:
            return response
    
    return "I'm still learning! Could you try rephrasing your question, or ask me about time, date, or to open an application?"

# Speak Function
def speak(text):
    output_label.config(text=text)
    engine.say(text)
    engine.runAndWait()

# Listen Function
def listen():
    with speech_recognition.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        speak("Listening...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")  # For debugging
        return command.lower()
    except speech_recognition.UnknownValueError:
        speak("Sorry, I didn't catch that. Please repeat.")
        return ""
    except speech_recognition.RequestError:
        speak("Speech recognition service is down.")
        return ""
    except speech_recognition.WaitTimeoutError:
        speak("No input detected. Say something!")
        return ""

# Enhanced Command Handler with AI Integration
def handle_command(command):
    # Add to conversation history
    conversation_history.append({"role": "user", "content": command})
    
    # Check for specific system commands first
    if 'time' in command and ('current' in command or 'what' in command):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {current_time}."
        speak(response)
        
    elif 'date' in command and ('today' in command or 'current' in command or 'what' in command):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        response = f"Today is {today}."
        speak(response)
        
    elif 'open notepad' in command:
        os.system("notepad")
        response = "Opening Notepad."
        speak(response)
        
    elif 'open calculator' in command:
        os.system("calc")
        response = "Opening Calculator."
        speak(response)
        
    elif 'read file' in command:
        speak("Please say the file name with extension.")
        filename = listen()
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    content = file.read()
                    speak("Reading file.")
                    # Read first 500 characters to avoid too long speech
                    speak(content[:500])
                    if len(content) > 500:
                        speak("File is longer. Would you like me to continue reading?")
            except Exception as e:
                speak(f"Error reading file: {str(e)}")
        else:
            speak("File not found or no filename provided.")
            
    elif 'search' in command or 'google' in command:
        speak("What should I search for?")
        query = listen()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching for {query} on Google.")
        else:
            speak("No search query provided.")
            
    elif 'weather' in command:
        webbrowser.open("https://www.google.com/search?q=weather")
        speak("Opening weather report.")
        
    elif 'news' in command:
        webbrowser.open("https://news.google.com")
        speak("Here are the latest news headlines.")
        
    elif 'set reminder' in command:
        speak("What is the reminder?")
        reminder = listen()
        if reminder:
            speak("In how many seconds should I remind you?")
            time_input = listen()
            try:
                seconds = int(''.join(filter(str.isdigit, time_input)))
                if seconds > 0:
                    speak(f"Reminder set for {seconds} seconds from now.")
                    
                    def reminder_thread():
                        time.sleep(seconds)
                        speak(f"Reminder: {reminder}")
                    
                    Thread(target=reminder_thread, daemon=True).start()
                else:
                    speak("Please provide a valid number of seconds.")
            except (ValueError, TypeError):
                speak("Invalid time input. Please provide a number.")
        else:
            speak("No reminder text provided.")
            
    elif 'exit' in command or 'quit' in command or 'stop' in command:
        speak("Goodbye! Have a nice day.")
        root.quit()
        
    elif 'help' in command or 'commands' in command:
        help_text = """I can help you with:
        - Telling time and date
        - Opening applications like Notepad and Calculator
        - Reading files
        - Searching on Google
        - Checking weather and news
        - Setting reminders
        - Having conversations and answering questions
        Just speak naturally to me!"""
        speak(help_text)
        
    else:
        # Use AI for general conversation
        try:
            ai_response = get_ai_response(command)
            conversation_history.append({"role": "assistant", "content": ai_response})
            speak(ai_response)
        except Exception as e:
            speak("Sorry, I encountered an error processing your request. Please try again.")
            print(f"Error: {e}")

# Thread function to avoid GUI freeze
def assistant_loop():
    speak("Hello! I am your enhanced AI assistant with conversational abilities. How can I help you?")
    
    while True:
        try:
            command = listen()
            if command:
                handle_command(command)
            time.sleep(0.5)  # Small delay to prevent overwhelming the system
        except KeyboardInterrupt:
            speak("Assistant stopped.")
            break
        except Exception as e:
            print(f"Error in assistant loop: {e}")
            speak("Sorry, I encountered an error. Let me try again.")
            time.sleep(1)

# Add some keyboard shortcuts
def on_key_press(event):
    if event.keysym == 'space':
        # Space bar to manually trigger listening
        Thread(target=lambda: handle_command(listen()), daemon=True).start()
    elif event.keysym == 'Escape':
        # Escape to quit
        speak("Goodbye!")
        root.quit()

root.bind('<KeyPress>', on_key_press)
root.focus_set()  # Make sure window can receive key events

# Add instructions to the GUI
instructions = tk.Label(root, 
                       text="Press SPACE to speak manually • Press ESC to exit\nSpeak naturally for conversations!", 
                       fg="yellow", bg="black", font=("Arial", 10))
instructions.pack(pady=10)

# Start assistant in a separate thread
Thread(target=assistant_loop, daemon=True).start()

# Run GUI
root.mainloop()
