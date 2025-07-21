import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Colores predefinidos para roommates
COLORES_ROOMMATES = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43'
]

def mostrar_calendario():
    """Pantalla principal del calendario"""
    if not st.session_state.cronograma:
        _mostrar_placeholder_calendario()
        return
    
    st.markdown("""
    <div style='background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0;'>📅 Cronograma Mensual Generado</h2>
        <p style='color: white; margin: 0; opacity: 0.9;'>
            Vista completa del cronograma con intervalos de 30 minutos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Opciones de visualización
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vista_semana = st.selectbox(
            "🗓️ Mostrar:",
            ["📅 Todas las semanas", "📅 Semana 1", "📅 Semana 2", "📅 Semana 3", "📅 Semana 4"],
            index=0
        )
    
    with col2:
        modo_vista = st.selectbox(
            "👁️ Modo de vista:",
            ["🎨 Visual", "📊 Tabla", "📈 Análisis"],
            index=0
        )
    
    with col3:
        if st.button("🔍 Detectar Conflictos", use_container_width=True):
            _detectar_conflictos_simples()
    
    # Mostrar contenido según selección
    if modo_vista == "🎨 Visual":
        _mostrar_calendario_visual(vista_semana)
    elif modo_vista == "📊 Tabla":
        _mostrar_calendario_tabla(vista_semana)
    else:
        _mostrar_analisis_cronograma()

def _mostrar_placeholder_calendario():
    """Placeholder cuando no hay cronograma"""
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px; margin: 2rem 0;'>
        <h2 style='color: #6c757d; margin-bottom: 1rem;'>📅 No hay cronograma generado</h2>
        <p style='color: #6c757d; font-size: 1.1rem;'>
            Ve a la sección "🧠 Optimizar" para generar tu cronograma mensual
        </p>
        <p style='color: #6c757d;'>
            O asegúrate de tener al menos 1 roommate y 1 tarea configurados
        </p>
    </div>
    """, unsafe_allow_html=True)

def _mostrar_calendario_visual(vista_semana: str):
    """Vista visual del calendario"""
    cronograma = st.session_state.cronograma
    
    # Determinar semanas a mostrar
    if vista_semana == "📅 Todas las semanas":
        semanas_mostrar = [1, 2, 3, 4]
        cols = st.columns(2)
    else:
        semana_num = int(vista_semana.split()[-1])
        semanas_mostrar = [semana_num]
        cols = [st.container()]
    
    # Mostrar calendarios
    for i, semana in enumerate(semanas_mostrar):
        with cols[i % len(cols)] if len(cols) > 1 else cols[0]:
            st.markdown(f"### 📅 Semana {semana}")
            _crear_calendario_semana(semana, cronograma)
    
    # Mostrar leyenda
    if len(semanas_mostrar) == 1:
        _mostrar_leyenda_colores()

def _crear_calendario_semana(semana: int, cronograma: dict):
    """Crea calendario visual para una semana"""
    dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    dias_completos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Generar intervalos de 30 minutos
    intervalos = []
    for h in range(6, 24):
        intervalos.extend([f"{h:02d}:00", f"{h:02d}:30"])
    
    # Crear datos del calendario
    calendario_data = []
    
    for i, intervalo in enumerate(intervalos):
        hora_decimal = 6 + (i * 0.5)
        fila = {'Hora': intervalo}
        
        for j, dia_completo in enumerate(dias_completos):
            # Buscar tareas en este slot
            tareas_slot = []
            for asig in cronograma.values():
                if (asig['dia'] == dia_completo and 
                    asig['semana'] == semana and
                    asig['hora'] <= hora_decimal < asig['hora'] + (asig['duracion'] / 60)):
                    
                    color = _get_color_roommate(asig['roommate'])
                    tareas_slot.append({
                        'tarea': asig['tarea'],
                        'roommate': asig['roommate'],
                        'color': color
                    })
            
            fila[dias[j]] = tareas_slot[0] if tareas_slot else None
        
        calendario_data.append(fila)
    
    # Renderizar HTML del calendario
    _renderizar_calendario_html(calendario_data, dias)

def _renderizar_calendario_html(calendario_data: list, dias: list):
    """Renderiza calendario en HTML optimizado"""
    
    css_calendario = """
    <style>
    .calendario-container {
        width: 100%;
        margin: 15px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-height: 500px;
        overflow-y: auto;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .calendario-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        font-size: 11px;
    }
    
    .calendario-table th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 4px;
        text-align: center;
        font-weight: 600;
        border: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .calendario-table td {
        border: 1px solid #e0e0e0;
        padding: 2px;
        height: 30px;
        vertical-align: middle;
        text-align: center;
        font-size: 9px;
    }
    
    .hora-column {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 60px;
        text-align: center;
        position: sticky;
        left: 0;
        z-index: 5;
    }
    
    .tarea-block {
        color: white;
        padding: 1px 2px;
        border-radius: 3px;
        font-size: 7px;
        font-weight: 500;
        line-height: 1.1;
        text-shadow: 0 1px 1px rgba(0,0,0,0.3);
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .empty-slot {
        background: #f8f9fa;
        height: 100%;
    }
    
    .calendario-table tr:hover {
        background-color: rgba(0,0,0,0.02);
    }
    </style>
    """
    
    html_calendario = css_calendario + '<div class="calendario-container">'
    html_calendario += '<table class="calendario-table">'
    
    # Header
    html_calendario += '<thead><tr>'
    html_calendario += '<th class="hora-column">Hora</th>'
    for dia in dias:
        html_calendario += f'<th>{dia}</th>'
    html_calendario += '</tr></thead>'
    
    # Body
    html_calendario += '<tbody>'
    for fila in calendario_data:
        hora = fila["Hora"]
        html_calendario += '<tr>'
        html_calendario += f'<td class="hora-column">{hora}</td>'
        
        for dia in dias:
            html_calendario += '<td>'
            
            if fila[dia] is not None:
                tarea_info = fila[dia]
                color = tarea_info['color']
                
                # Truncar nombres para vista compacta
                tarea_corta = tarea_info['tarea'][:6] + "..." if len(tarea_info['tarea']) > 6 else tarea_info['tarea']
                roommate_corto = tarea_info['roommate'][:4] + "..." if len(tarea_info['roommate']) > 4 else tarea_info['roommate']
                
                html_calendario += f'''
                <div class="tarea-block" style="background: {color};" title="{tarea_info['tarea']} - {tarea_info['roommate']}">
                    <div style="font-weight: bold;">{tarea_corta}</div>
                    <div style="font-size: 6px; opacity: 0.9;">{roommate_corto}</div>
                </div>
                '''
            else:
                html_calendario += '<div class="empty-slot"></div>'
            
            html_calendario += '</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</tbody></table></div>'
    
    st.markdown(html_calendario, unsafe_allow_html=True)

def _mostrar_leyenda_colores():
    """Muestra leyenda de colores por roommate"""
    st.markdown("### 🎨 Leyenda de Colores")
    
    cols = st.columns(min(len(st.session_state.roommates), 5))
    
    for i, roommate in enumerate(st.session_state.roommates):
        color = _get_color_roommate(roommate.nombre)
        
        with cols[i % len(cols)]:
            color_html = f"""
            <div style="
                background: {color};
                color: white;
                padding: 8px;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
                margin: 3px 0;
                font-size: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">
                👤 {roommate.nombre}
            </div>
            """
            st.markdown(color_html, unsafe_allow_html=True)

def _mostrar_calendario_tabla(vista_semana: str):
    """Vista en tabla del calendario"""
    cronograma = st.session_state.cronograma
    
    # Preparar datos
    data = []
    for asig in cronograma.values():
        # Filtrar por semana si es necesario
        if vista_semana != "📅 Todas las semanas":
            semana_filtro = int(vista_semana.split()[-1])
            if asig['semana'] != semana_filtro:
                continue
        
        hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
        
        data.append({
            'Semana': f"S{asig['semana']}",
            'Día': asig['dia'],
            'Hora': hora_str,
            'Tarea': asig['tarea'],
            'Roommate': asig['roommate'],
            'Duración': f"{asig['duracion']}min"
        })
    
    if data:
        df = pd.DataFrame(data)
        
        # Ordenar
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df['Día_Order'] = df['Día'].map(lambda x: orden_dias.index(x))
        df = df.sort_values(['Semana', 'Día_Order', 'Hora']).drop('Día_Order', axis=1)
        
        # Filtros adicionales
        col1, col2 = st.columns(2)
        with col1:
            roommate_filtro = st.selectbox("Filtrar roommate:", ["Todos"] + [rm.nombre for rm in st.session_state.roommates])
        with col2:
            categoria_filtro = st.selectbox("Filtrar categoría:", ["Todas"] + list(set(t.categoria for t in st.session_state.tareas)))
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if roommate_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Roommate'] == roommate_filtro]
        if categoria_filtro != "Todas":
            # Obtener categoría de cada tarea
            tareas_dict = {t.nombre: t.categoria for t in st.session_state.tareas}
            df_filtrado = df_filtrado[df_filtrado['Tarea'].map(lambda x: tareas_dict.get(x, '')) == categoria_filtro]
        
        # Mostrar tabla
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
        # Estadísticas rápidas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Asignaciones", len(df_filtrado))
        with col2:
            tiempo_total = df_filtrado['Duración'].str.replace('min', '').astype(int).sum()
            st.metric("Tiempo Total", f"{tiempo_total//60}h {tiempo_total%60}min")
        with col3:
            st.metric("Roommates Activos", df_filtrado['Roommate'].nunique())
        with col4:
            st.metric("Días Cubiertos", df_filtrado['Día'].nunique())
    
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados")

def _mostrar_analisis_cronograma():
    """Análisis detallado del cronograma"""
    cronograma = st.session_state.cronograma
    
    st.markdown("### 📈 Análisis del Cronograma")
    
    # Análisis por semana
    col1, col2 = st.columns(2)
    
    with col1:
        _grafico_carga_por_semana(cronograma)
    
    with col2:
        _grafico_distribucion_roommates(cronograma)
    
    # Verificación de cocina diaria
    st.markdown("---")
    _verificar_cocina_diaria(cronograma)

def _grafico_carga_por_semana(cronograma: dict):
    """Gráfico de carga de trabajo por semana"""
    carga_semana = {}
    
    for asig in cronograma.values():
        semana = f"Semana {asig['semana']}"
        carga_semana[semana] = carga_semana.get(semana, 0) + asig['duracion']
    
    if carga_semana:
        fig = go.Figure(data=[
            go.Bar(
                x=list(carga_semana.keys()),
                y=list(carga_semana.values()),
                marker_color='#4ECDC4',
                text=[f"{v//60}h {v%60}min" for v in carga_semana.values()],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Carga de Trabajo por Semana",
            xaxis_title="Semanas",
            yaxis_title="Tiempo (minutos)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def _grafico_distribucion_roommates(cronograma: dict):
    """Gráfico de distribución por roommate"""
    carga_roommate = {}
    
    for asig in cronograma.values():
        roommate = asig['roommate']
        carga_roommate[roommate] = carga_roommate.get(roommate, 0) + asig['duracion']
    
    if carga_roommate:
        colors = [_get_color_roommate(rm) for rm in carga_roommate.keys()]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(carga_roommate.keys()),
                values=list(carga_roommate.values()),
                hole=0.4,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=12
            )
        ])
        
        fig.update_layout(
            title="Distribución de Carga por Roommate",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def _verificar_cocina_diaria(cronograma: dict):
    """Verifica cumplimiento de cocina diaria"""
    st.markdown("### 🍳 Verificación de Cocina Diaria")
    
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Matriz de cocina por día y semana
    cocina_matriz = {}
    for semana in [1, 2, 3, 4]:
        cocina_matriz[semana] = {dia: False for dia in dias_semana}
    
    # Verificar asignaciones de cocina
    for asig in cronograma.values():
        tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
        if tarea_obj and tarea_obj.categoria == 'Cocina':
            cocina_matriz[asig['semana']][asig['dia']] = True
    
    # Crear tabla de verificación
    data_verificacion = []
    for dia in dias_semana:
        fila = {'Día': dia}
        for semana in [1, 2, 3, 4]:
            fila[f'S{semana}'] = "✅" if cocina_matriz[semana][dia] else "❌"
        data_verificacion.append(fila)
    
    df_verificacion = pd.DataFrame(data_verificacion)
    st.dataframe(df_verificacion, use_container_width=True, hide_index=True)
    
    # Métrica de cumplimiento
    total_dias = 28
    dias_con_cocina = sum(1 for semana in cocina_matriz.values() 
                         for tiene_cocina in semana.values() if tiene_cocina)
    
    cumplimiento = (dias_con_cocina / total_dias) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Días con Cocina", f"{dias_con_cocina}/28")
    with col2:
        st.metric("Cumplimiento", f"{cumplimiento:.1f}%")
    with col3:
        if cumplimiento >= 90:
            st.success("✅ Excelente cumplimiento")
        elif cumplimiento >= 70:
            st.warning("⚠️ Cumplimiento aceptable")
        else:
            st.error("❌ Cumplimiento deficiente")

def _detectar_conflictos_simples():
    """Detección básica de conflictos de horarios"""
    cronograma = st.session_state.cronograma
    conflictos = []
    
    # Agrupar por slot de tiempo
    slots = {}
    for key, asig in cronograma.items():
        slot_key = (asig['semana'], asig['dia'], asig['hora'])
        if slot_key not in slots:
            slots[slot_key] = []
        slots[slot_key].append((key, asig))
    
    # Buscar conflictos (más de una tarea al mismo tiempo)
    for slot_key, asignaciones in slots.items():
        if len(asignaciones) > 1:
            semana, dia, hora = slot_key
            hora_str = f"{int(hora):02d}:{int((hora % 1) * 60):02d}"
            
            conflictos.append({
                'semana': semana,
                'dia': dia,
                'hora': hora_str,
                'num_tareas': len(asignaciones),
                'tareas': [asig['tarea'] for _, asig in asignaciones],
                'roommates': [asig['roommate'] for _, asig in asignaciones]
            })
    
    # Mostrar resultados
    if conflictos:
        st.error(f"🚨 Se detectaron {len(conflictos)} conflictos de horarios")
        
        for conflicto in conflictos:
            st.markdown(f"""
            **⚠️ Conflicto:** Semana {conflicto['semana']}, {conflicto['dia']} a las {conflicto['hora']}  
            **Tareas:** {', '.join(conflicto['tareas'])}  
            **Roommates:** {', '.join(conflicto['roommates'])}
            """)
    else:
        st.success("✅ No se detectaron conflictos de horarios")

def _get_color_roommate(nombre_roommate: str) -> str:
    """Obtiene color consistente para un roommate"""
    try:
        nombres = [rm.nombre for rm in st.session_state.roommates]
        index = nombres.index(nombre_roommate)
        return COLORES_ROOMMATES[index % len(COLORES_ROOMMATES)]
    except (ValueError, IndexError):
        return '#95a5a6'  # Color por defecto