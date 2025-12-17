import flet as ft
from database.db_manager import adicionar_transacao, get_contas, get_todas_categorias
from ai.brain import classificar_transacao
from datetime import datetime

def AddTransactionPage(page_layout):
    
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False, color=ft.Colors.INDIGO)
    
    # --- DATA ---
    def change_date(e):
        if date_picker.value:
            data_field.value = date_picker.value.strftime("%d/%m/%Y")
            data_field.update()

    date_picker = ft.DatePicker(
        on_change=change_date,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31)
    )

    botao_data = ft.IconButton(
        icon=ft.Icons.CALENDAR_TODAY,
        icon_color=ft.Colors.INDIGO,
        on_click=lambda e: page_layout.page.open(date_picker)
    )

    data_field = ft.TextField(
        label="Data",
        value=datetime.now().strftime("%d/%m/%Y"),
        width=160,
        read_only=True,
        suffix=botao_data,
        border_radius=8,
        text_size=14
    )
    
    # --- CONTA ---
    opcoes_contas = []
    dados_contas = get_contas()
    if dados_contas:
        for c in dados_contas:
            opcoes_contas.append(ft.dropdown.Option(c['nome']))
        valor_padrao_conta = dados_contas[0]['nome']
    else:
        opcoes_contas.append(ft.dropdown.Option("Sem Conta"))
        valor_padrao_conta = "Sem Conta"

    conta_dropdown = ft.Dropdown(
        width=220,
        label="Conta / Cartão",
        options=opcoes_contas,
        value=valor_padrao_conta,
        icon=ft.Icons.WALLET,
        border_radius=8,
        text_size=14
    )

    # --- CATEGORIA ---
    cats_db = get_todas_categorias()
    if not cats_db:
        cats_db = ["Alimentação", "Transporte", "Moradia", "Lazer", "Outros"]
    
    categoria_dropdown = ft.Dropdown(
        expand=True,
        label="Categoria (IA)",
        options=[ft.dropdown.Option(x) for x in cats_db],
        value="Outros",
        border_radius=8,
        text_size=14
    )

    def on_desc_blur(e):
        if desc_field.value and len(desc_field.value) > 2:
            loading_ring.visible = True
            page_layout.page.update()
            
            lista_atual = [op.key for op in categoria_dropdown.options]
            sugestao = classificar_transacao(desc_field.value, valor_field.value, lista_atual)
            
            loading_ring.visible = False
            
            existe = False
            for op in categoria_dropdown.options:
                if op.key.lower() == sugestao.lower():
                    categoria_dropdown.value = op.key
                    existe = True
                    break
            
            if not existe:
                nova_op = ft.dropdown.Option(sugestao)
                categoria_dropdown.options.append(nova_op)
                categoria_dropdown.value = sugestao
            
            page_layout.page.update()

    desc_field = ft.TextField(
        label="Descrição", 
        hint_text="Ex: TV Nova", 
        expand=True,
        on_blur=on_desc_blur,
        border_radius=8
    )
    
    # --- VALOR E PARCELAS ---
    valor_field = ft.TextField(
        label="Valor Total (R$)", 
        hint_text="0.00", 
        width=200, 
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        prefix_text="R$ "
    )

    # Campo de Parcelas (Começa com 1x)
    parcelas_field = ft.TextField(
        label="Parcelas",
        value="1",
        width=100,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        text_align=ft.TextAlign.CENTER,
        suffix_text="x"
    )
    
    tipo_dropdown = ft.Dropdown(
        width=150,
        label="Tipo",
        options=[ft.dropdown.Option("despesa", "Despesa"), ft.dropdown.Option("receita", "Receita")],
        value="despesa",
        border_radius=8
    )

    def salvar_click(e):
        if not desc_field.value or not valor_field.value:
            desc_field.error_text = "Obrigatório"
            desc_field.update()
            return
        
        try:
            adicionar_transacao(
                descricao=desc_field.value, 
                valor=valor_field.value, 
                tipo=tipo_dropdown.value,
                categoria_nome=categoria_dropdown.value,
                conta_nome=conta_dropdown.value,
                data_str=data_field.value,
                num_parcelas=parcelas_field.value # Passamos as parcelas
            )
            
            # Limpeza
            desc_field.value = ""
            valor_field.value = ""
            parcelas_field.value = "1"
            desc_field.error_text = None
            categoria_dropdown.value = "Outros"
            data_field.value = datetime.now().strftime("%d/%m/%Y") 
            
            snack = ft.SnackBar(ft.Text("Lançamento Salvo!"), bgcolor=ft.Colors.GREEN_600)
            page_layout.page.open(snack)
            page_layout.page.update()
            
        except Exception as ex:
            snack = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED)
            page_layout.page.open(snack)
            page_layout.page.update()

    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Novo Lançamento", size=24, weight="bold", color=ft.Colors.BLACK87),
            ft.Container(height=20),
            
            ft.Container(
                padding=30,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                width=700,
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12, offset=ft.Offset(0, 5)),
                content=ft.Column(
                    spacing=20,
                    controls=[
                        ft.Row([data_field, ft.Container(width=10), conta_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Row([desc_field, loading_ring]),
                        categoria_dropdown,
                        
                        # LINHA DO VALOR + PARCELAS + TIPO
                        ft.Row([
                            valor_field, 
                            ft.Container(width=10), 
                            parcelas_field, # Campo Novo
                            ft.Container(width=10), 
                            tipo_dropdown
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                        
                        ft.ElevatedButton(
                            text="Confirmar Lançamento",
                            icon=ft.Icons.CHECK,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.INDIGO, 
                                color=ft.Colors.WHITE, 
                                padding=20,
                                shape=ft.RoundedRectangleBorder(radius=10)
                            ),
                            on_click=salvar_click,
                            width=300
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        ]
    )