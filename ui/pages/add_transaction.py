import flet as ft
from database.db_manager import adicionar_transacao
from ai.brain import classificar_transacao
from datetime import datetime

def AddTransactionPage(page_layout):
    
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False)
    
    # --- CAMPO DE DATA (CORRIGIDO) ---
    def change_date(e):
        # Pega a data escolhida e formata
        if date_picker.value:
            data_field.value = date_picker.value.strftime("%d/%m/%Y")
            data_field.update()

    date_picker = ft.DatePicker(
        on_change=change_date,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31)
    )

    # Botão ícone para abrir o calendário (mais seguro que on_focus)
    botao_data = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda e: page_layout.page.open(date_picker) # NOVA FORMA DE ABRIR
    )

    data_field = ft.TextField(
        label="Data",
        value=datetime.now().strftime("%d/%m/%Y"),
        width=190,
        read_only=True,
        suffix=botao_data # Colocamos o botão dentro do campo
    )
    # ---------------------

    categoria_dropdown = ft.Dropdown(
        width=400,
        label="Categoria (IA)",
        options=[ft.dropdown.Option(x) for x in ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Investimento", "Assinaturas", "Outros"]],
        value="Outros"
    )

    # Lógica da IA
    def on_desc_blur(e):
        if desc_field.value and len(desc_field.value) > 2:
            loading_ring.visible = True
            page_layout.page.update()
            
            sugestao = classificar_transacao(desc_field.value, valor_field.value)
            
            loading_ring.visible = False
            opcoes_texto = [op.key for op in categoria_dropdown.options]
            
            if sugestao in opcoes_texto:
                categoria_dropdown.value = sugestao
            else:
                categoria_dropdown.value = "Outros"
            
            page_layout.page.update()

    desc_field = ft.TextField(label="Descrição", hint_text="Ex: Almoço", width=400, on_blur=on_desc_blur)
    valor_field = ft.TextField(label="Valor (R$)", hint_text="0.00", width=400, keyboard_type=ft.KeyboardType.NUMBER)
    
    tipo_dropdown = ft.Dropdown(
        width=200,
        label="Tipo",
        options=[ft.dropdown.Option("despesa", "Despesa"), ft.dropdown.Option("receita", "Receita")],
        value="despesa"
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
                data_str=data_field.value 
            )
            
            # --- LIMPEZA ---
            desc_field.value = ""
            valor_field.value = ""
            desc_field.error_text = None
            categoria_dropdown.value = "Outros"
            data_field.value = datetime.now().strftime("%d/%m/%Y") 
            
            snack = ft.SnackBar(ft.Text("Sucesso!"), bgcolor=ft.Colors.GREEN)
            page_layout.page.open(snack) # Nova forma de abrir snackbar também
            page_layout.page.update()
            
        except Exception as ex:
            snack = ft.SnackBar(ft.Text(f"Erro: {ex}"), bgcolor=ft.Colors.RED)
            page_layout.page.open(snack)
            page_layout.page.update()

    return ft.Container(
        padding=40,
        content=ft.Column(
            controls=[
                ft.Row([ft.Text("Novo Lançamento", size=25, weight=ft.FontWeight.BOLD), loading_ring]),
                
                ft.Row([data_field, tipo_dropdown]),
                desc_field,
                categoria_dropdown,
                valor_field,
                
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                
                ft.ElevatedButton(
                    text="Salvar Lançamento",
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_800, color=ft.Colors.WHITE, padding=20),
                    on_click=salvar_click,
                    width=200
                )
            ]
        )
    )