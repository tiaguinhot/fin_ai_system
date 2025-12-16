import flet as ft
from database.db_manager import get_saldo_total, get_ultimas_transacoes, deletar_transacao, editar_transacao

def HomePage(page: ft.Page):
    
    # --- DIALOG DE EDIÇÃO (Mesma lógica de antes) ---
    edit_id = ft.Text(visible=False)
    edit_desc = ft.TextField(label="Nova Descrição")
    edit_valor = ft.TextField(label="Novo Valor", keyboard_type=ft.KeyboardType.NUMBER)
    
    def fechar_dialog(e):
        page.close(dialog_edit)
        page.update()

    def salvar_edicao(e):
        try:
            editar_transacao(int(edit_id.value), edit_desc.value, edit_valor.value)
            page.close(dialog_edit)
            atualizar_dados() 
            page.open(ft.SnackBar(ft.Text("Atualizado!"), bgcolor=ft.Colors.GREEN))
            page.update()
        except Exception as ex:
            print(ex)

    dialog_edit = ft.AlertDialog(
        title=ft.Text("Editar Transação"),
        content=ft.Column([edit_desc, edit_valor], tight=True, width=300),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialog),
            ft.ElevatedButton("Salvar", on_click=salvar_edicao),
        ],
    )
    # ---------------------------------------------

    txt_saldo = ft.Text("R$ 0,00", size=30, weight=ft.FontWeight.BOLD)
    
    # Tabela agora configurada para ter rolagem interna se necessário
    tabela = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Data")),
            ft.DataColumn(ft.Text("Categoria")),
            ft.DataColumn(ft.Text("Descrição")),
            ft.DataColumn(ft.Text("Valor"), numeric=True),
            ft.DataColumn(ft.Text("Ações")),
        ],
        rows=[]
    )

    def carregar_transacoes():
        # ALTERAÇÃO 1: Aumentei o limite para 50 lançamentos
        dados = get_ultimas_transacoes(50) 
        tabela.rows = []
        
        for t in dados:
            def on_delete(e, id_t=t['id']):
                deletar_transacao(id_t)
                atualizar_dados()
            
            def on_edit(e, t_data=t):
                edit_id.value = str(t_data['id'])
                edit_desc.value = t_data['descricao']
                edit_valor.value = str(abs(t_data['valor']))
                page.open(dialog_edit) 
                page.update()

            cor_valor = ft.Colors.GREEN if t['valor'] > 0 else ft.Colors.RED_300
            
            tabela.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(t['data'])),
                        ft.DataCell(ft.Container(
                            content=ft.Text(t['categoria'], size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.WHITE10,
                            padding=5,
                            border_radius=5
                        )),
                        # Texto da descrição truncado se for muito longo
                        ft.DataCell(ft.Text(t['descricao'], max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(f"R$ {t['valor']:.2f}", color=cor_valor)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=on_edit),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=on_delete),
                        ])),
                    ]
                )
            )

    def atualizar_dados():
        saldo = get_saldo_total()
        txt_saldo.value = f"R$ {saldo:.2f}"
        txt_saldo.color = ft.Colors.GREEN if saldo >= 0 else ft.Colors.RED
        carregar_transacoes()
        page.update()

    atualizar_dados()

    # LAYOUT FINAL
    return ft.Container(
        padding=20,
        content=ft.Column(
            expand=True, # IMPORTANTE: Ocupa toda a altura disponível
            controls=[
                ft.Text("Dashboard", size=30, weight=ft.FontWeight.BOLD),
                
                # Card Saldo (Fixo no topo)
                ft.Container(
                    margin=ft.margin.only(top=10, bottom=10),
                    padding=20,
                    bgcolor=ft.Colors.GREY_900,
                    border_radius=10,
                    content=ft.Column([
                        ft.Text("Saldo Atual", size=14, color=ft.Colors.WHITE70),
                        txt_saldo,
                    ])
                ),
                
                ft.Text("Histórico (Últimos 50)", size=20, weight=ft.FontWeight.W_600),
                
                # Container da Tabela com SCROLL ativado
                ft.Container(
                    expand=True, # Ocupa o resto do espaço para baixo
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=10,
                    padding=10,
                    # ALTERAÇÃO 2: ListView permite rolar a tabela infinitamente
                    content=ft.ListView(
                        controls=[tabela],
                        expand=True,
                        auto_scroll=False
                    )
                )
            ]
        )
    )