# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
from pathlib import Path

class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.search_history = self.load_history()
        self.setup_page()
        self.build_ui()
        
    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []

    def save_history(self):
        """Save search history to file."""
        with open(self.history_file, 'w') as f:
            json.dump(self.search_history, f)
    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
    
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.SYSTEM  # Use system theme
    
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
    
        self.page.padding = 20
    
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
    
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_200,
            border_radius=10,
            padding=20,
        )
        
        # Forecast container (hidden by default)
        self.forecast_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Title row with Toggle
        title_row = ft.Row(
            [
                self.title,
                self.theme_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        
        # UI for search history
        self.history_dropdown = ft.Dropdown(
            label="Recent searches",
            label_style=ft.TextStyle(size=12, color=ft.Colors.GREY_800),
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=self.on_history_select,
            width=300
        )

        weather_and_forecast_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.weather_container,
                    col={"xs": 12, "md": 6},
                    padding=0
                ),
                ft.Container(
                    content=self.forecast_container,
                    col={"xs": 12, "md": 6},
                    padding=0
                ),
            ],
            spacing=10,
            run_spacing=10,
        )
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    
                    # Search history dropdown in a row, left-aligned
                    ft.Row(
                        [self.history_dropdown],
                        alignment=ft.MainAxisAlignment.START,
                    ),

                    self.search_button,
                    
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    weather_and_forecast_row,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )
        
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
        
    def on_history_select(self, e):
        self.city_input.value = e.control.value
        self.page.update()
    
    def add_to_history(self, city: str):
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10]  # keep last 10
            self.save_history()
            
            # Update dropdown
            if hasattr(self, "history_dropdown"):
                self.history_dropdown.options = [ft.dropdown.Option(c) for c in self.search_history]
                self.page.update()
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Add to history
            self.add_to_history(city)
            
            # Display weather
            await self.display_weather(weather_data)
            
            # Fetch weather data
            forecast_data = await self.weather_service.get_forecast(city)
            
            # Display forecast
            await self.display_forecast(forecast_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get('main', {}).get('pressure', 0)
        cloudiness = data.get('clouds', {}).get('all', 0)
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),

                # Weather icon and description
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                            color=ft.Colors.BLUE_900,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # Temperature
                ft.Text(
                    f"{temp:.1f}°C",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),

                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),

                ft.Divider(),

                # Additional info
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=self.create_info_card(
                                ft.Icons.WATER_DROP, "Humidity", f"{humidity}%"
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                        ft.Container(
                            content=self.create_info_card(
                                ft.Icons.AIR, "Wind Speed", f"{wind_speed} m/s"
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                        ft.Container(
                            content=self.create_info_card(
                                ft.Icons.SPEED, "Pressure", f"{pressure} hPa"
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                        ft.Container(
                            content=self.create_info_card(
                                ft.Icons.CLOUD, "Cloudiness", f"{cloudiness} %"
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                    ],
                    spacing=10,
                    run_spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # -- Animation --
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()
        
        # Fade in
        self.weather_container.opacity = 1
        self.page.update()
        
    async def display_forecast(self, data: dict):
        """Display 5-day forecast using one sample per day."""
        forecast_list = data.get("list", [])
        daily_forecast = forecast_list[::8]  # 5 days reading

        # Create forecast cards
        forecast_cards = []
        
        for item in daily_forecast:
            card=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(item["dt_txt"].split()[0], size=14, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD),
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png",
                            width=60,
                            height=60,
                        ),
                        ft.Text(
                            f"{item['main']['temp']}°C",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                bgcolor=ft.Colors.BLUE_100,
                border_radius=10,
                padding=10,
                width=120,
                height=150,
                col={"xs": 12, "sm": 6, "md": 4}
            )
            forecast_cards.append(card)

        # Make the entire forecast section big like the left weather box
        self.forecast_container.content = ft.Column(
            [
                ft.Text("5-Day Forecast", size=22, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD),
                ft.ResponsiveRow(
                    controls=forecast_cards,
                    spacing=15,
                    run_spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
        self.forecast_container.padding = 20
        self.forecast_container.border_radius = 10
        self.forecast_container.visible = True
        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.YELLOW_200,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.forecast_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
    