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
        return ft.Container(content=ft.Text("Sem gastos no período"), padding=20)

    i = 0
    for cat, valor in gastos_por_categoria.items():
        cor = cores[i % len(cores)]
        porcentagem = (valor / total) * 100
        
        sections.append(
            ft.PieChartSection(
                valor,
                title=f"{porcentagem:.0f}%",
                title_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                color=cor,
                radius=40,
            )
        )
        i += 1

    return ft.Container(
        # height=200, <--- REMOVI A ALTURA FIXA. 
        # Agora ele vai expandir para preencher os 320px do pai que definimos na Home.
        content=ft.PieChart(
            sections=sections,
            sections_space=2,
            center_space_radius=50,
            expand=True
        )
    )