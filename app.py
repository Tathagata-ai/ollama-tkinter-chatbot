# %%
import requests
import tkinter as tk
from tkinter import scrolledtext
import json
import threading

# ---------------- CONFIG ----------------
URL = "http://localhost:11434/api/chat"
MODEL = "phi3:mini"

SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely in markdown."

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# ---------------- SEND MESSAGE ----------------
def send_message():
    user_input = entry.get().strip()
    if not user_input:
        return

    entry.delete(0, tk.END)

    # Show user message
    chat_area.insert(tk.END, f"You: {user_input}\n")
    chat_area.yview(tk.END)

    # Add to memory
    messages.append({"role": "user", "content": user_input})

    # Limit memory for speed
    limited_messages = messages[-4:]

    # Run API in thread
    threading.Thread(target=get_response, args=(limited_messages,), daemon=True).start()


# ---------------- GET RESPONSE ----------------
def get_response(msgs):
    payload = {
        "model": MODEL,
        "messages": msgs,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "num_predict": 150
        }
    }

    try:
        response = requests.post(URL, json=payload, stream=True)

        if response.status_code == 200:

            full_reply = ""

            # Show AI label safely
            root.after(0, lambda: chat_area.insert(tk.END, "AI: "))

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))

                        if "message" in data and "content" in data["message"]:
                            content = data["message"]["content"]
                            full_reply += content

                            # Thread-safe UI update
                            root.after(0, lambda c=content: chat_area.insert(tk.END, c))
                            root.after(0, lambda: chat_area.yview(tk.END))

                    except json.JSONDecodeError:
                        continue

            # New line after full response
            root.after(0, lambda: chat_area.insert(tk.END, "\n\n"))

            # Save response to memory
            messages.append({"role": "assistant", "content": full_reply})

        else:
            root.after(0, lambda: chat_area.insert(
                tk.END, f"\nError: {response.status_code} - {response.text}\n"
            ))

    except Exception as e:
        root.after(0, lambda: chat_area.insert(
            tk.END, f"\nConnection Error: {str(e)}\n"
        ))


# ---------------- CLEAR CHAT ----------------
def clear_chat():
    chat_area.delete("1.0", tk.END)

    global messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


# ---------------- UI SETUP ----------------
root = tk.Tk()
root.title("Ollama AI Assistant")
root.geometry("650x520")
root.configure(bg="#1e1e2f")

# Chat display
chat_area = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Arial", 12),
    bg="#2b2b3c",
    fg="#f8f8f2",
    insertbackground="#f8f8f2"
)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Input frame
frame = tk.Frame(root, bg="#1e1e2f")
frame.pack(padx=10, pady=10, fill=tk.X)

# Input box
entry = tk.Entry(
    frame,
    font=("Arial", 12),
    bg="#3a3a4f",
    fg="#f8f8f2",
    insertbackground="#f8f8f2"
)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# Clear button
clear_btn = tk.Button(
    frame,
    text="Clear",
    command=clear_chat,
    bg="#ff5555",
    fg="white",
    font=("Arial", 11)
)
clear_btn.pack(side=tk.RIGHT, padx=(0, 5))

# Send button
send_button = tk.Button(
    frame,
    text="Send",
    command=send_message,
    bg="#50fa7b",
    fg="black",
    font=("Arial", 11)
)
send_button.pack(side=tk.RIGHT)

# Enter key support
root.bind('<Return>', lambda event: send_message())

# Run app
root.mainloop()


