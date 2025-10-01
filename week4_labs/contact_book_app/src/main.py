import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600

    db_conn = init_db()

    # Input fields
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)

    # Search input
    search_input = ft.TextField(
        label="Search Contacts",
        width=350,
    )

    # Clear name input error when typing
    def clear_name_error_text(e):
        if name_input.error_text:
            name_input.error_text = None
            page.update()
    name_input.on_change = clear_name_error_text

    inputs = (name_input, phone_input, email_input)

    # Contacts ListView
    contacts_list_view = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    # Scrollable Contacts section
    contacts_section = ft.Column(
        controls=[contacts_list_view],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    # Add Contact button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    # Dark mode toggle
    def toggle_theme(e, page):
        page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        page.update()

    dark_mode_switch = ft.Switch(
        label="Dark Mode",
        value=False,
        on_change=lambda e: toggle_theme(e, page)
    )

    # Connect search input to display_contacts
    search_input.on_change = lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value)

    # Main layout
    page.add(
        ft.Column(
            controls=[
                dark_mode_switch,
                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Text("Search Contacts:", size=16, weight=ft.FontWeight.BOLD),
                search_input,
                contacts_section
            ],
            expand=True
        )
    )

    # Display initial contacts
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)