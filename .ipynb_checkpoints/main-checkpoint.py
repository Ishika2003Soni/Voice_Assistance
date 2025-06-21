import streamlit as st
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import wikipedia
import threading

# Initialize the speech recognition and text-to-speech engines
@st.cache_resource
def initialize_engines():
    recognizer = sr.Recognizer()
    tts_engine = pyttsx3.init()

    voices = tts_engine.getProperty('voices')
    if voices:
        tts_engine.setProperty('voice', voices[0].id)
    tts_engine.setProperty('rate', 150)
    tts_engine.setProperty('volume', 0.9)

    return recognizer, tts_engine

def speak_text(text, tts_engine):
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        st.error(f"TTS Error: {e}")

def listen_for_speech(recognizer, timeout=5):
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
        st.info("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        return text.lower()
    except sr.WaitTimeoutError:
        return "timeout"
    except sr.UnknownValueError:
        return "unknown"
    except sr.RequestError as e:
        return f"error: {e}"
    except Exception as e:
        return f"error: {e}"

def get_weather_info(city="Delhi"):
    return f"The weather in {city} is sunny with a temperature of 25°C"

def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found. Be more specific. Options: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find information about that topic."
    except:
        return "An error occurred while searching."

def open_application(app_name):
    try:
        apps = {
            "notepad": "notepad", "calculator": "calc", "paint": "mspaint", "edge": "start msedge",
            "chrome": "start chrome", "firefox": "start firefox", "word": "start winword",
            "excel": "start excel", "powerpoint": "start powerpnt", "outlook": "start outlook",
            "file explorer": "explorer", "command prompt": "start cmd", "powershell": "start powershell",
            "task manager": "taskmgr", "control panel": "control", "settings": "start ms-settings:",
            "music": "start wmplayer", "photos": "start ms-photos:", "camera": "start microsoft.windows.camera:",
            "maps": "start bingmaps:", "calendar": "start outlookcal:", "mail": "start outlookmail:",
            "store": "start ms-windows-store:", "skype": "start skype:", "teams": "start msteams:",
            "discord": "start discord:", "spotify": "start spotify:", "steam": "start steam:",
            "netflix": "start netflix:", "vlc": "start vlc", "obs": "start obs64", "zoom": "start zoom:"
        }
        os.system(apps[app_name])
        return f"Opening {app_name.capitalize()}"
    except:
        return f"I couldn't open {app_name}."

def process_command(command, tts_engine):
    command = command.lower().strip()

    if any(word in command for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I help you today?"
    elif "time" in command:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "date" in command or "today" in command:
        return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
    elif "weather" in command and 'open' not in command:
        city = "Delhi"
        if 'in' in command:
            city = command.split('in')[-1].strip()
        return get_weather_info(city)
    elif any(w in command for w in ['search', 'wikipedia', 'tell me about', 'what is']) and 'open' not in command:
        for term in ['search for', 'search', 'wikipedia', 'tell me about', 'what is', 'who is']:
            if term in command:
                query = command.split(term)[-1].strip()
                return search_wikipedia(query)
        return "What would you like me to search for?"
    elif 'open' in command:
        for keyword, url in {
            'youtube': "https://www.youtube.com", 'google': "https://www.google.com",
            'github': "https://www.github.com", 'facebook': "https://www.facebook.com",
            'twitter': "https://www.twitter.com", 'instagram': "https://www.instagram.com",
            'linkedin': "https://www.linkedin.com", 'gmail': "https://www.gmail.com",
            'whatsapp': "https://web.whatsapp.com"
        }.items():
            if keyword in command:
                webbrowser.open(url)
                return f"Opening {keyword.capitalize()}"
        for app in [
            'notepad', 'calculator', 'paint', 'edge', 'chrome', 'firefox', 'word', 'excel', 'powerpoint',
            'outlook', 'file explorer', 'command prompt', 'powershell', 'task manager', 'control panel',
            'settings', 'music', 'photos', 'camera', 'maps', 'calendar', 'mail', 'store', 'skype', 'teams',
            'discord', 'spotify', 'steam', 'netflix', 'vlc', 'obs', 'zoom']:
            if app in command:
                return open_application(app)
        return "I can open apps like Notepad, Word, or websites like YouTube. Try again!"
    elif "lock screen" in command:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        return "Locking the screen"
    elif "volume up" in command:
        os.system('powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]175)"')
        return "Increasing volume"
    elif "volume down" in command:
        os.system('powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]174)"')
        return "Decreasing volume"
    elif "mute" in command:
        os.system('powershell -c "(New-Object -comObject WScript.Shell).SendKeys([char]173)"')
        return "Toggling mute"
    elif any(x in command for x in ['plus', 'minus', 'multiply', 'divide', 'calculate']):
        try:
            nums = [int(s) for s in command.split() if s.isdigit()]
            if 'plus' in command:
                return f"The result is {sum(nums)}"
            elif 'minus' in command:
                return f"The result is {nums[0] - nums[1]}"
            elif 'multiply' in command or 'times' in command:
                return f"The result is {nums[0] * nums[1]}"
            elif 'divide' in command:
                return f"The result is {nums[0] / nums[1]}" if nums[1] != 0 else "Cannot divide by zero."
        except:
            return "I couldn't understand the math expression."
    elif any(x in command for x in ['bye', 'exit', 'quit']):
        return "Goodbye! Have a nice day!"
    else:
        return "Sorry, I didn't understand. Try commands like 'open notepad' or 'what's the weather'."

def main():
    st.set_page_config(page_title="🎤 Voice Assistant", layout="wide")

    st.markdown("""
    <style>
    .main-header {text-align: center; color: #1f77b4; margin-bottom: 30px;}
    .user-message {background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;}
    .assistant-message {background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-header'>🎤 Voice Assistant</h1>", unsafe_allow_html=True)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'is_listening' not in st.session_state:
        st.session_state.is_listening = False

    recognizer, tts_engine = initialize_engines()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💬 Conversation")
        for user, assistant in st.session_state.chat_history:
            st.markdown(f"<div class='user-message'><strong>You:</strong> {user}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='assistant-message'><strong>Assistant:</strong> {assistant}</div>", unsafe_allow_html=True)

        st.subheader("⌨️ Type your command")
        text_input = st.text_input("Enter your command:")
        if st.button("📤 Send Text Command"):
            if text_input:
                response = process_command(text_input, tts_engine)
                st.session_state.chat_history.append((text_input, response))
                threading.Thread(target=speak_text, args=(response, tts_engine), daemon=True).start()
                st.rerun()

        st.subheader("📂 Or choose a command")
        all_commands = [
            'What time is it?', "What's the date?", "What's the weather?", "Search for India", "Tell me about Python",
            "Calculate 5 plus 3", "Multiply 4 times 6", "Subtract 10 minus 3", "Divide 20 by 4",
            'Open Notepad', 'Open Calculator', 'Open Paint', 'Open Edge', 'Open Chrome', 'Open Word', 'Open Excel',
            'Open PowerPoint', 'Open Outlook', 'Open File Explorer', 'Open Command Prompt', 'Open Task Manager',
            'Open Settings', 'Open Photos', 'Open Camera', 'Open Maps', 'Open Spotify', 'Open Discord', 'Open Teams',
            'Open YouTube', 'Open Google', 'Open GitHub', 'Open Facebook', 'Open Instagram', 'Open Gmail',
            'Open WhatsApp', 'Open LinkedIn', 'Lock Screen', 'Volume Up', 'Volume Down', 'Mute', 'Open Control Panel',
            'Hello', 'Goodbye'
        ]
        selected_command = st.selectbox("👇 Choose from all available commands:", [""] + all_commands)
        if selected_command and st.button("🚀 Run Selected Command"):
            response = process_command(selected_command, tts_engine)
            st.session_state.chat_history.append((selected_command, response))
            threading.Thread(target=speak_text, args=(response, tts_engine), daemon=True).start()
            st.rerun()

    with col2:
        st.subheader("🎙️ Voice Controls")
        if st.button("🎤 Start Listening", disabled=st.session_state.is_listening):
            st.session_state.is_listening = True
            speech_text = listen_for_speech(recognizer)
            if speech_text == "timeout":
                st.warning("⏰ Listening timeout.")
            elif speech_text == "unknown":
                st.warning("❓ Couldn't understand.")
            elif speech_text.startswith("error"):
                st.error(speech_text)
            else:
                st.success(f"📝 You said: {speech_text}")
                response = process_command(speech_text, tts_engine)
                st.session_state.chat_history.append((speech_text, response))
                threading.Thread(target=speak_text, args=(response, tts_engine), daemon=True).start()
                st.rerun()
            st.session_state.is_listening = False

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()
