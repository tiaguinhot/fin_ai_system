import flet as ft

def DonutChart(gastos_por_categoria):
    sections = []
    cores = [
        ft.Colors.INDIGO, ft.Colors.BLUE, ft.Colors.TEAL, 
        ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.RED_400,
        ft.Colors.CYAN, ft.Colors.AMBER
    ]
    
    total = sum(gastos_por_categoria.values())
    if total == 0:
        return ft.Container(
            content=ft.Text("Sem gastos", color=ft.Colors.GREY_400, size=12),
            alignment=ft.alignment.center,
            height=160
        )

    i = 0
    for cat, valor in gastos_por_categoria.items():
        cor = cores[i % len(cores)]
        porcentagem = (valor / total) * 100
        
        # Oculta fatias muito pequenas para não poluir
        if porcentagem > 2:
            title_text = f"{porcentagem:.0f}%"
        else:
            title_text = ""

        sections.append(
            ft.PieChartSection(
                valor,
                title=title_text,
                title_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                color=cor,
                radius=30, # Reduzido de 40 para 30 (mais fino/compacto)
            )
        )
        i += 1

    return ft.Container(
        height=160, # Altura fixa para garantir que cabe no card
        content=ft.PieChart(
            sections=sections,
            sections_space=2,
            center_space_radius=40, # Reduzido de 50 para 40
            expand=True
        )
    )