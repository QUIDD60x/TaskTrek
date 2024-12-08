import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import os
import json
from plyer import notification
import openai
import traceback

# --- Configuration ---
with open("config.json", "r") as file:
    config = json.load(file)
    
APP_DATA_FILE = "checklist_data.json"
ERROR_LOG_FILE = "error_log.txt"
OPENAI_API_KEY = config["OPENAI_API_KEY"]

# --- Error Handling ---
def log_error(e):
    with open(ERROR_LOG_FILE, "a") as file:
        file.write(traceback.format_exc())
    print(f"An error occurred. Details logged to {ERROR_LOG_FILE}")

# --- Load/Save Tasks ---
def load_tasks():
    try:
        if os.path.exists(APP_DATA_FILE):
            with open(APP_DATA_FILE, "r") as file:
                return json.load(file)
        return []
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to load tasks.")
        return []

def save_tasks():
    try:
        with open(APP_DATA_FILE, "w") as file:
            json.dump(tasks, file)
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to save tasks.")

# --- Task Management ---
def add_task():
    try:
        task = simpledialog.askstring("New Task", "Enter a new task:")
        if task:
            tasks.append({"task": task, "completed": False})
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to add task.")

def remove_task():
    try:
        selected_task_index = task_listbox.curselection()
        if selected_task_index:
            tasks.pop(selected_task_index[0])
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to remove task.")

def toggle_task():
    try:
        selected_task_index = task_listbox.curselection()
        if selected_task_index:
            task = tasks[selected_task_index[0]]
            task["completed"] = not task["completed"]
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to toggle task.")

def refresh_task_list():
    try:
        task_listbox.delete(0, tk.END)
        for task in tasks:
            prefix = "[✔] " if task["completed"] else "[ ] "
            task_listbox.insert(tk.END, prefix + task["task"])
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to refresh task list.")

# --- ChatGPT Integration ---
def generate_tasks():
    try:
        goal = simpledialog.askstring("Goal", "What is your goal for today?")
        if goal:
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You will firstly generate a detailed roadmap on a specified subject, with subjects such as research needed, programs/software you may need, literature and readings that can be helpful, and practicable goals. Secondly, you will help guide the user to practice weekly goals and make sure they have the help they need to have improvement in said subject. You will generate a weekly checklist pertaining to the roadmap, with an achievable goal every week and a bi-daily reading suggestion. Do not overelaborate, or add any off topic information. "},
                    {"role": "user", "content": f"Create a checklist for achieving the goal: {goal}. include weekly small step goals to help progress the skill, and bi-weekly reading recommendations (if the task at hand should require something like that). Assume the checklist will be done in a weekly format, with learning checks and challenge check."}
                ]
            )
            checklist = response['choices'][0]['message']['content']
            for line in checklist.split("\n"):
                if line.strip():
                    tasks.append({"task": line.strip(), "completed": False})
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", f"Failed to generate tasks: {e}")

# --- Desktop Notifications ---
def send_notification():
    try:
        notification.notify(
            title="Checklist Reminder",
            message="Don't forget to check your tasks for today!",
            timeout=10
        )
    except Exception as e:
        log_error(e)

# --- Dark Mode GUI Setup ---
def set_dark_mode():
    app.configure(bg='#2e2e2e')
    task_listbox.configure(bg='#333333', fg='#ffffff', selectbackground='#555555', selectforeground='#ffffff')
    button_frame.configure(bg='#2e2e2e')
    
    for widget in button_frame.winfo_children():
        widget.configure(bg='#555555', fg='#ffffff', activebackground='#777777', activeforeground='#ffffff')

# --- Roadmap Tab ---
def create_roadmap_tab(notebook):
    roadmap_tab = tk.Frame(notebook, bg='#2e2e2e')
    notebook.add(roadmap_tab, text="Roadmap")
    tk.Label(roadmap_tab, text="Roadmap Test 1", fg="#ffffff", bg="#2e2e2e").pack()
    # tk.Label(roadmap_tab, text="Learning Path 2: Data Structures", fg="#ffffff", bg="#2e2e2e").pack()

# --- GUI Setup ---
try:
    app = tk.Tk()
    app.title("Checklist Application")

    notebook = ttk.Notebook(app)
    notebook.pack(expand=True, fill="both")

    # Create the roadmap tab
    create_roadmap_tab(notebook)

    task_listbox = tk.Listbox(app, height=15, width=50)
    task_listbox.pack()

    button_frame = tk.Frame(app)
    button_frame.pack()

    tk.Button(button_frame, text="Add Task", command=add_task).grid(row=0, column=0)
    tk.Button(button_frame, text="Remove Task", command=remove_task).grid(row=0, column=1)
    tk.Button(button_frame, text="Toggle Task", command=toggle_task).grid(row=0, column=2)
    tk.Button(button_frame, text="Generate Tasks (ChatGPT)", command=generate_tasks).grid(row=0, column=3)

    tasks = load_tasks()
    refresh_task_list()

    send_notification()

    set_dark_mode()  # Apply dark mode

    app.mainloop()

except Exception as e:
    log_error(e)
    input("An unexpected error occurred. Press Enter to exit...")