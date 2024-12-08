import tkinter as tk # Used for the GUI
from tkinter import messagebox, simpledialog, ttk
import os
import json
from plyer import notification
import openai
import traceback

# --- Configuration ---
with open("config.json", "r") as file: # I store most sensitive info in my config.json file. Currently if you want to use the AI aspect of this, you'd need to recreate this config file and insert your own API key.
    config = json.load(file)
    
APP_DATA_FILE = "checklist_data.json"
ERROR_LOG_FILE = "error_log.txt"
OPENAI_API_KEY = config["OPENAI_API_KEY"] # Once you have your own API key in a config.json file, have it point here.

# --- Error Handling ---
def log_error(e):
    with open(ERROR_LOG_FILE, "a") as file:
        file.write(traceback.format_exc())
    print(f"An error occurred. Details logged to {ERROR_LOG_FILE}")

# --- Load/Save Tasks ---
def load_tasks(): #This loads whatever tasks you may have already generated, which are saved in a .json file nearby. For a quick and easy reset of your checklist, simply delete this.
    try:
        if os.path.exists(APP_DATA_FILE):
            with open(APP_DATA_FILE, "r") as file:
                return json.load(file)
        return []
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to load tasks.")
        return []

def save_tasks(): # This will save your checklist as soon as it's made, and update their status (checked or unchecked).
    try:
        with open(APP_DATA_FILE, "w") as file:
            json.dump(tasks, file)
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to save tasks.")

# --- Task Management ---
def add_task(): # This is the manual way to add a task.
    try:
        task = simpledialog.askstring("New Task", "Enter a new task:")
        if task:
            tasks.append({"task": task, "completed": False})
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to add task.")

def remove_task(): # Manual way to delete a task.
    try:
        selected_task_index = task_listbox.curselection()
        if selected_task_index:
            tasks.pop(selected_task_index[0])
            refresh_task_list()
            save_tasks()
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to remove task.")
        
#def select_all_tabs():     --- Not really necessary right now. Might be implemented later?
#    for tab_id in range(notebook.index("end")):  # Loop through all tabs
#       notebook.select(tab_id)
        
def disable_generate_tasks(): # This function disables the "Generate tasks" option once it's been generated. Implementing this now for when I want to provide my own usage key (to prevent spamming), and I currently don't delete one checklist when you generate another (in case of it being an accident or something).
    generate_button.config(state=tk.DISABLED)
    
def update_checklist_size(event): # This scales the checklist box with the size of your screen. A lot prettier!
    task_listbox.config(width=event.width // 10, height=event.height // 30)

def toggle_task(): # This marks your task as done or not, with a checkmark.
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

def refresh_task_list(): # When your previous tasks are loaded, this is what loads them (along with their status).
    try:
        task_listbox.delete(0, tk.END)
        for task in tasks:
            prefix = "[✔] " if task["completed"] else "[ ] "
            task_listbox.insert(tk.END, prefix + task["task"])
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", "Failed to refresh task list.")

# --- ChatGPT Integration ---

def generate_roadmap(goal, roadmap_label): # This generates a roadmap title at the top (planning on expanding on this later).
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You will generate a roadmap title for a specified goal."},
                {"role": "user", "content": f"Create a title for the goal: {goal}."}
            ]
        )
        roadmap = response['choices'][0]['message']['content']
        # Update the roadmap label with the generated content
        roadmap_label.config(text=roadmap)
    except Exception as e:
        log_error(e)
        messagebox.showerror("Error", f"Failed to generate roadmap: {e}")
        
def generate_tasks(): # This is what generates the checklist string.
    try:
        goal = simpledialog.askstring("Goal", "What is your goal?")
        if goal:
            # Get the roadmap label to update
            roadmap_label = create_roadmap_tab(notebook)
            generate_roadmap(goal, roadmap_label)  # Generate roadmap first
            
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[ # The given prompt. Feel free to manipulate it however you see fit.
                    {"role": "system", "content": "You will firstly generate a detailed roadmap on a specified subject, with subjects such as research needed, programs/software you may need, literature and readings that can be helpful, and practicable goals. Secondly, you will help guide the user to practice weekly goals and make sure they have the help they need to have improvement in said subject. You will generate a weekly checklist pertaining to the roadmap, with an achievable goal every week and a bi-daily reading suggestion. Do not overelaborate, or add any off topic information. Do not anything like by following this list you'll get x, just keep to the checklist. "},
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
def send_notification(): # Not quite sure what I want to do with this, but might as well keep it around.
    try:
        notification.notify(
            title="Checklist Reminder",
            message="Don't forget to check your tasks for today!",
            timeout=10
        )
    except Exception as e:
        log_error(e)

# --- Dark Mode GUI Setup ---
def set_dark_mode(): # Made it a lot easier on the eyes.
    app.configure(bg='#2e2e2e')
    task_listbox.configure(bg='#333333', fg='#ffffff', selectbackground='#555555', selectforeground='#ffffff')
    button_frame.configure(bg='#2e2e2e')
    
    for widget in button_frame.winfo_children():
        widget.configure(bg='#555555', fg='#ffffff', activebackground='#777777', activeforeground='#ffffff')

# --- Roadmap Tab ---
def create_roadmap_tab(notebook): # This is where the roadmaps are positioned.
    roadmap_tab = tk.Frame(notebook, bg='#2e2e2e')
    notebook.add(roadmap_tab, text="Roadmap")
    roadmap_label = tk.Label(roadmap_tab, text="Roadmap content will appear here.", fg="#ffffff", bg="#2e2e2e", wraplength=600, justify="left")
    roadmap_label.pack(padx=10, pady=10)
    return roadmap_label


# --- GUI Setup ---
try: # I... Am Steve.
    app = tk.Tk()
    app.title("Checklist Application")
    app.geometry("800x600")  # Set initial window size

    # Bind resize event for dynamic scaling
    app.bind("<Configure>", update_checklist_size)

    notebook = ttk.Notebook(app)
    notebook.pack(expand=True, fill="both")

    # Roadmap Tab Setup
    create_roadmap_tab(notebook)

    # Checklist Box
    task_listbox = tk.Listbox(app, width=80, height=20)
    task_listbox.pack(expand=True, fill="both")  # Make it fill the available space

    # Button Frame
    button_frame = tk.Frame(app)
    button_frame.pack()

    tk.Button(button_frame, text="Add Task", command=add_task).grid(row=0, column=0)
    tk.Button(button_frame, text="Remove Task", command=remove_task).grid(row=0, column=1)
    tk.Button(button_frame, text="Toggle Task", command=toggle_task).grid(row=0, column=2)
    generate_button = tk.Button(button_frame, text="Generate Tasks (ChatGPT)",
                                 command=lambda: [generate_tasks(), disable_generate_tasks()])
    generate_button.grid(row=0, column=3)

    # Load tasks and initialize
    tasks = load_tasks()
    refresh_task_list()

    # Send reminder notifications
    send_notification()

    # Apply dark mode theme
    set_dark_mode()

    app.mainloop()

except Exception as e:
    log_error(e)
    input("An unexpected error occurred. Press Enter to exit...")