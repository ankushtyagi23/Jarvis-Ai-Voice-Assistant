from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat history
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []

def GoogleSearch(query: str):



    """Performs a Google search and returns the top 5 results."""
    Answer = f"The search results for '{query.strip()}' are:\n[start]\n"



    try:
        results = search(query.strip(), num_results=10)  # Increased number of results to 10




        for i in results:
            Answer += f"{i}\n"  # Only URL is returned in googlesearch package
    except Exception as e:
        Answer += f"Error performing Google search: {str(e)}. Please try again later."

    if not results:
        print("⚠️ No results found for the query.")
    Answer += "[end]"


    return Answer

def AnswerModifier(Answer):
    """Cleans up the answer by removing empty lines."""
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def Information():
    """Fetches real-time date and time."""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")  # Corrected formatting
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    
    return data

def RealtimeSearchEngine(prompt):
    """Processes a query, performs a Google search, and uses Groq AI to generate a response."""
    global messages

    # Load chat history
    try:
        with open(r"Data/ChatLog.json", "r") as f:
            messages = load(f)
    except FileNotFoundError:
        messages = []

    # Add user query
    messages.append({"role": "user", "content": prompt})

    # Get Google search results
    search_results = GoogleSearch(prompt)

    # System message with search results
    system_messages = [
        {"role": "system", "content": System},
        {"role": "system", "content": search_results},
        {"role": "system", "content": Information()}
    ]

    # Streamed response
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=system_messages + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True
    )

    # Collect streamed response
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Update chat history
    messages.append({"role": "assistant", "content": Answer})
    with open(r"Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)


if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
