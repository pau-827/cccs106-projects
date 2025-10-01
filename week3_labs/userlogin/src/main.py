import flet as ft
from db_connection import connect_db
import mysql.connector

def main(page: ft.Page):
    page.title = "User Login"
    page.window_width = 400
    page.window_height = 350
    page.window_frameless = True
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.bgcolor = ft.Colors.AMBER_ACCENT

    # Title
    title = ft.Text("User Login", size=24, weight="bold", text_align="center", color=ft.Colors.BLUE_900)

    # Username and password fields
    username = ft.TextField(
        label="Username",
        hint_text="Enter your username",
        width=300,
        prefix_icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
    )
    
    password = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        width=300,
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        hint_style=ft.TextStyle(color=ft.Colors.GREY),
    )

    # One dialog instance with safe default
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(""),
        content=ft.Text(""),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dialog())]
    )

    # Register dialog with page once
    page.overlay.append(dialog)

    def close_dialog():
        dialog.open = False
        page.update()

    # Function to configure and show dialog
    def show_dialog(title, message, icon, color):
        dialog.title = ft.Row(
            [ft.Icon(icon, color=color, size=28),
             ft.Text(title, size=18, weight="bold")],
            alignment="start",
            spacing=10
        )
        dialog.content = ft.Text(message, size=14)
        dialog.actions = [ft.TextButton("OK", on_click=lambda e: close_dialog())]
        dialog.actions_alignment = "end"
        dialog.open = True
        page.update()

    # Login button handler
    def login_click(e):
        if not username.value or not password.value:
            show_dialog("Input Error", "Please enter username and password",
                        ft.Icons.INFO, ft.Colors.BLUE)
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username.value, password.value)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                show_dialog("Login Successful", f"Welcome, {username.value}!",
                            ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN)
            else:
                show_dialog("Login Failed", "Invalid username or password",
                            ft.Icons.ERROR, ft.Colors.RED)

        except mysql.connector.Error as err:
            print("DB error:", err)
            show_dialog("Database Error", "An error occurred while connecting to the database",
                        ft.Icons.STORAGE, ft.Colors.ORANGE)

    # Login button
    login_button = ft.ElevatedButton(
        text="Login", width=150, icon=ft.Icons.LOGIN, on_click=login_click
    )

    # Layout
    page.add(
        ft.Column(
            [title, username, password,
             ft.Container(content=login_button, alignment=ft.alignment.center)],
            spacing=20,
            horizontal_alignment="center",
            alignment="center",
        )
    )

ft.app(target=main)