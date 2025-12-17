import flet as ft
from database.db_manager import get_resumo_financeiro
from ai.brain import gerar_analise_financeira
import threading # Importante para não travar a tela

def InsightsPage(page_layout):
    
    resultado_markdown = ft.Markdown(
        value="Clique no botão para gerar uma análise do seu perfil financeiro...",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        on_tap_link=lambda e: page_layout.page.launch_url(e.data),
    )
    
    loading = ft.ProgressBar(width=400, color=ft.Colors.INDIGO, bgcolor=ft.Colors.INDIGO_100, visible=False)
    
    btn_gerar = ft.ElevatedButton(
        text="Gerar Análise com IA",
        icon=ft.Icons.AUTO_AWESOME,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.INDIGO,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    # Função que roda em segundo plano (Worker)
    def tarefa_ia():
        try:
            # 1. Busca dados e chama IA (Isso demora)
            dados = get_resumo_financeiro()
            analise = gerar_analise_financeira(dados)
            
            # 2. Atualiza a tela (Volta para o contexto visual)
            resultado_markdown.value = analise
        except Exception as ex:
            resultado_markdown.value = f"Ocorreu um erro: {ex}"
        
        # 3. Desliga o loading e habilita o botão
        loading.visible = False
        btn_gerar.disabled = False
        page_layout.page.update()

    def gerar_click(e):
        # Prepara a tela (Mostra loading)
        btn_gerar.disabled = True
        loading.visible = True
        resultado_markdown.value = "Analisando seus dados (pode levar alguns segundos)..."
        page_layout.page.update()
        
        # Inicia a tarefa em paralelo sem travar a janela
        threading.Thread(target=tarefa_ia).start()

    btn_gerar.on_click = gerar_click

    return ft.Column(
        expand=True,
        controls=[
            ft.Text("IA Financial Advisor", size=28, weight="bold", color=ft.Colors.BLACK87),
            ft.Text("Descubra padrões ocultos nos seus gastos.", size=14, color=ft.Colors.GREY_500),
            
            ft.Container(height=20),
            
            ft.Container(
                content=ft.Column([
                    btn_gerar,
                    ft.Container(height=10),
                    loading
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=20),
            
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=30,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row([ft.Icon(ft.Icons.ANALYTICS, color=ft.Colors.INDIGO), ft.Text(" Relatório Gerado", weight="bold")], spacing=10),
                        ft.Divider(),
                        resultado_markdown
                    ]
                )
            )
        ]
    )