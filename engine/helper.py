# engine/helper.py

import re
import subprocess
import time
import pyautogui
import sqlite3
from urllib.parse import quote

from engine.config import ASSISTANT_NAME
from engine.speech import speak

def extract_yt_term(command):
    pattern1 = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern1, command, re.IGNORECASE)
    if match:
        return match.group(1)

    pattern2 = r'play\s+(.*)'
    match = re.search(pattern2, command, re.IGNORECASE)
    if match:
        return match.group(1)

    return None

def remove_words(input_string, words_to_remove):
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    return ' '.join(filtered_words)

def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        conn = sqlite3.connect("jarvis.db")
        cursor = conn.cursor()
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
                       ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        conn.close()

        if results:
            mobile_number_str = str(results[0][0])
            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str
            return mobile_number_str, query
        else:
            speak('Not found in contacts')
            return 0, 0
    except Exception as e:
        print("[DB ERROR]", e)
        speak('There was an error accessing the contacts')
        return 0, 0

def whatsApp(mobile_no, message, flag, name):
    if flag == 'message':
        target_tab = 12
        jarvis_message = "Message sent successfully to " + name
    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "Calling " + name
    else:
        target_tab = 6
        message = ''
        jarvis_message = "Starting video call with " + name

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)

    pyautogui.hotkey('ctrl', 'f')
    for _ in range(1, target_tab):
        pyautogui.hotkey('tab')
    pyautogui.hotkey('enter')

    speak(jarvis_message)
