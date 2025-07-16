import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar

COLORES_ROOMMATES = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
    '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f'
]

def get_roommate_color(roommate_nombre, roommates_list):
    try:
        index = [rm.nombre for rm in roommates_list].index(roommate_nombre)
        return COLORES_ROOMMATES[index % len(COLORES_ROOMMATES)]
    except (ValueError, IndexError):
        return '#95a5a6'

def crear_calendario_visual():
    if not st.session_state.cronograma:
        st.warning("No hay cronograma para mostrar")
        return
    
    st.subheader("📅 Calendario Semanal")
    
    cronograma = st.session_state.cronograma
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas = list(range(6, 23))
    
    calendario_data = []
    
    for hora in horas:
        fila = {'Hora': f"{hora:02d}:00 - {hora+1:02d}:00"}
        
        for dia in dias:
            tareas_slot = []
            
            for key, asig in cronograma.items():
                if (asig['dia'] == dia and 
                    asig['hora'] <= hora < asig['hora'] + (asig['duracion'] / 60)):
                    
                    color = get_roommate_color(asig['roommate'], st.session_state.roommates)
                    tareas_slot.append({
                        'tarea': asig['tarea'],
                        'roommate': asig['roommate'],
                        'color': color
                    })
            
            if tareas_slot:
                contenido = tareas_slot[0]
                fila[dia] = contenido
            else:
                fila[dia] = None
        
        calendario_data.append(fila)
    
    mostrar_calendario_html(calendario_data, dias)
    mostrar_leyenda_colores()

def mostrar_calendario_html(calendario_data, dias):
    css_calendario = """
    <style>
    .calendario-container {
        width: 100%;
        margin: 20px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .calendario-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .calendario-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #ddd;
    }
    
    .calendario-table td {
        border: 1px solid #e0e0e0;
        padding: 8px;
        height: 60px;
        vertical-align: middle;
        text-align: center;
        font-size: 12px;
        position: relative;
    }
    
    .hora-column {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 120px;
        text-align: center;
    }
    
    .tarea-block {
        background: {color};
        color: white;
        padding: 4px 6px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 500;
        line-height: 1.2;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        margin: 1px;
        display: block;
        word-wrap: break-word;
        hyphens: auto;
    }
    
    .empty-slot {
        background: #f8f9fa;
        height: 100%;
    }
    
    .calendario-table tr:hover {
        background-color: #f5f5f5;
    }
    
    .calendario-table td:hover {
        background-color: #e3f2fd;
        cursor: pointer;
    }
    </style>
    """
    
    html_calendario = css_calendario + '<div class="calendario-container">'
    html_calendario += '<table class="calendario-table">'
    
    html_calendario += '<thead><tr>'
    html_calendario += '<th class="hora-column">Hora</th>'
    for dia in dias:
        html_calendario += f'<th>{dia}</th>'
    html_calendario += '</tr></thead>'
    
    html_calendario += '<tbody>'
    for fila in calendario_data:
        html_calendario += '<tr>'
        html_calendario += f'<td class="hora-column">{fila["Hora"]}</td>'
        
        for dia in dias:
            html_calendario += '<td>'
            
            if fila[dia] is not None:
                tarea_info = fila[dia]
                color = tarea_info['color']
                
                bloque_html = f'''
                <div class="tarea-block" style="background: {color};">
                    <div style="font-weight: bold; margin-bottom: 2px;">{tarea_info['tarea']}</div>
                    <div style="font-size: 10px; opacity: 0.9;">👤 {tarea_info['roommate']}</div>
                </div>
                '''
                html_calendario += bloque_html
            else:
                html_calendario += '<div class="empty-slot"></div>'
            
            html_calendario += '</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</tbody></table></div>'
    
    st.markdown(html_calendario, unsafe_allow_html=True)

def mostrar_leyenda_colores():
    st.subheader("🎨 Leyenda de Colores")
    
    cols = st.columns(len(st.session_state.roommates))
    
    for i, roommate in enumerate(st.session_state.roommates):
        color = get_roommate_color(roommate.nombre, st.session_state.roommates)
        
        with cols[i]:
            color_html = f"""
            <div style="
                background: {color};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                margin: 5px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">
                👤 {roommate.nombre}
            </div>
            """
            st.markdown(color_html, unsafe_allow_html=True)

def crear_calendario_mensual():
    if not st.session_state.cronograma:
        st.warning("No hay cronograma para mostrar")
        return
    
    st.subheader("🗓️ Vista Calendario Mensual")
    
    # Selector de semana simplificado
    col1, col2 = st.columns([1, 3])
    
    with col1:
        vista_semana = st.selectbox(
            "Mostrar:",
            ["Todas las semanas", "Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            index=0
        )
    
    # Generar datos para las 4 semanas
    cronograma = st.session_state.cronograma
    
    # Preparar colores por roommate
    colores_dict = {}
    for i, roommate in enumerate(st.session_state.roommates):
        colores_dict[roommate.nombre] = COLORES_ROOMMATES[i % len(COLORES_ROOMMATES)]
    
    # Determinar qué semanas mostrar
    if vista_semana == "Todas las semanas":
        semanas_a_mostrar = [1, 2, 3, 4]
        cols = st.columns(2)
    else:
        semana_num = int(vista_semana.split()[-1])
        semanas_a_mostrar = [semana_num]
        cols = [st.container()]
    
    # Mostrar las semanas seleccionadas
    for i, semana_num in enumerate(semanas_a_mostrar):
        with cols[i % len(cols)] if len(cols) > 1 else cols[0]:
            st.markdown(f"### 📅 Semana {semana_num}")
            crear_semana_calendario_html(semana_num, cronograma, colores_dict)
    
    # Mostrar leyenda solo una vez
    mostrar_leyenda_colores()

def crear_semana_calendario_html(semana_num, cronograma, colores_dict):
    """Crea calendario de semana con mismo estilo HTML que el semanal"""
    
    # Definir estructura
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    horas = list(range(6, 23))
    
    # Crear datos del calendario para esta semana
    calendario_data = []
    
    for hora in horas:
        fila = {'Hora': f"{hora:02d}:00 - {hora+1:02d}:00"}
        
        for dia in dias:
            tareas_slot = []
            
            # Buscar tareas en esta hora y día
            for key, asig in cronograma.items():
                if (asig['dia'] == dia and 
                    asig['hora'] <= hora < asig['hora'] + (asig['duracion'] / 60)):
                    
                    color = colores_dict.get(asig['roommate'], '#95a5a6')
                    tareas_slot.append({
                        'tarea': asig['tarea'],
                        'roommate': asig['roommate'],
                        'color': color
                    })
            
            if tareas_slot:
                contenido = tareas_slot[0]  # Tomar la primera tarea si hay varias
                fila[dia] = contenido
            else:
                fila[dia] = None
        
        calendario_data.append(fila)
    
    # Generar HTML del calendario (mismo estilo que semanal)
    css_calendario = """
    <style>
    .calendario-container-mensual {
        width: 100%;
        margin: 15px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .calendario-table-mensual {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
    }
    
    .calendario-table-mensual th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 6px;
        text-align: center;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #ddd;
    }
    
    .calendario-table-mensual td {
        border: 1px solid #e0e0e0;
        padding: 6px;
        height: 50px;
        vertical-align: middle;
        text-align: center;
        font-size: 10px;
        position: relative;
    }
    
    .hora-column-mensual {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 80px;
        text-align: center;
        font-size: 10px;
    }
    
    .tarea-block-mensual {
        color: white;
        padding: 3px 4px;
        border-radius: 4px;
        font-size: 9px;
        font-weight: 500;
        line-height: 1.1;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        margin: 1px;
        display: block;
        word-wrap: break-word;
        hyphens: auto;
    }
    
    .empty-slot-mensual {
        background: #f8f9fa;
        height: 100%;
    }
    
    .calendario-table-mensual tr:hover {
        background-color: #f5f5f5;
    }
    
    .calendario-table-mensual td:hover {
        background-color: #e3f2fd;
        cursor: pointer;
    }
    </style>
    """
    
    html_calendario = css_calendario + '<div class="calendario-container-mensual">'
    html_calendario += '<table class="calendario-table-mensual">'
    
    # Header
    html_calendario += '<thead><tr>'
    html_calendario += '<th class="hora-column-mensual">Hora</th>'
    for dia in dias:
        html_calendario += f'<th>{dia[:3]}</th>'  # Abbreviar días para ahorrar espacio
    html_calendario += '</tr></thead>'
    
    # Body
    html_calendario += '<tbody>'
    for fila in calendario_data:
        html_calendario += '<tr>'
        html_calendario += f'<td class="hora-column-mensual">{fila["Hora"]}</td>'
        
        for dia in dias:
            html_calendario += '<td>'
            
            if fila[dia] is not None:
                tarea_info = fila[dia]
                color = tarea_info['color']
                
                # Truncar nombres para vista mensual
                tarea_corta = tarea_info['tarea'][:12] + "..." if len(tarea_info['tarea']) > 12 else tarea_info['tarea']
                roommate_corto = tarea_info['roommate'][:8] + "..." if len(tarea_info['roommate']) > 8 else tarea_info['roommate']
                
                bloque_html = f'''
                <div class="tarea-block-mensual" style="background: {color};">
                    <div style="font-weight: bold; margin-bottom: 1px;">{tarea_corta}</div>
                    <div style="font-size: 8px; opacity: 0.9;">👤 {roommate_corto}</div>
                </div>
                '''
                html_calendario += bloque_html
            else:
                html_calendario += '<div class="empty-slot-mensual"></div>'
            
            html_calendario += '</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</tbody></table></div>'
    
    # Mostrar el calendario
    st.markdown(html_calendario, unsafe_allow_html=True)
    
    # Información adicional de la semana
    if semana_num:
        with st.expander(f"📊 Estadísticas Semana {semana_num}", expanded=False):
            # Contar tareas por roommate en esta vista
            tareas_por_roommate = {}
            tiempo_por_roommate = {}
            
            for asig in cronograma.values():
                rm = asig['roommate']
                if rm not in tareas_por_roommate:
                    tareas_por_roommate[rm] = 0
                    tiempo_por_roommate[rm] = 0
                tareas_por_roommate[rm] += 1
                tiempo_por_roommate[rm] += asig['duracion']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Tareas por Roommate:**")
                for rm, count in tareas_por_roommate.items():
                    st.write(f"• {rm}: {count} tareas")
            
            with col2:
                st.write("**Tiempo por Roommate:**")
                for rm, tiempo in tiempo_por_roommate.items():
                    horas = tiempo // 60
                    minutos = tiempo % 60
                    st.write(f"• {rm}: {horas}h {minutos}min")
                    
def crear_semana_calendario(semana, cronograma, colores_dict):
    intervalos_30min = []
    for h in range(6, 24):
        for m in [0, 30]:
            intervalos_30min.append(f"{h:02d}:{m:02d}")
    
    dias_nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    calendar_data = np.zeros((len(intervalos_30min), 7))
    calendar_text = [['' for _ in range(7)] for _ in range(len(intervalos_30min))]
    calendar_colors = [['rgba(240,240,240,0.3)' for _ in range(7)] for _ in range(len(intervalos_30min))]
    
    dias_semana_map = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for asignacion in cronograma.values():
        try:
            dia_idx = dias_semana_map.index(asignacion['dia'])
            hora_inicio = asignacion['hora']
            duracion_horas = asignacion['duracion'] / 60
            roommate = asignacion['roommate']
            tarea = asignacion['tarea']
            
            inicio_idx = int((hora_inicio - 6) * 2)
            fin_idx = int(inicio_idx + (duracion_horas * 2))
            
            for idx in range(max(0, inicio_idx), min(len(intervalos_30min), fin_idx)):
                if 0 <= dia_idx < 7:
                    calendar_data[idx][dia_idx] = 1
                    calendar_text[idx][dia_idx] = f"{roommate}<br>{tarea[:12]}"
                    calendar_colors[idx][dia_idx] = colores_dict.get(roommate, '#CCCCCC')
        except (ValueError, IndexError):
            continue
    
    fig = go.Figure()
    
    fig.add_trace(go.Heatmap(
        z=calendar_data,
        x=dias_nombres,
        y=intervalos_30min,
        colorscale=[[0, 'rgba(245,245,245,0.5)'], [1, 'rgba(255,255,255,0.8)']],
        showscale=False,
        text=calendar_text,
        texttemplate="%{text}",
        textfont={"size": 8},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}<br>%{text}<extra></extra>"
    ))
    
    for i in range(len(intervalos_30min)):
        for j in range(7):
            if calendar_data[i][j] > 0:
                fig.add_shape(
                    type="rect",
                    x0=j-0.45, x1=j+0.45,
                    y0=i-0.45, y1=i+0.45,
                    fillcolor=calendar_colors[i][j],
                    opacity=0.8,
                    line=dict(width=1, color='white')
                )
    
    fig.update_layout(
        title=f"Semana {semana['numero']}",
        xaxis_title="Días",
        yaxis_title="Horarios",
        height=300,
        font=dict(size=9),
        margin=dict(l=40, r=10, t=40, b=10)
    )
    
    fig.update_xaxes(side="top", tickangle=0)
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(range(0, len(intervalos_30min), 4)),
        ticktext=[intervalos_30min[i] for i in range(0, len(intervalos_30min), 4)]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def mostrar_calendario_individual(roommate):
    st.write(f"### 📅 Disponibilidad de {roommate.nombre}")
    
    intervalos_30min = []
    for h in range(6, 24):
        for m in [0, 30]:
            intervalos_30min.append(h + m/60)
    
    intervalos_labels = [f"{int(h):02d}:{int((h % 1) * 60):02d}" for h in intervalos_30min]
    
    disponibilidad_data = np.zeros((len(intervalos_30min), 7))
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for dia_idx, dia in enumerate(dias_semana):
        if dia in roommate.horarios_disponibles:
            for rango in roommate.horarios_disponibles[dia]:
                for i, hora in enumerate(intervalos_30min):
                    if rango.contiene_hora(hora):
                        disponibilidad_data[i][dia_idx] = 1
    
    fig = go.Figure(data=go.Heatmap(
        z=disponibilidad_data,
        x=dias_semana,
        y=intervalos_labels,
        colorscale=[
            [0, 'rgba(255,200,200,0.3)'],
            [1, 'rgba(100,200,100,0.8)']
        ],
        showscale=True,
        colorbar=dict(
            title="Disponibilidad",
            tickvals=[0, 1],
            ticktext=["No disponible", "Disponible"]
        ),
        text=[[
            "✅ Disponible" if disponibilidad_data[i][j] == 1 else "❌ No disponible"
            for j in range(7)
        ] for i in range(len(intervalos_30min))],
        texttemplate="%{text}",
        textfont={"size": 8},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}<br>%{text}<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"Horarios de Disponibilidad - {roommate.nombre}",
        xaxis_title="Días",
        yaxis_title="Horarios (30 min)",
        height=400,
        font=dict(size=10)
    )
    
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(range(0, len(intervalos_labels), 4)),
        ticktext=[intervalos_labels[i] for i in range(0, len(intervalos_labels), 4)]
    )
    
    fig.update_xaxes(side="top")
    
    st.plotly_chart(fig, use_container_width=True)

def mostrar_vista_por_dias():
    cronograma = st.session_state.cronograma
    
    data = []
    for key, asig in cronograma.items():
        data.append({
            'Día': asig['dia'],
            'Hora': f"{asig['hora']:02d}:00",
            'Tarea': asig['tarea'],
            'Roommate': asig['roommate'],
            'Duración': f"{asig['duracion']}min"
        })
    
    df = pd.DataFrame(data)
    
    st.subheader("Vista por días")
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for dia in dias:
        with st.expander(f"📅 {dia}"):
            dia_data = df[df['Día'] == dia].sort_values('Hora')
            
            if not dia_data.empty:
                for _, row in dia_data.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    with col1:
                        st.write(f"🕐 {row['Hora']}")
                    with col2:
                        st.write(f"📝 {row['Tarea']}")
                    with col3:
                        st.write(f"👤 {row['Roommate']}")
                    with col4:
                        st.write(f"⏱️ {row['Duración']}")
            else:
                st.write("Sin tareas")

def mostrar_vista_tabla():
    cronograma = st.session_state.cronograma
    
    data = []
    for key, asig in cronograma.items():
        data.append({
            'Día': asig['dia'],
            'Hora': f"{asig['hora']:02d}:00",
            'Tarea': asig['tarea'],
            'Roommate': asig['roommate'],
            'Duración': f"{asig['duracion']}min"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)