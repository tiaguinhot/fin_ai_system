import flet as ft
from ui.components import DonutChart
from database.db_manager import get_saldo_total, get_ultimas_transacoes, deletar_transacao, editar_transacao, get_gastos_por_categoria 

def HomePage(page: ft.Page):
    
    # --- VARIÁVEIS DE EDIÇÃO ---
    edit_id = ft.Text(visible=False)
    edit_desc = ft.TextField(label="Descrição", border=ft.InputBorder.UNDERLINE)
    edit_valor = ft.TextField(label="Valor", keyboard_type=ft.KeyboardType.NUMBER, border=ft.InputBorder.UNDERLINE)
    
    def fechar_dialog(e):
        page.close(dialog_edit)
        page.update()

    def salvar_edicao(e):
        try:
            editar_transacao(int(edit_id.value), edit_desc.value, edit_valor.value)
            page.close(dialog_edit)
            
            # Aqui sim usamos page.update() pois a tela já existe
            carregar_tudo(atualizar_tela=True) 
            
            page.open(ft.SnackBar(ft.Text("Atualizado!"), bgcolor=ft.Colors.GREEN))
            page.update()
        except Exception as ex:
            print(ex)

    dialog_edit = ft.AlertDialog(
        title=ft.Text("Editar", weight="bold"),
        content=ft.Column([edit_desc, edit_valor], tight=True, width=300),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialog),
            ft.ElevatedButton("Salvar", on_click=salvar_edicao),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # --- ELEMENTOS DA UI ---
    txt_saldo = ft.Text("R$ 0,00", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)
    area_grafico = ft.Container()
    
    # Tabela Estilizada
    tabela = ft.DataTable(
        column_spacing=25,
        heading_row_height=40,
        data_row_min_height=50,
        columns=[
            ft.DataColumn(ft.Text("DATA", weight="bold", color=ft.Colors.GREY_600, size=12)),
            ft.DataColumn(ft.Text("CONTA", weight="bold", color=ft.Colors.GREY_600, size=12)),
            ft.DataColumn(ft.Text("CATEGORIA", weight="bold", color=ft.Colors.GREY_600, size=12)),
            ft.DataColumn(ft.Text("DESCRIÇÃO", weight="bold", color=ft.Colors.GREY_600, size=12)),
            ft.DataColumn(ft.Text("VALOR", weight="bold", color=ft.Colors.GREY_600, size=12), numeric=True),
            ft.DataColumn(ft.Text("AÇÕES", weight="bold", color=ft.Colors.GREY_600, size=12)),
        ],
        rows=[]
    )

    # Função Central que carrega tudo
    def carregar_tudo(atualizar_tela=False):
        # 1. Carrega Saldo
        saldo = get_saldo_total()
        txt_saldo.value = f"R$ {saldo:.2f}"
        txt_saldo.color = ft.Colors.BLACK87 if saldo >= 0 else ft.Colors.RED_600
        
        # 2. Carrega Gráfico
        dados_grafico = get_gastos_por_categoria()
        area_grafico.content = DonutChart(dados_grafico)

        # 3. Carrega Transações
        dados = get_ultimas_transacoes(50) 
        tabela.rows = []
        
        for t in dados:
            def on_delete(e, id_t=t['id']):
                deletar_transacao(id_t)
                carregar_tudo(atualizar_tela=True) # Atualiza ao deletar
            
            def on_edit(e, t_data=t):
                edit_id.value = str(t_data['id'])
                edit_desc.value = t_data['descricao']
                edit_valor.value = str(abs(t_data['valor']))
                page.open(dialog_edit) 
                page.update()

            cor_valor = ft.Colors.EMERALD_600 if t['valor'] > 0 else ft.Colors.RED_600
            
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(t['data'], size=13)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(t['conta'], size=11, weight="bold", color=ft.Colors.INDIGO_700),
                            bgcolor=ft.Colors.INDIGO_50,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(t['categoria'], size=11, weight="bold", color=ft.Colors.GREY_700),
                            bgcolor=ft.Colors.GREY_200,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4
                        )),
                        ft.DataCell(ft.Text(t['descricao'], size=13, weight="w500", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(f"R$ {t['valor']:.2f}", color=cor_valor, weight="bold", size=13)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=ft.Colors.GREY_500, icon_size=18, on_click=on_edit),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=18, on_click=on_delete),
                        ], spacing=0)),
                    ]
                )
            )
        
        # O SEGREDO ESTÁ AQUI:
        # Só chamamos page.update() se a tela já estiver renderizada (eventos de clique)
        # Se for a primeira carga, não atualizamos a página (o return fará isso)
        if atualizar_tela:
            page.update()

    # Chamada Inicial (SEM page.update)
    carregar_tudo(atualizar_tela=False)

    return ft.Column(
        expand=True,
        controls=[
            ft.Text("Visão Geral", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            
            # Row contendo Saldo e Gráfico
            ft.Row(
                height=320, 
                controls=[
                    # CARD DE SALDO
                    ft.Container(
                        expand=1, 
                        padding=25,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12),
                        content=ft.Column([
                            ft.Text("Saldo Disponível", size=14, color=ft.Colors.GREY_500),
                            txt_saldo,
                            ft.Container(height=20),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=40, color=ft.Colors.INDIGO_100)
                        ])
                    ),
                    
                    ft.Container(width=20),
                    
                    # CARD DO GRÁFICO
                    ft.Container(
                        expand=1, 
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK12),
                        content=ft.Column([
                            ft.Text("Despesas por Categoria", size=14, weight="bold", color=ft.Colors.GREY_600),
                            area_grafico
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    )
                ]
            ),
            
            ft.Text("Últimas Movimentações", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK87),
            
            # Tabela
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=10,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                content=ft.ListView(controls=[tabela], expand=True, auto_scroll=False)
            )
        ]
    )