import os
import re
import sqlite3
import struct
import time
import webbrowser
import eel
import pvporcupine
import pyaudio
import pywhatkit as kit
from playsound import playsound
import pyautogui as autogui

from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assests\\audio\\www_assets_audio_start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    app_name = query.lower().strip()

    if app_name == "":
        speak("Sorry, I didn't understand what to open.")
        return

    try:
        cursor.execute('SELECT path FROM sys_command WHERE name = ?', (app_name,))
        result = cursor.fetchone()
        if result:
            speak(f"Opening {app_name}")
            os.startfile(result[0])
            return

        cursor.execute('SELECT url FROM web_command WHERE name = ?', (app_name,))
        result = cursor.fetchone()
        if result:
            speak(f"Opening {app_name}")
            webbrowser.open(result[0])
            return

        speak(f"Trying to open {app_name}")
        os.system(f'start {app_name}')

    except Exception as e:
        print(f"[ERROR] Failed to open {app_name}: {e}")
        speak("Something went wrong.")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak(f"Playing {search_term} on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't understand what to play.")

def hotword():
    porcupine = None
    paud = None
    audio_stream = None

    try:
        # Use the pre-trained "jarvis" and "alexa" hotwords
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"])
        paud = pyaudio.PyAudio()

        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("[INFO] Listening for hotword...")

        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("[HOTWORD DETECTED] JARVIS TRIGGERED")
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")

    except Exception as e:
        print(f"[HOTWORD ERROR] {e}")

    finally:
        if porcupine: porcupine.delete()
        if audio_stream: audio_stream.close()
        if paud: paud.terminate()
