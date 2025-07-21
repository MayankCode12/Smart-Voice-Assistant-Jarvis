import speech_recognition as sr
import eel
import time
import wikipedia
import sqlite3
from datetime import datetime
import requests

from engine.helper import remove_words, findContact, whatsApp
from engine.config import ASSISTANT_NAME
from engine.speech import speak

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplayMessage('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 6)
    try:
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        eel.DisplayMessage(query)
        time.sleep(1)
    except Exception:
        print("Sorry, I didn't catch that.")
        return ""
    return query.lower()

def get_contact_number_by_name(name):
    try:
        conn = sqlite3.connect("jarvis.db")
        cursor = conn.cursor()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
                       ('%' + name + '%', name + '%'))
        results = cursor.fetchall()
        conn.close()
        return results[0][0] if results else "not found"
    except Exception as e:
        print(f"[ERROR] Contact lookup failed: {e}")
        return "not found"

def search_wikipedia(term):
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(term, sentences=2)
        return summary
    except Exception as e:
        print(f"[WIKI ERROR] {e}")
        return "Sorry, I couldn't find anything on Wikipedia."

def get_time():
    now = datetime.now()
    return now.strftime("%I:%M %p")

def get_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()
        return f"{joke['setup']}... {joke['punchline']}"
    except Exception as e:
        print(f"[JOKE ERROR] {e}")
        return "Sorry, I couldn't fetch a joke."

@eel.expose
def allCommands(message=1):
    if message == 1:
        while True:
            query = takecommand()
            print(query)

            try:
                if query in ["exit", "quit", "stop", "shutdown"]:
                    speak("Okay, shutting down.")
                    break

                if query.strip() == "":
                    speak("I didn't catch that. Listening again.")
                    continue

                if "open" in query:
                    from engine.features import openCommand
                    openCommand(query)

                elif "on youtube" in query:
                    from engine.features import PlayYoutube
                    PlayYoutube(query)

                elif "call" in query or "phone" in query or "contact" in query:
                    words_to_remove = ['make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'contact', '']
                    name = remove_words(query, words_to_remove)
                    number = get_contact_number_by_name(name)
                    speak(f"The number for {name} is {number}")

                elif "send message" in query or "phone call" in query or "video call" in query:
                    message = ""
                    contact_no, name = findContact(query)

                    if contact_no != 0:
                        if "send message" in query:
                            message = 'message'
                            speak("What message should I send?")
                            query = takecommand()
                        elif "phone call" in query:
                            message = 'call'
                        else:
                            message = 'video call'
                        whatsApp(contact_no, query, message, name)

                elif "wikipedia" in query or "who is" in query or "what is" in query:
                    cleaned = query.replace("search", "").replace("on", "").replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
                    result = search_wikipedia(cleaned)
                    speak(result)

                elif "what is the time" in query:
                    current_time = get_time()
                    speak(f"The current time is {current_time}")

                elif "tell me a joke" in query:
                    joke = get_joke()
                    speak(joke)

                else:
                    speak("Sorry, I don't understand that yet.")

            except Exception as e:
                print("error:", e)
                eel.ShowHood()
