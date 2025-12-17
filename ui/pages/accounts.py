import flet as ft
from database.db_manager import adicionar_conta, get_contas, deletar_conta

def AccountsPage(page_layout):
    
    nome_field = ft.TextField(label="Nome", hint_text="Ex: Nubank", expand=True, border_radius=8)
    
    # CORREÇÃO 1: Label curto e helper_text para a explicação não quebrar o layout
    saldo_inicial_field = ft.TextField(
        label="Saldo ou Fatura", 
        value="0.00", 
        width=200, # Um pouco mais largo
        keyboard_type=ft.KeyboardType.NUMBER, 
        prefix_text="R$ ", 
        border_radius=8,
        helper_text="Use negativo (-) se estiver devendo" # Texto de ajuda aqui
    )
    
    fechamento_field = ft.TextField(label="Dia Fechamento", width=140, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, visible=False, hint_text="Ex: 5")
    vencimento_field = ft.TextField(label="Dia Vencimento", width=140, keyboard_type=ft.KeyboardType.NUMBER, border_radius=8, visible=False, hint_text="Ex: 10")

    def on_tipo_change(e):
        tipo = tipo_dropdown.value
        if tipo == "Crédito":
            fechamento_field.visible = True
            vencimento_field.visible = True
            saldo_inicial_field.label = "Fatura Atual"
        else:
            fechamento_field.visible = False
            vencimento_field.visible = False
            saldo_inicial_field.label = "Saldo Inicial"
        page_layout.page.update()

    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        width=150,
        options=[
            ft.dropdown.Option("Corrente"),
            ft.dropdown.Option("Investimento"),
            ft.dropdown.Option("Dinheiro"),
            ft.dropdown.Option("Crédito"),
        ],
        value="Corrente",
        border_radius=8,
        on_change=on_tipo_change
    )

    lista_contas = ft.GridView(
        runs_count=2,
        child_aspect_ratio=2.5,
        spacing=10,
        run_spacing=10,
    )

    def carregar_contas():
        lista_contas.controls.clear()
        dados = get_contas()
        
        for c in dados:
            icone = ft.Icons.ACCOUNT_BALANCE_WALLET
            cor_bg_icone = ft.Colors.BLUE_50
            cor_icone = ft.Colors.BLUE
            
            subtitulo = c['tipo']
            
            if c['tipo'] == "Dinheiro":
                icone = ft.Icons.MONEY
                cor_bg_icone = ft.Colors.GREEN_50
                cor_icone = ft.Colors.GREEN
            elif c['tipo'] == "Crédito":
                icone = ft.Icons.CREDIT_CARD
                cor_bg_icone = ft.Colors.PURPLE_50
                cor_icone = ft.Colors.PURPLE
                if c['dia_fechamento'] and c['dia_vencimento']:
                    subtitulo = f"Fecha dia {c['dia_fechamento']} • Vence dia {c['dia_vencimento']}"
            elif c['tipo'] == "Investimento":
                icone = ft.Icons.TRENDING_UP
                cor_bg_icone = ft.Colors.ORANGE_50
                cor_icone = ft.Colors.ORANGE

            def delete_click(e, id_c=c['id']):
                deletar_conta(id_c)
                carregar_contas()
                page_layout.page.open(ft.SnackBar(ft.Text("Conta removida!")))
                page_layout.page.update()

            card = ft.Container(
                padding=15,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icone, color=cor_icone, size=24),
                        bgcolor=cor_bg_icone,
                        padding=10,
                        border_radius=10
                    ),
                    ft.Column([
                        ft.Text(c['nome'], weight="bold", size=15, color=ft.Colors.BLACK87),
                        ft.Text(subtitulo, color=ft.Colors.GREY_500, size=11),
                    ], expand=True, spacing=2),
                    
                    ft.Column([
                        ft.Text("Saldo/Fatura", size=10, color=ft.Colors.GREY_400),
                        ft.Text(f"R$ {c['saldo_inicial']:.2f}", weight="bold", color=ft.Colors.BLACK54),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END),
                    
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=20, on_click=delete_click)
                ])
            )
            lista_contas.controls.append(card)
        
        page_layout.page.update()

    def salvar_click(e):
        if not nome_field.value:
            nome_field.error_text = "Obrigatório"
            nome_field.update()
            return
        
        try:
            adicionar_conta(
                nome=nome_field.value, 
                tipo=tipo_dropdown.value, 
                saldo_inicial=saldo_inicial_field.value,
                dia_fechamento=fechamento_field.value,
                dia_vencimento=vencimento_field.value
            )
            nome_field.value = ""
            saldo_inicial_field.value = "0.00"
            fechamento_field.value = ""
            vencimento_field.value = ""
            nome_field.error_text = None
            page_layout.page.open(ft.SnackBar(ft.Text("Conta criada!"), bgcolor=ft.Colors.GREEN_600))
            page_layout.page.update()
            carregar_contas()
        except Exception as ex:
            page_layout.page.open(ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED))

    carregar_contas()

    return ft.Column([
        ft.Text("Carteira", size=24, weight="bold", color=ft.Colors.BLACK87),
        
        ft.Container(
            margin=ft.margin.only(top=10, bottom=20),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            content=ft.Column([
                ft.Text("Adicionar Nova Conta", weight="bold", color=ft.Colors.INDIGO),
                
                # CORREÇÃO 2: Adicionamos Containers de altura (15) entre as linhas para dar respiro
                ft.Row([nome_field, tipo_dropdown], vertical_alignment=ft.CrossAxisAlignment.START),
                
                ft.Container(height=15), 
                
                ft.Row([fechamento_field, vencimento_field], vertical_alignment=ft.CrossAxisAlignment.START),
                
                ft.Container(height=15),
                
                ft.Row([
                    saldo_inicial_field,
                    ft.Container(expand=True), 
                    ft.ElevatedButton(
                        "Adicionar", 
                        icon=ft.Icons.ADD, 
                        on_click=salvar_click,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        ),
        
        ft.Text("Meus Cartões e Contas", size=18, weight="bold", color=ft.Colors.BLACK87),
        
        ft.Container(expand=True, content=lista_contas)
    ])