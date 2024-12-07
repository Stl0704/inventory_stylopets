from django.shortcuts import render
import pandas as pd
from inventory.models import *
from plotly.graph_objs import Figure, Bar, Pie

# RENDER DASHBOARD


def dashView(request):
    # Datos para el primer gráfico - Cantidad Total de Ingresos por Fecha
    ingresos = HistorialIngresosTests.objects.all()

    if ingresos.exists():
        # Contar la cantidad total de ingresos
        ingresos_data = {
            'Fecha': [ingreso.fecha.date() for ingreso in ingresos],
        }
        df_ingresos = pd.DataFrame(ingresos_data)
        df_ingresos['Cantidad'] = 1  # Cada ingreso cuenta como 1

        # Agrupar los ingresos por fecha
        df_ingresos_agrupados = df_ingresos.groupby(
            'Fecha').sum().reset_index()

        # Crear gráfico de barras con un efecto 3D
        fig1 = Figure(
            data=[
                Bar(
                    x=df_ingresos_agrupados['Fecha'],
                    y=df_ingresos_agrupados['Cantidad'],
                    marker=dict(color='rgba(55, 128, 191, 0.7)', line=dict(
                        color='rgba(55, 128, 191, 1.0)', width=2)),
                    width=0.5
                )
            ],
            layout=dict(
                title='Cantidad de Ingresos por Fecha',
                scene=dict(
                    xaxis_title='Fecha',
                    yaxis_title='Cantidad',
                )
            )
        )
        graph1_html = fig1.to_html(full_html=False)
    else:
        graph1_html = "<p>No hay datos de ingresos disponibles.</p>"

    # Datos para el segundo gráfico - Stock Actual por Categoría
    productos = ProductoTests.objects.all()

    if productos.exists():
        # Convertir los datos a un DataFrame de Pandas
        productos_data = {
            'Categoría': [producto.Categoria for producto in productos],
            'Stock': [producto.Stock for producto in productos]
        }
        df_productos = pd.DataFrame(productos_data)

        # Agrupar el stock por categoría
        df_stock_categoria = df_productos.groupby(
            'Categoría').sum().reset_index()

        # Crear gráfico circular (pie chart) con efecto tridimensional
        fig2 = Figure(
            data=[
                Pie(
                    labels=df_stock_categoria['Categoría'],
                    values=df_stock_categoria['Stock'],
                    hole=0.3,
                    marker=dict(
                        line=dict(color='rgba(255, 255, 255, 1.0)', width=2),
                        colors=['#EF553B', '#00CC96', '#636EFA', '#AB63FA']
                    )
                )
            ],
            layout=dict(
                title='Stock Actual por Categoría'
            )
        )
        graph2_html = fig2.to_html(full_html=False)
    else:
        graph2_html = "<p>No hay datos de productos disponibles.</p>"

    # Pasar los gráficos al contexto de la plantilla
    context = {
        'graph1_html': graph1_html,
        'graph2_html': graph2_html
    }

    return render(request, 'dashboard.html', context)
