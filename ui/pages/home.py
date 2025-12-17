import flet as ft
from ui.components import DonutChart
from database.db_manager import get_saldo_total, get_ultimas_transacoes, deletar_transacao, editar_transacao, get_gastos_por_categoria 

def HomePage(page: ft.Page):
    
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
    txt_saldo = ft.Text("R$ 0,00", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87) 
    area_grafico = ft.Container()
    
    tabela = ft.DataTable(
        column_spacing=20,
        heading_row_height=35,
        data_row_min_height=45,
        columns=[
            ft.DataColumn(ft.Text("DATA", weight="bold", color=ft.Colors.GREY_600, size=11)),
            ft.DataColumn(ft.Text("CONTA", weight="bold", color=ft.Colors.GREY_600, size=11)),
            ft.DataColumn(ft.Text("CATEGORIA", weight="bold", color=ft.Colors.GREY_600, size=11)),
            ft.DataColumn(ft.Text("DESCRIÇÃO", weight="bold", color=ft.Colors.GREY_600, size=11)),
            ft.DataColumn(ft.Text("VALOR", weight="bold", color=ft.Colors.GREY_600, size=11), numeric=True),
            ft.DataColumn(ft.Text("AÇÕES", weight="bold", color=ft.Colors.GREY_600, size=11)),
        ],
        rows=[]
    )

    def carregar_tudo(atualizar_tela=False):
        saldo = get_saldo_total()
        txt_saldo.value = f"R$ {saldo:.2f}"
        txt_saldo.color = ft.Colors.BLACK87 if saldo >= 0 else ft.Colors.RED_600
        
        dados_grafico = get_gastos_por_categoria()
        area_grafico.content = DonutChart(dados_grafico)

        dados = get_ultimas_transacoes(50) 
        tabela.rows = []
        
        for t in dados:
            def on_delete(e, id_t=t['id']):
                deletar_transacao(id_t)
                carregar_tudo(atualizar_tela=True)
            
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
                        ft.DataCell(ft.Text(t['data'], size=12)),
                        ft.DataCell(ft.Container(
                            content=ft.Text(t['conta'], size=10, weight="bold", color=ft.Colors.INDIGO_700),
                            bgcolor=ft.Colors.INDIGO_50,
                            padding=ft.padding.symmetric(horizontal=6, vertical=3),
                            border_radius=4
                        )),
                        ft.DataCell(ft.Container(
                            content=ft.Text(t['categoria'], size=10, weight="bold", color=ft.Colors.GREY_700),
                            bgcolor=ft.Colors.GREY_200,
                            padding=ft.padding.symmetric(horizontal=6, vertical=3),
                            border_radius=4
                        )),
                        ft.DataCell(ft.Text(t['descricao'], size=12, weight="w500", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(f"R$ {t['valor']:.2f}", color=cor_valor, weight="bold", size=12)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=ft.Colors.GREY_500, icon_size=16, on_click=on_edit),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=16, on_click=on_delete),
                        ], spacing=0)),
                    ]
                )
            )
        
        if atualizar_tela:
            page.update()

    carregar_tudo(atualizar_tela=False)

    return ft.Column(
        expand=True,
        spacing=15, 
        controls=[
            ft.Text("Visão Geral", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            
            ft.Row(
                height=250, 
                controls=[
                    # CARD SALDO
                    ft.Container(
                        expand=1, 
                        padding=20,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column([
                            ft.Text("Saldo Disponível", size=12, color=ft.Colors.GREY_500),
                            txt_saldo,
                            ft.Container(height=10),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=30, color=ft.Colors.INDIGO_100)
                        ], alignment=ft.MainAxisAlignment.CENTER) # Centraliza conteúdo do saldo
                    ),
                    ft.Container(width=15),
                    # CARD GRÁFICO
                    ft.Container(
                        expand=1, 
                        padding=15,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=15,
                        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                        content=ft.Column([
                            ft.Text("Despesas por Categoria", size=12, weight="bold", color=ft.Colors.GREY_600),
                            area_grafico
                        ], 
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER) # Centraliza o gráfico verticalmente
                    )
                ]
            ),
            
            ft.Text("Últimas Movimentações", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.BLACK87),
            
            # Tabela
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=5,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
                content=ft.ListView(controls=[tabela], expand=True, auto_scroll=False)
            )
        ]
    )