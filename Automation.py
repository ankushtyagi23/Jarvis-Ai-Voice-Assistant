from AppOpener import close, open as appopen
from webbrowser import open as webopen
from fake_useragent import UserAgent
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import time


# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt for AI assistant
SystemChatBot = [{"role": "system", "content": "You're an AI content writer. Generate letters, code, applications, essays, notes, songs, and poems."}]
messages = []

# Google Search Function
def GoogleSearch(topic):
    search(topic)
    return True

# AI Content Writer Function with API Retry
def ContentWriterAI(prompt):
    messages.append({"role": "user", "content": f"{prompt}"})
    
    for attempt in range(3):  # Retry 3 times
        try:
            completion = client.chat.completions.create(
                model="allam-2-7b",  # ✅ Use a working model
                messages=SystemChatBot + messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=False
            )
            answer = completion.choices[0].message.content
            messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            print(f"❌ Error: {e} | Retrying {attempt + 1}/3...")
            time.sleep(2)  # Wait before retrying
    return "Error: AI service unavailable."


# Create and Open a Notepad File with Generated Content
def Content(topic):
    content_by_ai = ContentWriterAI(topic)
    
    filename = topic.lower().replace(" ", "_") + ".txt"
    filepath = os.path.join("Data", filename)
    
    os.makedirs("Data", exist_ok=True)  # Ensure Data directory exists

    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content_by_ai)
    
    subprocess.Popen(["notepad.exe", filepath])
    return True

# YouTube Search Function
def YoutubeSearch(topic):
    webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
    return True

# Play YouTube Video
def PlayYoutube(query):
    playonyt(query)
    return True
# Open Application (with Fallback)
def OpenApp(app):
    try:
        # Try to open as an installed application
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        # If the app is not installed, open the website
        print(f"[bold yellow]{app} not found, opening website...[/bold yellow]")
        webbrowser.open(f"https://www.{app}.com")
        return False

# Close Application
def CloseApp(app):
    if "chrome" in app:
        return False  # Prevent closing Chrome
    try:
        close(app, match_closest=True, throw_error=True)
        return True
    except:
        return False

# System Controls
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
   
    if command in actions:
        actions[command]()
        return True
    return False

# Command Execution with Async
async def TranslateAndExecute(commands):
    tasks = []
    
    for command in commands:
        command = command.lower()
        
        if command.startswith("open"):
            tasks.append(asyncio.to_thread(OpenApp, command.removeprefix("open").strip()))
        elif command.startswith("close"):
            tasks.append(asyncio.to_thread(CloseApp, command.removeprefix("close").strip()))
        elif command.startswith("play"):
            tasks.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play").strip()))
        elif command.startswith("content"):
            tasks.append(asyncio.to_thread(Content, command.removeprefix("content").strip()))
        elif command.startswith("google search"):
            tasks.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search").strip()))
        elif command.startswith("youtube search"):
            tasks.append(asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search").strip()))
        elif command.startswith("system"):
            tasks.append(asyncio.to_thread(System, command.removeprefix("system").strip()))
        else:
            print(f"[bold red]No function found for: {command}[/bold red]")

    results = await asyncio.gather(*tasks)
    return results

# Run Automation
async def Automation(commands):
    await TranslateAndExecute(commands)
    return True

# Entry Point
if __name__ == "__main__":
    asyncio.run(Automation(["open facebook",  "open instagram", "open telegram","content write a song about AI"]))