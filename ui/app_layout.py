import flet as ft
from ui.pages.home import HomePage
from ui.pages.add_transaction import AddTransactionPage
# Importamos o manager para ler o saldo real na home
from database.db_manager import get_saldo_total

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True 
        
        self.content_area = ft.Container(
            expand=True, 
            padding=10,
            content=self.get_home_content() # Começa com a Home
        )

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED, 
                    selected_icon=ft.Icons.DASHBOARD, 
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ADD_CARD_OUTLINED, 
                    selected_icon=ft.Icons.ADD_CARD, 
                    label="Lançamentos"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANALYTICS_OUTLINED, 
                    selected_icon=ft.Icons.ANALYTICS, 
                    label="IA Insights"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED, 
                    selected_icon=ft.Icons.SETTINGS, 
                    label="Config"
                ),
            ],
            on_change=self.mudar_pagina
        )

        self.controls = [self.rail, ft.VerticalDivider(width=1), self.content_area]

    # Função auxiliar para gerar a Home com saldo atualizado
    def get_home_content(self):
        
        saldo = get_saldo_total()
        cor_saldo = ft.Colors.GREEN if saldo >= 0 else ft.Colors.RED
        
        return HomePage(self.page)

    def mudar_pagina(self, e):
        index = e.control.selected_index
        
        if index == 0:
            # Ao voltar para home, recarrega o saldo
            self.content_area.content = self.get_home_content()
        elif index == 1:
            self.content_area.content = AddTransactionPage(self)
        elif index == 2:
            self.content_area.content = ft.Text("IA Insights em construção...")
        else:
            self.content_area.content = ft.Text("Configurações em construção...")
            
        self.content_area.update()