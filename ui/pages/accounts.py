import flet as ft
from database.db_manager import adicionar_conta, get_contas, deletar_conta

def AccountsPage(page_layout):
    
    nome_field = ft.TextField(
        label="Nome", 
        hint_text="Ex: Nubank", 
        expand=True, 
        border_radius=8, 
        text_size=14, 
        height=45
    )
    
    # --- LÓGICA DE LIMPEZA E FOCO (IGUAL AO ADD_TRANSACTION) ---
    def on_saldo_focus(e):
        # Limpa se for zero para facilitar digitação
        if saldo_inicial_field.value in ["0,00", "0.00", "0"]:
            saldo_inicial_field.value = ""
            saldo_inicial_field.update()

    def on_saldo_blur(e):
        # Se vazio, volta zero
        if saldo_inicial_field.value == "":
            saldo_inicial_field.value = "0,00"
            saldo_inicial_field.update()

    saldo_inicial_field = ft.TextField(
        label="Saldo/Fatura", 
        value="0,00", 
        width=180, 
        keyboard_type=ft.KeyboardType.NUMBER, 
        prefix_text="R$ ", 
        border_radius=8,
        text_size=14,
        height=45,
        helper_text="Use (-) se devendo",
        on_focus=on_saldo_focus,
        on_blur=on_saldo_blur
    )
    
    fechamento_field = ft.TextField(
        label="Dia Fech.", width=100, keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=8, visible=False, hint_text="05", height=45, text_size=14
    )
    
    vencimento_field = ft.TextField(
        label="Dia Venc.", width=100, keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=8, visible=False, hint_text="10", height=45, text_size=14
    )

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

    # --- CORREÇÃO AQUI: REMOVIDO 'HEIGHT' E ADICIONADO 'CONTENT_PADDING' ---
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        width=130,
        options=[
            ft.dropdown.Option("Corrente"),
            ft.dropdown.Option("Investimento"),
            ft.dropdown.Option("Dinheiro"),
            ft.dropdown.Option("Crédito"),
        ],
        value="Corrente",
        border_radius=8,
        text_size=14,
        # height=45,  <-- REMOVIDO PQ CAUSAVA O ERRO
        content_padding=ft.padding.only(left=10, right=10, top=10, bottom=10), # Ajuste visual
        on_change=on_tipo_change
    )

    lista_contas = ft.GridView(
        runs_count=2,
        child_aspect_ratio=3.0,
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
                    subtitulo = f"Fecha dia {c['dia_fechamento']} • Vence {c['dia_vencimento']}"
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
                padding=12,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=4, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)),
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icone, color=cor_icone, size=20),
                        bgcolor=cor_bg_icone,
                        padding=8,
                        border_radius=8
                    ),
                    ft.Column([
                        ft.Text(c['nome'], weight="bold", size=14, color=ft.Colors.BLACK87),
                        ft.Text(subtitulo, color=ft.Colors.GREY_500, size=10),
                    ], expand=True, spacing=1),
                    
                    ft.Column([
                        ft.Text("Saldo", size=9, color=ft.Colors.GREY_400),
                        ft.Text(f"R$ {c['saldo_inicial']:.2f}", weight="bold", size=12, color=ft.Colors.BLACK54),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END),
                    
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=18, on_click=delete_click)
                ])
            )
            lista_contas.controls.append(card)
        
        page_layout.page.update()

    def salvar_click(e):
        if not nome_field.value:
            nome_field.error_text = "*"
            nome_field.update()
            return
        
        # Tratamento da vírgula
        saldo_str = saldo_inicial_field.value.replace(",", ".")
        try:
            float(saldo_str)
        except:
            saldo_inicial_field.error_text = "Inválido"
            saldo_inicial_field.update()
            return
        
        try:
            adicionar_conta(
                nome=nome_field.value, 
                tipo=tipo_dropdown.value, 
                saldo_inicial=saldo_str, # Passa o valor com ponto
                dia_fechamento=fechamento_field.value,
                dia_vencimento=vencimento_field.value
            )
            nome_field.value = ""
            saldo_inicial_field.value = "0,00"
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
        ft.Text("Carteira", size=22, weight="bold", color=ft.Colors.BLACK87),
        
        ft.Container(
            margin=ft.margin.only(top=5, bottom=15),
            padding=15, 
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
            content=ft.Column([
                ft.Text("Adicionar Conta", weight="bold", size=14, color=ft.Colors.INDIGO),
                
                ft.Row([nome_field, tipo_dropdown], vertical_alignment=ft.CrossAxisAlignment.START),
                
                ft.Container(height=5),
                
                ft.Row([fechamento_field, vencimento_field], vertical_alignment=ft.CrossAxisAlignment.START),
                
                ft.Container(height=5),
                
                ft.Row([
                    saldo_inicial_field,
                    ft.Container(expand=True), 
                    ft.ElevatedButton(
                        "Adicionar", 
                        icon=ft.Icons.ADD, 
                        on_click=salvar_click,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8), padding=15)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ])
        ),
        
        ft.Text("Meus Cartões e Contas", size=16, weight="bold", color=ft.Colors.BLACK87),
        
        ft.Container(expand=True, content=lista_contas)
    ])