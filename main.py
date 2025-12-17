import flet as ft
from ui.app_layout import AppLayout

def main(page: ft.Page):
    page.title = "FinAI System"
    
    # Define o Modo Claro
    page.theme_mode = ft.ThemeMode.LIGHT 
    
    # Configura o Tema com a cor Semente (Indigo)
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.INDIGO, 
        # CORREÇÃO AQUI: Mudou de ThemeVisualDensity para VisualDensity
        visual_density=ft.VisualDensity.COMFORTABLE,
        font_family="Roboto",
        use_material3=True
    )
    
    page.padding = 0
    page.window.width = 1100
    page.window.height = 800
    
    layout = AppLayout(page)
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main)