import flet as ft
from ui.app_layout import AppLayout

def main(page: ft.Page):
    # Configurações da Janela
    page.title = "FinAI System"
    page.theme_mode = ft.ThemeMode.DARK # Modo escuro minimalista
    page.padding = 0
    page.window.width = 1000
    page.window.height = 700
    
    # Instancia o Layout Principal
    layout = AppLayout(page)
    
    # Adiciona à pagina
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)