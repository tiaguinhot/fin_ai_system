import flet as ft
from ui.app_layout import AppLayout
import os

def main(page: ft.Page):
    page.title = "FinAI System"
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    # OTIMIZAÇÃO 1: Mudamos para STANDARD para reduzir espaços desnecessários globalmente
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO, 
        visual_density=ft.VisualDensity.STANDARD, 
        font_family="Roboto",
        use_material3=True
    )
    
    page.padding = 0
    # Tamanhos ajustados para desktop
    page.window.width = 1000
    page.window.height = 700
    page.window.min_width = 800
    page.window.min_height = 600
    
    # Centraliza a janela ao abrir
    page.window.center()

    layout = AppLayout(page)
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)