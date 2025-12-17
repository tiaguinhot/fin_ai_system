import flet as ft
from ui.app_layout import AppLayout
import os

def main(page: ft.Page):
    page.title = "FinAI System"
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    # CONFIGURAÇÃO DE LOCALIZAÇÃO (PORTUGUÊS BRASIL)
    # Isso traduz automaticamente o DatePicker e outros componentes
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("pt", "BR"),
            ft.Locale("en", "US"),
        ],
        current_locale=ft.Locale("pt", "BR")
    )

    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO, 
        visual_density=ft.VisualDensity.STANDARD, 
        font_family="Roboto",
        use_material3=True
    )
    
    page.padding = 0
    page.window.width = 1000
    page.window.height = 700
    page.window.min_width = 800
    page.window.min_height = 600
    page.window.center()

    layout = AppLayout(page)
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)