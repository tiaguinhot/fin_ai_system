import flet as ft
from database.db_manager import adicionar_conta, get_contas, deletar_conta

def AccountsPage(page_layout):
    
    # --- CAMPOS RESPONSIVOS ---
    nome_field = ft.TextField(
        label="Nome", hint_text="Ex: Nubank", 
        border_radius=8, text_size=14, 
        col={"xs": 12, "md": 8} # Ocupa mais espaço que o tipo
    )
    
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("Corrente"),
            ft.dropdown.Option("Investimento"),
            ft.dropdown.Option("Dinheiro"),
            ft.dropdown.Option("Crédito"),
        ],
        value="Corrente",
        border_radius=8,
        text_size=14,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=10),
        col={"xs": 12, "md": 4}
    )

    fechamento_field = ft.TextField(
        label="Dia Fech.", keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=8, visible=False, hint_text="05", text_size=14,
        col={"xs": 6, "md": 3}
    )
    
    vencimento_field = ft.TextField(
        label="Dia Venc.", keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=8, visible=False, hint_text="10", text_size=14,
        col={"xs": 6, "md": 3}
    )

    def on_saldo_focus(e):
        if saldo_inicial_field.value in ["0,00", "0.00", "0"]:
            saldo_inicial_field.value = ""
            saldo_inicial_field.update()

    def on_saldo_blur(e):
        if saldo_inicial_field.value == "":
            saldo_inicial_field.value = "0,00"
            saldo_inicial_field.update()

    saldo_inicial_field = ft.TextField(
        label="Saldo/Fatura", value="0,00", 
        keyboard_type=ft.KeyboardType.NUMBER, prefix_text="R$ ", 
        border_radius=8, text_size=14,
        helper_text="Use (-) se devendo",
        on_focus=on_saldo_focus, on_blur=on_saldo_blur,
        col={"xs": 12, "md": 6}
    )
    
    # Botão de adicionar também entra na grade
    btn_add = ft.ElevatedButton(
        "Adicionar Conta", 
        icon=ft.Icons.ADD, 
        on_click=lambda e: salvar_click(e),
        style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8), padding=18),
        col={"xs": 12, "md": 6} 
    )

    def on_tipo_change(e):
        tipo = tipo_dropdown.value
        # Mostra/Esconde campos de data
        fechamento_field.visible = (tipo == "Crédito")
        vencimento_field.visible = (tipo == "Crédito")
        
        # Ajusta label
        if tipo == "Crédito":
            saldo_inicial_field.label = "Fatura Atual"
        else:
            saldo_inicial_field.label = "Saldo Inicial"
            
        page_layout.page.update()

    tipo_dropdown.on_change = on_tipo_change

    # --- LISTAGEM ---
    # GridView já é responsivo por natureza (runs_count define colunas fixas, 
    # mas max_extent é melhor para responsividade real)
    lista_contas = ft.GridView(
        expand=True,
        max_extent=300, # Cada card terá no max 300px, cabendo quantos derem na tela
        child_aspect_ratio=2.8, # Formato do card
        spacing=15,
        run_spacing=15,
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
                icone, cor_bg_icone, cor_icone = ft.Icons.MONEY, ft.Colors.GREEN_50, ft.Colors.GREEN
            elif c['tipo'] == "Crédito":
                icone, cor_bg_icone, cor_icone = ft.Icons.CREDIT_CARD, ft.Colors.PURPLE_50, ft.Colors.PURPLE
                if c['dia_fechamento'] and c['dia_vencimento']:
                    subtitulo = f"Fecha dia {c['dia_fechamento']} • Vence {c['dia_vencimento']}"
            elif c['tipo'] == "Investimento":
                icone, cor_bg_icone, cor_icone = ft.Icons.TRENDING_UP, ft.Colors.ORANGE_50, ft.Colors.ORANGE

            def delete_click(e, id_c=c['id']):
                deletar_conta(id_c)
                carregar_contas()
                page_layout.page.open(ft.SnackBar(ft.Text("Conta removida!")))
                page_layout.page.update()

            card = ft.Container(
                padding=15, bgcolor=ft.Colors.WHITE, border_radius=12,
                shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
                content=ft.Row([
                    ft.Container(content=ft.Icon(icone, color=cor_icone, size=24), bgcolor=cor_bg_icone, padding=10, border_radius=10),
                    ft.Column([
                        ft.Text(c['nome'], weight="bold", size=15, color=ft.Colors.BLACK87),
                        ft.Text(subtitulo, color=ft.Colors.GREY_500, size=11),
                    ], expand=True, spacing=1),
                    ft.Column([
                        ft.Text("Saldo", size=10, color=ft.Colors.GREY_400),
                        ft.Text(f"R$ {c['saldo_inicial']:.2f}", weight="bold", size=13, color=ft.Colors.BLACK54),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=20, on_click=delete_click)
                ])
            )
            lista_contas.controls.append(card)
        page_layout.page.update()

    def salvar_click(e):
        if not nome_field.value:
            nome_field.error_text = "*"
            nome_field.update()
            return
        saldo_str = saldo_inicial_field.value.replace(",", ".")
        try: float(saldo_str)
        except: 
            saldo_inicial_field.error_text = "Inválido"
            saldo_inicial_field.update()
            return
        
        try:
            adicionar_conta(nome_field.value, tipo_dropdown.value, saldo_str, fechamento_field.value, vencimento_field.value)
            nome_field.value = ""
            saldo_inicial_field.value = "0,00"
            page_layout.page.open(ft.SnackBar(ft.Text("Conta criada!"), bgcolor=ft.Colors.GREEN_600))
            page_layout.page.update()
            carregar_contas()
        except Exception as ex:
            page_layout.page.open(ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED))

    carregar_contas()

    return ft.Column([
        ft.Text("Carteira", size=24, weight="bold", color=ft.Colors.BLACK87),
        
        # CARD FORMULÁRIO
        ft.Container(
            padding=20, bgcolor=ft.Colors.WHITE, border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
            content=ft.ResponsiveRow( # Grid System aqui
                controls=[
                    nome_field, tipo_dropdown,
                    fechamento_field, vencimento_field,
                    saldo_inicial_field, btn_add
                ],
                vertical_alignment=ft.CrossAxisAlignment.END # Alinha botão com os campos
            )
        ),
        
        ft.Text("Meus Cartões e Contas", size=18, weight="bold", color=ft.Colors.BLACK87),
        ft.Container(expand=True, content=lista_contas)
    ])