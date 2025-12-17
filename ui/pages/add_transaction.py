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
        last_date=datetime(2030, 12, 31),
        cancel_text="Cancelar",
        confirm_text="Confirmar",
        help_text="Selecione a data"
    )

    botao_data = ft.IconButton(
        icon=ft.Icons.CALENDAR_TODAY,
        icon_color=ft.Colors.INDIGO,
        on_click=lambda e: page_layout.page.open(date_picker)
    )

    data_field = ft.TextField(
        label="Data",
        value=datetime.now().strftime("%d/%m/%Y"),
        read_only=True,
        suffix=botao_data,
        border_radius=8,
        text_size=14,
        col={"xs": 12, "md": 6} # Metade da tela no PC, inteira no Celular
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
        label="Conta / Cartão",
        options=opcoes_contas,
        value=valor_padrao_conta,
        icon=ft.Icons.WALLET,
        border_radius=8,
        text_size=14,
        col={"xs": 12, "md": 6} # Metade da tela no PC
    )

    # --- CATEGORIA ---
    categoria_field = ft.TextField(
        label="Categoria (IA ou Digite)",
        value="Outros",
        border_radius=8,
        text_size=14,
        hint_text="Ex: Salário, Mercado...",
        col={"xs": 12} # Linha inteira
    )

    # --- VALOR ---
    def on_valor_focus(e):
        if valor_field.value in ["0,00", "0.00", "0"]:
            valor_field.value = ""
            valor_field.update()

    def on_valor_blur(e):
        if valor_field.value == "":
            valor_field.value = "0,00"
            valor_field.update()

    valor_field = ft.TextField(
        label="Valor (R$)", 
        value="0,00", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=8,
        prefix_text="R$ ",
        on_focus=on_valor_focus,
        on_blur=on_valor_blur,
        col={"xs": 12, "md": 4} # 1/3 da linha no PC
    )

    # --- DESCRICAO & IA ---
    def on_desc_blur(e):
        if desc_field.value and len(desc_field.value) > 2:
            loading_ring.visible = True
            page_layout.page.update()
            
            cats_existentes = get_todas_categorias()
            if not cats_existentes:
                 cats_existentes = ["Alimentação", "Transporte", "Lazer", "Salário"]

            val_temp = valor_field.value.replace(",", ".") if valor_field.value else "0"
            sugestao = classificar_transacao(desc_field.value, val_temp, cats_existentes)
            
            loading_ring.visible = False
            categoria_field.value = sugestao
            
            snack_text = f"Categoria sugerida: {sugestao}"
            page_layout.page.open(ft.SnackBar(ft.Text(snack_text), duration=2000))
            page_layout.page.update()

    desc_field = ft.TextField(
        label="Descrição", 
        hint_text="Ex: Salário Mensal", 
        on_blur=on_desc_blur,
        border_radius=8,
        suffix=loading_ring,
        col={"xs": 12} # Linha inteira
    )

    parcelas_field = ft.TextField(
        label="Parcelas",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        text_align=ft.TextAlign.CENTER,
        suffix_text="x",
        col={"xs": 6, "md": 4} # Metade no celular, 1/3 no PC
    )
    
    tipo_dropdown = ft.Dropdown(
        label="Tipo",
        options=[ft.dropdown.Option("despesa", "Despesa"), ft.dropdown.Option("receita", "Receita")],
        value="despesa",
        border_radius=8,
        col={"xs": 6, "md": 4} # Metade no celular, 1/3 no PC
    )

    def salvar_click(e):
        if not desc_field.value or not valor_field.value:
            desc_field.error_text = "Obrigatório"
            desc_field.update()
            return
        
        valor_str = valor_field.value
        valor_formatado = valor_str.replace(",", ".")
        
        try:
            float(valor_formatado)
        except ValueError:
            valor_field.error_text = "Valor inválido"
            valor_field.update()
            return

        try:
            adicionar_transacao(
                descricao=desc_field.value, 
                valor=valor_formatado, 
                tipo=tipo_dropdown.value,
                categoria_nome=categoria_field.value, 
                conta_nome=conta_dropdown.value,
                data_str=data_field.value,
                num_parcelas=parcelas_field.value
            )
            
            desc_field.value = ""
            valor_field.value = "0,00"
            parcelas_field.value = "1"
            desc_field.error_text = None
            valor_field.error_text = None
            categoria_field.value = "Outros"
            data_field.value = datetime.now().strftime("%d/%m/%Y") 
            
            snack = ft.SnackBar(ft.Text("Lançamento Salvo!"), bgcolor=ft.Colors.GREEN_600)
            page_layout.page.open(snack)
            page_layout.page.update()
            
        except Exception as ex:
            snack = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED)
            page_layout.page.open(snack)
            page_layout.page.update()

    # --- LAYOUT DINÂMICO ---
    # Usamos ResponsiveRow para o formulário se adaptar
    formulario = ft.ResponsiveRow(
        controls=[
            data_field,
            conta_dropdown,
            desc_field,
            categoria_field,
            valor_field,
            parcelas_field,
            tipo_dropdown
        ],
        spacing=20,
        run_spacing=20
    )

    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Novo Lançamento", size=24, weight="bold", color=ft.Colors.BLACK87),
            ft.Container(height=10),
            
            ft.Container(
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                # Largura máxima limitada para não ficar "esticado demais" em monitores gigantes
                # mas flexível em menores
                width=800, 
                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK12, offset=ft.Offset(0, 5)),
                content=ft.Column([
                    formulario,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
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
                        width=300 # Botão mantém tamanho fixo para elegância
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        ]
    )