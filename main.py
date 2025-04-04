import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext, ttk

GOOGLE_API_KEY = "AIzaSyD6bTQ1NbxvKaIfybTWxcjS8epl1tYQufc"
genai.configure(api_key=GOOGLE_API_KEY)

LANGUAGES = ["Python", "Java", "C++", "JavaScript", "C#", "Go", "Rust"]

BG_COLOR = "#1e1e1e"  
TEXT_COLOR = "#dcdcdc"  
BUTTON_COLOR = "#007acc" 
INPUT_BG = "#252526"  
INPUT_TEXT = "#ffffff"  

def get_debugging_response(user_input, language):
    """Send the user's input code & language to Gemini AI for debugging."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest") 
        prompt = f"Debug this {language} code:\n{user_input}\nProvide fixes and explanations."
        response = model.generate_content(prompt)
        return response.text if response.text else "No response from AI."
    except Exception as e:
        return f"Error: {str(e)}"

def send_message():
    """Handles user input, sends it to Gemini AI, and displays the response."""
    user_input = user_entry.get("1.0", tk.END).strip()
    selected_language = language_var.get()

    if user_input:
        chat_history.insert(tk.END, f"You ({selected_language}):\n{user_input}\n", "user")
        chat_history.insert(tk.END, "-" * 70 + "\n", "divider")

        response = get_debugging_response(user_input, selected_language)
        chat_history.insert(tk.END, f"Bot:\n{response}\n", "bot")
        chat_history.insert(tk.END, "=" * 70 + "\n", "divider")
        
        chat_history.yview(tk.END)
        user_entry.delete("1.0", tk.END)
def clear_placeholder(event):
    if user_entry.get("1.0", "end-1c") == placeholder_text:
        user_entry.delete("1.0", "end")
        user_entry.config(fg=INPUT_TEXT)

def add_placeholder(event):
    if user_entry.get("1.0", "end-1c").strip() == "":
        user_entry.insert("1.0", placeholder_text)
        user_entry.config(fg="gray")

root = tk.Tk()
root.title("🌟 AI Debugging Chatbot")
root.geometry("1000x800")
root.configure(bg=BG_COLOR)

chat_history = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Arial", 12),bg=INPUT_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
chat_history.pack(pady=10, padx=10)
chat_history.tag_config("user", foreground="#00ff00")
chat_history.tag_config("bot", foreground="#ffa500")  
chat_history.tag_config("divider", foreground="#666666") 

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack(pady=5)

tk.Label(frame, text="Select Language:", font=("Arial", 12, "bold"), fg=TEXT_COLOR, bg=BG_COLOR).pack(side=tk.LEFT, padx=5)
language_var = tk.StringVar()
language_var.set("Python")  # Default language
language_menu = ttk.Combobox(frame, textvariable=language_var, values=LANGUAGES, state="readonly", font=("Arial", 12))
language_menu.pack(side=tk.LEFT, padx=5)

# Input Box
user_entry = tk.Text(root, height=15, width=80, font=("Arial", 12), bg=INPUT_BG, fg=INPUT_TEXT, insertbackground=TEXT_COLOR)
user_entry.pack(pady=5, padx=10)

placeholder_text = "Enter your code here..."
user_entry.insert("1.0", placeholder_text)
user_entry.config(fg="gray")

user_entry.bind("<FocusIn>", clear_placeholder)
user_entry.bind("<FocusOut>", add_placeholder)

# Send Button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 12, "bold"), 
                        bg=BUTTON_COLOR, fg="white", activebackground="#005f8b", padx=20, pady=5)
send_button.pack(pady=10)

root.mainloop()
