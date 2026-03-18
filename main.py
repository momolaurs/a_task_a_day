import flet as ft
import random
import sqlite3
import os
from datetime import datetime

#database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tasks.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date_added TEXT NOT NULL,
        completed INTEGER NOT NULL
    )
    """)
    conn.commit()

# db logic

def add_task_db(task_name):
    cursor.execute("""
        INSERT INTO tasks (name, date_added, completed)
        VALUES (?, ?, ?)
    """, (
        task_name,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        0
    ))
    conn.commit()

def get_tasks_db():
    cursor.execute("SELECT * FROM tasks WHERE completed = 0")
    rows = cursor.fetchall()
    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "name": row[1],
            "date_added": row[2],
            "completed": bool(row[3])
        })
    return tasks

def complete_task_db(task_id):
    cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()

def update_task_db(task_id, new_name):
    cursor.execute("UPDATE tasks SET name = ? WHERE id = ?", (new_name, task_id))
    conn.commit()

def pick_weighted_task_db():
    tasks = get_tasks_db()
    if not tasks:
        return None
    now = datetime.now()
    weights = []
    for task in tasks:
        date_added = datetime.strptime(task['date_added'], "%Y-%m-%d %H:%M:%S")
        days_old = (now - date_added).days
        weights.append(days_old + 1)
    return random.choices(tasks, weights=weights, k=1)[0]

#ui

def main(page: ft.Page):
    page.title = "a task a day"
    page.padding = 20
    page.window.width = 500
    page.window.height = 700

    task_list = ft.Column()

    def refresh_task_list():
        task_list.controls.clear()
        tasks = get_tasks_db()

        for task in tasks:

            def make_complete_handler(t_id):
                return lambda e: complete_task(t_id)

            def make_edit_handler(t):
                return lambda e: open_edit_dialog(t)

            checkbox = ft.Checkbox(value=False, on_change=make_complete_handler(task['id']))
            task_text = ft.Text(task['name'], expand=True)
            edit_button = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="edit task",
                on_click=make_edit_handler(task)
            )

            row = ft.Row([checkbox, task_text, edit_button])
            task_list.controls.append(row)

        page.update()

    def add_task(e=None):
        if task_input.value.strip() == "":
            return
        add_task_db(task_input.value.strip())
        task_input.value = ""
        refresh_task_list()

    def complete_task(task_id):
        complete_task_db(task_id)
        refresh_task_list()

    def pick_task(e):
        task = pick_weighted_task_db()
        if task:
            selected_task_text.value = f"the ✨oRacLE✨ has chosen: \n {task['name']}"
        else:
            selected_task_text.value = "you are free of burden"
        oracle_button.visible = False
        selected_task_text.visible = True
        page.update()

    def open_edit_dialog(task):
        edit_input = ft.TextField(value=task['name'])

        dialog = ft.AlertDialog(title=ft.Text("Edit Task"), content=edit_input)

        def close_dialog(e=None):
            dialog.open = False
            page.update()

        def save_edit(e):
            if edit_input.value.strip() == "":
                return
            update_task_db(task['id'], edit_input.value)
            close_dialog()
            refresh_task_list()

        dialog.actions = [
            ft.TextButton("cancel", on_click=close_dialog),
            ft.TextButton("save", on_click=save_edit),
        ]

        page.overlay.append(dialog) 
        dialog.open = True
        page.update()

    #layout

    task_input = ft.TextField(label="new task", expand=True, on_submit=add_task)
    oracle_button = ft.Button("ask the ✨OrACle✨", on_click=pick_task)
    selected_task_text = ft.Text(size=18, weight="bold", text_align="center", visible=False)

    oracle_container = ft.Container(
        content=ft.Column(
            [oracle_button, selected_task_text],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment(0, 0),
        border=ft.border.all(1, "grey"),
        border_radius=10,
        padding=20,
    )

    page.add(
        ft.Row(
            [ft.Text("a task a day", size=36, weight="bold", text_align="center")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        oracle_container,
        ft.Divider(),
        task_list,
        ft.Row([
            ft.Icon(ft.Icons.ADD, color="grey"),
            task_input,
            ft.Button("add", on_click=add_task)
        ])
    )
    refresh_task_list()
    page.update()

#run the thing

init_db()
ft.run(main)