import flet as ft
from ui.pages.home import HomePage
from ui.pages.add_transaction import AddTransactionPage
from ui.pages.accounts import AccountsPage
# ADICIONE ESTA LINHA ABAIXO:
from ui.pages.insights import InsightsPage

class AppLayout(ft.Row):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True 
        self.spacing = 0 # Remove espaçamento padrão da linha
        
        # Área de Conteúdo com fundo "Off-White" para contraste
        self.content_area = ft.Container(
            expand=True, 
            padding=30, # Mais margem interna
            bgcolor=ft.Colors.GREY_100, # Fundo cinza claro moderno
            content=self.get_home_content() 
        )

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200, # Um pouco menor para ser mais elegante
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
                ft.NavigationRailDestination(icon=ft.Icons.ADD_CARD_OUTLINED, selected_icon=ft.Icons.ADD_CARD, label="Lançar"),
                ft.NavigationRailDestination(icon=ft.Icons.WALLET_OUTLINED, selected_icon=ft.Icons.WALLET, label="Contas"),
                ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS_OUTLINED, selected_icon=ft.Icons.ANALYTICS, label="Insights"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Config"),
            ],
            on_change=self.mudar_pagina,
            bgcolor=ft.Colors.WHITE, # Menu branco
            # Adiciona uma sombra sutil na direita do menu
            # elevation=5 (o Flet novo controla isso diferente, mas o bgcolor white já ajuda)
        )

        # Removemos o VerticalDivider para ficar mais limpo
        self.controls = [self.rail, self.content_area]

    def get_home_content(self):
        return HomePage(self.page)

    def mudar_pagina(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = self.get_home_content()
        elif index == 1:
            self.content_area.content = AddTransactionPage(self)
        elif index == 2:
            self.content_area.content = AccountsPage(self)
        elif index == 3: # AQUI A MUDANÇA
            self.content_area.content = InsightsPage(self)
        else:
            self.content_area.content = ft.Text("Configurações em construção...")
        self.content_area.update()