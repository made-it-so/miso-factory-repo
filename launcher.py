# MISO Self-Contained Engine - launcher.py v1.4 (Forcing Debug Mode)
import tkinter as tk
from tkinter import font
import subprocess
import webbrowser
import os
import signal

SERVER_URL = "http://127.0.0.1:5000"
PATH_TO_AGENT_RUNNER = "python_agent_runner"
server_process = None

def start_server():
    global server_process
    if server_process is None:
        try:
            print("Starting MISO server in DEBUG mode...")
            # Create a copy of the current environment and add the FLASK_DEBUG variable
            env = os.environ.copy()
            env["FLASK_DEBUG"] = "1"
            
            server_process = subprocess.Popen(
                ["flask", "run"],
                cwd=PATH_TO_AGENT_RUNNER,
                env=env, # Pass the modified environment to the subprocess
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            update_status("Server is starting...", "green")
            app.after(4000, check_server_status)
        except Exception as e:
            update_status(f"Error: {e}", "red")
#... (The rest of the file is the same as v1.3, this is a simplified representation)
def check_server_status():
    global server_process
    if server_process and server_process.poll() is None:
        update_status("Server is RUNNING (Debug Mode)", "green")
        start_button.config(state=tk.DISABLED); stop_button.config(state=tk.NORMAL); open_button.config(state=tk.NORMAL)
    else:
        server_process = None; update_status("Server failed or stopped.", "red")
        start_button.config(state=tk.NORMAL); stop_button.config(state=tk.DISABLED); open_button.config(state=tk.DISABLED)
def stop_server():
    global server_process
    if server_process:
        print("Stopping MISO server..."); os.kill(server_process.pid, signal.CTRL_C_EVENT)
        server_process = None; update_status("Server is OFFLINE", "gray")
        start_button.config(state=tk.NORMAL); stop_button.config(state=tk.DISABLED); open_button.config(state=tk.DISABLED)
def open_forge(): webbrowser.open_new_tab(SERVER_URL)
def update_status(message, color): status_label.config(text=message, fg=color)
app = tk.Tk(); app.title("MISO Engine"); app.geometry("400x220"); app.resizable(False, False)
default_font = font.Font(family="Segoe UI", size=10); status_font = font.Font(family="Segoe UI", size=11, weight="bold")
main_frame = tk.Frame(app, padx=20, pady=20); main_frame.pack(fill=tk.BOTH, expand=True)
status_label = tk.Label(main_frame, text="Server is OFFLINE", font=status_font, fg="gray", wraplength=360); status_label.pack(pady=10)
button_frame = tk.Frame(main_frame); button_frame.pack(pady=20)
start_button = tk.Button(button_frame, text="Start Server", command=start_server, font=default_font, width=15); start_button.pack(side=tk.LEFT, padx=5)
stop_button = tk.Button(button_frame, text="Stop Server", command=stop_server, font=default_font, width=15, state=tk.DISABLED); stop_button.pack(side=tk.LEFT, padx=5)
open_button = tk.Button(main_frame, text="Open MISO Forge", command=open_forge, font=default_font, state=tk.DISABLED); open_button.pack()
app.mainloop()
if server_process: stop_server()
