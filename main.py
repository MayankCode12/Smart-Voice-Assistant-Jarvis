import os
import eel

from engine.features import playAssistantSound
from engine.command import allCommands

# ✅ Initialize Eel with the frontend folder
eel.init("www")

# ✅ The function that starts everything
def start():
    try:
        # 1. Play assistant startup sound
        playAssistantSound()

        # 2. Open Edge browser in app mode
        os.system('start msedge.exe --app="http://localhost:8000/index.html"')

        # 3. Start the Eel web app
        eel.start('index.html', mode=None, host='localhost', port=8000, block=True)

    except Exception as e:
        print(f"[ERROR] Failed to start Jarvis: {e}")
