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
        date_completed TEXT,
        completed INTEGER NOT NULL
    )
    """)
    conn.commit()

# db logic

def add_task_db(task_name):
    cursor.execute("""
        INSERT INTO tasks (name, date_added, date_completed, completed)
        VALUES (?, ?, ?, ?)
    """, (
        task_name,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        None,
        0
    ))
    conn.commit()

def get_tasks_db():
    cursor.execute("SELECT * FROM tasks WHERE completed = 0")
    rows = cursor.fetchall()
    return format_tasks(rows)

def get_completed_tasks_db():
    cursor.execute("SELECT * FROM tasks WHERE completed = 1")
    rows = cursor.fetchall()
    return format_tasks(rows)

def format_tasks(rows):
    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "name": row[1],
            "date_added": row[2],
            "date_completed": row[3],
            "completed": bool(row[4])
        })
    return tasks

def complete_task_db(task_id):
    cursor.execute("""
        UPDATE tasks 
        SET completed = 1, date_completed = ?
        WHERE id = ?
    """, (
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        task_id
    ))
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

# helpers

def time_ago(date_str):
    now = datetime.now()
    past = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    diff = now - past

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds//60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds//3600)}h ago"
    else:
        return f"{diff.days}d ago"

def procrastination_days(task):
    dc = task.get('date_completed')

    if not dc or dc == 0 or not isinstance(dc, str):
        return 0

    try:
        added = datetime.strptime(task['date_added'], "%Y-%m-%d %H:%M:%S")
        completed = datetime.strptime(dc, "%Y-%m-%d %H:%M:%S")
        return (completed - added).days
    except Exception:
        return 0

# ui

def main(page: ft.Page):
    page.title = "a (1) task a day"
    page.window.width = 700
    page.window.height = 700
    page.padding = 0

    # ---------- STATE ----------
    content = ft.Column(expand=True)
    task_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    auto_close = True

    # ---------- HELPERS ----------

    def clear_content():
        content.controls.clear()
    
    def toggle_auto_close(e):
        nonlocal auto_close
        auto_close = e.control.value

    def show_home():
        clear_content()

        refresh_task_list()

        content.controls.extend([
            ft.Text("a task a day", size=32, weight="bold"),

            ft.Container(
                content=ft.Column(
                    [oracle_button, selected_task_text, complete_oracle_button],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                border=ft.Border.all(1, "grey"),
                border_radius=12,
                padding=20
            ),

            ft.Divider(),
            ft.Container(task_list, expand=True),

            ft.Row([
                task_input,
                ft.Button("add", on_click=add_task)
            ])
        ])

        page.update()

    def show_completed():
        clear_content()

        tasks = get_completed_tasks_db()

        completed_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        for task in tasks:
            days = procrastination_days(task)
            label = "same day" if days == 0 else f"was procrastinated for {days} days"

            completed_list.controls.append(
                ft.Row([
                    ft.Column([
                        ft.Text(task['name'], weight="bold"),
                        ft.Text(label, size=12, color="grey")
                    ], expand=True)
                ])
            )

        content.controls.extend([
            ft.Text(f"completed tasks ({len(tasks)})", size=28, weight="bold"),
            completed_list
        ])

        page.update()

    def show_debug():
        clear_content()

        def delete_completed(e):
            cursor.execute("DELETE FROM tasks WHERE completed = 1")
            conn.commit()
            show_debug()

        content.controls.extend([
            ft.Text("debug", size=28, weight="bold"),
            ft.Text("danger zone ⚠️", color="red"),

            ft.Button(
                "delete ALL completed tasks",
                bgcolor="red",
                color="white",
                on_click=delete_completed
            )
        ])

        page.update()

    # ---------- TASK LIST ----------

    def refresh_task_list():
        task_list.controls.clear()
        tasks = get_tasks_db()

        for task in tasks:

            def make_complete_handler(t_id):
                return lambda e: complete_task(t_id)

            def make_edit_handler(t):
                return lambda e: open_edit_dialog(t)

            row = ft.Row([
                ft.Checkbox(on_change=make_complete_handler(task['id'])),

                ft.Column([
                    ft.Text(task['name'], weight="bold"),
                    ft.Text(time_ago(task['date_added']), size=12, color="grey"),
                ], expand=True, spacing=0),

                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    on_click=make_edit_handler(task)
                )
            ])

            task_list.controls.append(row)

    # ---------- ACTIONS ----------

    def add_task(e=None):
        if not task_input.value.strip():
            return
        add_task_db(task_input.value.strip())
        task_input.value = ""
        refresh_task_list()
        page.update()

    def complete_task(task_id):
        complete_task_db(task_id)

        if auto_close:
            page.run_task(page.window.close)
        else:
            refresh_task_list()
            page.update()

    def pick_task(e):
        task = pick_weighted_task_db()
        if task:
            selected_task_text.value = f"the ✨oRacLE✨ has chosen: \n {task['name']}"
            complete_oracle_button.visible = True
            complete_oracle_button.on_click = lambda e: complete_task(task['id'])
        else:
            selected_task_text.value = "you are free of burden"

        oracle_button.visible = False
        selected_task_text.visible = True

        page.update()

    def open_edit_dialog(task):
        edit_input = ft.TextField(value=task['name'])

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Task"),
            content=edit_input,
            actions=[
                ft.TextButton("cancel", on_click=lambda e: close_dialog(dialog)),
                ft.TextButton("save", on_click=lambda e: save_edit())
            ]
        )

        def save_edit():
            if edit_input.value.strip():
                update_task_db(task['id'], edit_input.value)
                close_dialog(dialog)
                refresh_task_list()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # ---------- INPUTS ----------

    task_input = ft.TextField(label="new task", expand=True, on_submit=add_task)

    oracle_button = ft.Button("ask the ✨OrACle✨", on_click=pick_task)
    selected_task_text = ft.Text(visible=False, size=18, weight="bold")
    complete_oracle_button = ft.Button("completed", visible=False)

    # ---------- SIDEBAR ----------
    auto_close_switch = ft.Switch(
        value=True,
        tooltip="If ON, the app will close automatically when you complete a task. If OFF, it just refreshes the list.",
        on_change=toggle_auto_close
    )
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME, label="home"),
            ft.NavigationRailDestination(icon=ft.Icons.CHECK, label="completed"),
            ft.NavigationRailDestination(icon=ft.Icons.BUG_REPORT, label="debug"),
        ],
        on_change=lambda e: handle_nav_change(e.control.selected_index)
    )

    def handle_nav_change(index):
        if index == 0:
            show_home()
        elif index == 1:
            show_completed()
        elif index == 2:
            show_debug()

    # ---------- LAYOUT ----------

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Container(
                            rail,
                            expand=True
                        ),
                        ft.Divider(),
                        ft.Text("   auto close toggle", size=11, color="grey"),
                        auto_close_switch 
                    ],
                    width=100
                ),

                ft.VerticalDivider(width=1),

                ft.Container(content, expand=True, padding=20)
            ],
            expand=True
        )
    )

    show_home()

# run

init_db()
ft.run(main)