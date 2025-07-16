import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import calendar
from conflict_detector import DetectorConflictos

def crear_calendario_mensual_con_conflictos():
    """Vista del calendario mensual que muestra conflictos"""
    if not st.session_state.cronograma:
        st.warning("No hay cronograma para mostrar")
        return
    
    st.subheader("🗓️ Calendario Mensual con Detección de Conflictos")
    
    # Detectar conflictos primero
    detector = DetectorConflictos(
        st.session_state.cronograma,
        st.session_state.roommates,
        st.session_state.tareas
    )
    
    conflictos, tipos_conflictos = detector.mostrar_resumen_conflictos()
    
    # Guardar conflictos en session state para uso en otros componentes
    st.session_state.conflictos_detectados = conflictos
    
    st.divider()
    
    # Selector de modo de vista
    col1, col2 = st.columns([1, 3])
    
    with col1:
        modo_vista = st.selectbox(
            "Modo de Vista:",
            ["Normal", "Solo Conflictos", "Resaltado"],
            help="Normal: Vista estándar | Solo Conflictos: Muestra solo slots con conflictos | Resaltado: Marca conflictos en rojo"
        )
        
        vista_semana = st.selectbox(
            "Mostrar:",
            ["Todas las semanas", "Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            index=0
        )
    
    with col2:
        if conflictos:
            st.info(f"💡 **Modo '{modo_vista}'**: Se detectaron {len(conflictos)} conflictos de horarios.")
        else:
            st.success("✅ No hay conflictos detectados. Mostrando calendario normal.")
    
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
            crear_semana_calendario_con_conflictos(semana_num, st.session_state.cronograma, colores_dict, conflictos, modo_vista)
    
    # Mostrar leyenda
    mostrar_leyenda_colores_con_conflictos()

def crear_semana_calendario_con_conflictos(semana_num, cronograma, colores_dict, conflictos, modo_vista):
    """Crea calendario de semana mostrando conflictos"""
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    intervalos_30min = []
    
    for h in range(6, 24):
        intervalos_30min.append(f"{h:02d}:00")
        intervalos_30min.append(f"{h:02d}:30")
    
    # Crear datos del calendario
    calendario_data = []
    
    for i, intervalo in enumerate(intervalos_30min):
        hora_decimal = 6 + (i * 0.5)
        fila = {'Hora': intervalo}
        
        for dia in dias:
            tareas_slot = []
            tiene_conflicto = False
            
            # Verificar si hay conflicto en este slot
            conflict_key = (semana_num, dia, hora_decimal)
            if conflict_key in conflictos:
                tiene_conflicto = True
            
            # Buscar tareas en esta hora, día y semana
            for key, asig in cronograma.items():
                if (asig['dia'] == dia and 
                    asig['semana'] == semana_num and
                    asig['hora'] <= hora_decimal < asig['hora'] + (asig['duracion'] / 60)):
                    
                    color = colores_dict.get(asig['roommate'], '#95a5a6')
                    tareas_slot.append({
                        'tarea': asig['tarea'],
                        'roommate': asig['roommate'],
                        'color': color,
                        'tiene_conflicto': tiene_conflicto,
                        'asignacion_key': key
                    })
            
            # Aplicar filtros según modo de vista
            if modo_vista == "Solo Conflictos" and not tiene_conflicto:
                fila[dia] = None
            elif tareas_slot:
                fila[dia] = {
                    'tareas': tareas_slot,
                    'tiene_conflicto': tiene_conflicto,
                    'num_tareas': len(tareas_slot)
                }
            else:
                fila[dia] = None
        
        calendario_data.append(fila)
    
    # Generar HTML del calendario con conflictos
    mostrar_calendario_html_con_conflictos(calendario_data, dias, modo_vista)

def mostrar_calendario_html_con_conflictos(calendario_data, dias, modo_vista):
    """Renderiza calendario HTML con visualización de conflictos"""
    
    css_calendario = """
    <style>
    .calendario-container-conflictos {
        width: 100%;
        margin: 15px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .calendario-table-conflictos {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        font-size: 10px;
    }
    
    .calendario-table-conflictos th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 4px;
        text-align: center;
        font-weight: 600;
        font-size: 11px;
        border: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .calendario-table-conflictos td {
        border: 1px solid #e0e0e0;
        padding: 2px;
        height: 35px;
        vertical-align: top;
        text-align: center;
        font-size: 8px;
        position: relative;
    }
    
    .hora-column-conflictos {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 60px;
        text-align: center;
        font-size: 9px;
        position: sticky;
        left: 0;
        z-index: 5;
    }
    
    .tarea-block-conflictos {
        color: white;
        padding: 1px 2px;
        border-radius: 3px;
        font-size: 7px;
        font-weight: 500;
        line-height: 1.0;
        margin: 1px 0;
        display: block;
        word-wrap: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .celda-conflicto {
        background: linear-gradient(45deg, #ffebee 25%, transparent 25%, transparent 75%, #ffebee 75%), 
                    linear-gradient(45deg, #ffebee 25%, transparent 25%, transparent 75%, #ffebee 75%);
        background-size: 8px 8px;
        background-position: 0 0, 4px 4px;
        border: 2px solid #f44336 !important;
        animation: pulse-conflict 2s infinite;
    }
    
    .indicador-conflicto {
        position: absolute;
        top: 0;
        right: 0;
        background: #f44336;
        color: white;
        font-size: 6px;
        padding: 1px 3px;
        border-radius: 0 0 0 3px;
        font-weight: bold;
        z-index: 10;
    }
    
    @keyframes pulse-conflict {
        0% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4); }
        70% { box-shadow: 0 0 0 4px rgba(244, 67, 54, 0); }
        100% { box-shadow: 0 0 0 0 rgba(244, 67, 54, 0); }
    }
    
    .empty-slot-conflictos {
        background: #f8f9fa;
        height: 100%;
    }
    
    .tarea-multiple {
        margin-bottom: 1px;
        font-size: 6px;
    }
    </style>
    """
    
    html_calendario = css_calendario + '<div class="calendario-container-conflictos">'
    html_calendario += '<table class="calendario-table-conflictos">'
    
    # Header
    html_calendario += '<thead><tr>'
    html_calendario += '<th class="hora-column-conflictos">Hora</th>'
    for dia in dias:
        html_calendario += f'<th>{dia[:3]}</th>'
    html_calendario += '</tr></thead>'
    
    # Body
    html_calendario += '<tbody>'
    for fila in calendario_data:
        hora = fila["Hora"]
        
        html_calendario += '<tr>'
        html_calendario += f'<td class="hora-column-conflictos">{hora}</td>'
        
        for dia in dias:
            cell_class = ""
            cell_content = ""
            
            if fila[dia] is not None:
                slot_data = fila[dia]
                tiene_conflicto = slot_data['tiene_conflicto']
                tareas = slot_data['tareas']
                num_tareas = slot_data['num_tareas']
                
                # Aplicar clase de conflicto si es necesario
                if tiene_conflicto and modo_vista == "Resaltado":
                    cell_class = "celda-conflicto"
                
                # Crear contenido de la celda
                if num_tareas == 1:
                    # Una sola tarea
                    tarea_info = tareas[0]
                    color = tarea_info['color']
                    tarea_corta = tarea_info['tarea'][:8] + "..." if len(tarea_info['tarea']) > 8 else tarea_info['tarea']
                    roommate_corto = tarea_info['roommate'][:6] + "..." if len(tarea_info['roommate']) > 6 else tarea_info['roommate']
                    
                    cell_content = f'''
                    <div class="tarea-block-conflictos" style="background: {color};" title="{tarea_info['tarea']} - {tarea_info['roommate']}">
                        <div style="font-weight: bold;">{tarea_corta}</div>
                        <div style="opacity: 0.9;">{roommate_corto}</div>
                    </div>
                    '''
                
                else:
                    # Múltiples tareas (CONFLICTO)
                    for i, tarea_info in enumerate(tareas):
                        color = tarea_info['color']
                        tarea_corta = tarea_info['tarea'][:6] + "..." if len(tarea_info['tarea']) > 6 else tarea_info['tarea']
                        roommate_corto = tarea_info['roommate'][:4] + "..." if len(tarea_info['roommate']) > 4 else tarea_info['roommate']
                        
                        cell_content += f'''
                        <div class="tarea-block-conflictos tarea-multiple" style="background: {color};" title="{tarea_info['tarea']} - {tarea_info['roommate']}">
                            <div style="font-weight: bold;">{tarea_corta}</div>
                            <div style="opacity: 0.9;">{roommate_corto}</div>
                        </div>
                        '''
                    
                    # Agregar indicador de conflicto
                    cell_content += f'<div class="indicador-conflicto">⚠{num_tareas}</div>'
                
            else:
                cell_content = '<div class="empty-slot-conflictos"></div>'
            
            html_calendario += f'<td class="{cell_class}">{cell_content}</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</tbody></table></div>'
    
    # Mostrar el calendario
    st.markdown(html_calendario, unsafe_allow_html=True)

def mostrar_leyenda_colores_con_conflictos():
    """Muestra leyenda incluyendo indicadores de conflictos"""
    st.subheader("🎨 Leyenda de Colores y Conflictos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Colores por Roommate:**")
        cols = st.columns(min(len(st.session_state.roommates), 4))
        
        for i, roommate in enumerate(st.session_state.roommates):
            color = get_roommate_color(roommate.nombre, st.session_state.roommates)
            
            with cols[i % len(cols)]:
                color_html = f"""
                <div style="
                    background: {color};
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    text-align: center;
                    font-weight: bold;
                    margin: 2px 0;
                    font-size: 11px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                ">
                    👤 {roommate.nombre}
                </div>
                """
                st.markdown(color_html, unsafe_allow_html=True)
    
    with col2:
        st.write("**Indicadores de Conflictos:**")
        
        indicadores_html = """
        <div style="font-size: 12px;">
            <div style="margin: 5px 0;">
                <span style="background: #f44336; color: white; padding: 2px 6px; border-radius: 3px;">⚠2</span>
                = 2 tareas simultáneas
            </div>
            <div style="margin: 5px 0;">
                <span style="background: #f44336; color: white; padding: 2px 6px; border-radius: 3px;">⚠3</span>
                = 3+ tareas simultáneas
            </div>
            <div style="margin: 5px 0;">
                <span style="border: 2px solid #f44336; padding: 2px 6px; border-radius: 3px; background: repeating-linear-gradient(45deg, transparent, transparent 4px, #ffebee 4px, #ffebee 8px);">🔴</span>
                = Celda con conflicto
            </div>
        </div>
        """
        st.markdown(indicadores_html, unsafe_allow_html=True)

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

def crear_calendario_mensual():
    """Vista principal del calendario mensual con intervalos de 30 minutos"""
    if not st.session_state.cronograma:
        st.warning("No hay cronograma para mostrar")
        return
    
    st.subheader("🗓️ Calendario Mensual (4 Semanas)")
    
    # Selector de semana
    col1, col2 = st.columns([1, 3])
    
    with col1:
        vista_semana = st.selectbox(
            "Mostrar:",
            ["Todas las semanas", "Semana 1", "Semana 2", "Semana 3", "Semana 4"],
            index=0
        )
    
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
            crear_semana_calendario_30min(semana_num, cronograma, colores_dict)
    
    # Mostrar leyenda solo una vez
    mostrar_leyenda_colores()
    
    # Análisis del cronograma mensual
    mostrar_analisis_mensual(cronograma)

def crear_semana_calendario_30min(semana_num, cronograma, colores_dict):
    """Crea calendario de semana con intervalos de 30 minutos"""
    
    # Definir estructura con intervalos de 30 minutos
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    intervalos_30min = []
    
    # Crear intervalos de 30 minutos desde 6:00 hasta 23:30
    for h in range(6, 24):
        intervalos_30min.append(f"{h:02d}:00")
        intervalos_30min.append(f"{h:02d}:30")
    
    # Crear datos del calendario para esta semana
    calendario_data = []
    
    for i, intervalo in enumerate(intervalos_30min):
        hora_decimal = 6 + (i * 0.5)
        fila = {'Hora': intervalo}
        
        for dia in dias:
            tareas_slot = []
            
            # Buscar tareas en esta hora, día y semana
            for key, asig in cronograma.items():
                if (asig['dia'] == dia and 
                    asig['semana'] == semana_num and
                    asig['hora'] <= hora_decimal < asig['hora'] + (asig['duracion'] / 60)):
                    
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
    
    # Generar HTML del calendario
    mostrar_calendario_html_30min(calendario_data, dias)

def mostrar_calendario_html_30min(calendario_data, dias):
    """Renderiza calendario HTML optimizado para intervalos de 30 minutos"""
    
    css_calendario = """
    <style>
    .calendario-container-30min {
        width: 100%;
        margin: 15px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .calendario-table-30min {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
        font-size: 11px;
    }
    
    .calendario-table-30min th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 4px;
        text-align: center;
        font-weight: 600;
        font-size: 11px;
        border: 1px solid #ddd;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .calendario-table-30min td {
        border: 1px solid #e0e0e0;
        padding: 3px;
        height: 35px;
        vertical-align: middle;
        text-align: center;
        font-size: 9px;
        position: relative;
    }
    
    .hora-column-30min {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 60px;
        text-align: center;
        font-size: 9px;
        position: sticky;
        left: 0;
        z-index: 5;
    }
    
    .tarea-block-30min {
        color: white;
        padding: 2px 3px;
        border-radius: 3px;
        font-size: 8px;
        font-weight: 500;
        line-height: 1.0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        margin: 1px;
        display: block;
        word-wrap: break-word;
        hyphens: auto;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .empty-slot-30min {
        background: #f8f9fa;
        height: 100%;
    }
    
    .calendario-table-30min tr:hover {
        background-color: #f5f5f5;
    }
    
    .calendario-table-30min td:hover {
        background-color: #e3f2fd;
        cursor: pointer;
    }
    
    /* Resaltar franjas horarias importantes */
    .hora-comida {
        background-color: #fff3cd !important;
    }
    
    .hora-manana {
        background-color: #d4edda !important;
    }
    
    .hora-noche {
        background-color: #d1ecf1 !important;
    }
    </style>
    """
    
    html_calendario = css_calendario + '<div class="calendario-container-30min">'
    html_calendario += '<table class="calendario-table-30min">'
    
    # Header
    html_calendario += '<thead><tr>'
    html_calendario += '<th class="hora-column-30min">Hora</th>'
    for dia in dias:
        html_calendario += f'<th>{dia[:3]}</th>'
    html_calendario += '</tr></thead>'
    
    # Body
    html_calendario += '<tbody>'
    for fila in calendario_data:
        hora = fila["Hora"]
        hora_num = int(hora.split(':')[0])
        
        # Clase especial para diferentes franjas horarias
        clase_franja = ""
        if 12 <= hora_num <= 14:
            clase_franja = "hora-comida"
        elif 6 <= hora_num <= 9:
            clase_franja = "hora-manana"
        elif 20 <= hora_num <= 23:
            clase_franja = "hora-noche"
        
        html_calendario += f'<tr class="{clase_franja}">'
        html_calendario += f'<td class="hora-column-30min">{hora}</td>'
        
        for dia in dias:
            html_calendario += '<td>'
            
            if fila[dia] is not None:
                tarea_info = fila[dia]
                color = tarea_info['color']
                
                # Truncar nombres para vista compacta
                tarea_corta = tarea_info['tarea'][:8] + "..." if len(tarea_info['tarea']) > 8 else tarea_info['tarea']
                roommate_corto = tarea_info['roommate'][:6] + "..." if len(tarea_info['roommate']) > 6 else tarea_info['roommate']
                
                bloque_html = f'''
                <div class="tarea-block-30min" style="background: {color};" title="{tarea_info['tarea']} - {tarea_info['roommate']}">
                    <div style="font-weight: bold;">{tarea_corta}</div>
                    <div style="font-size: 7px; opacity: 0.9;">{roommate_corto}</div>
                </div>
                '''
                html_calendario += bloque_html
            else:
                html_calendario += '<div class="empty-slot-30min"></div>'
            
            html_calendario += '</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</tbody></table></div>'
    
    # Mostrar el calendario
    st.markdown(html_calendario, unsafe_allow_html=True)

def mostrar_leyenda_colores():
    """Muestra la leyenda de colores para roommates"""
    st.subheader("🎨 Leyenda de Colores")
    
    cols = st.columns(min(len(st.session_state.roommates), 5))
    
    for i, roommate in enumerate(st.session_state.roommates):
        color = get_roommate_color(roommate.nombre, st.session_state.roommates)
        
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

def mostrar_analisis_mensual(cronograma):
    """Análisis específico del cronograma mensual"""
    st.subheader("📊 Análisis Mensual")
    
    # Estadísticas por semana
    estadisticas_semanas = {}
    
    for asig in cronograma.values():
        semana = asig['semana']
        if semana not in estadisticas_semanas:
            estadisticas_semanas[semana] = {
                'tareas_totales': 0,
                'tiempo_total': 0,
                'roommates': set(),
                'cocina_dias': set()
            }
        
        estadisticas_semanas[semana]['tareas_totales'] += 1
        estadisticas_semanas[semana]['tiempo_total'] += asig['duracion']
        estadisticas_semanas[semana]['roommates'].add(asig['roommate'])
        
        # Verificar si es tarea de cocina
        tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
        if tarea_obj and tarea_obj.categoria == 'Cocina':
            estadisticas_semanas[semana]['cocina_dias'].add(asig['dia'])
    
    # Mostrar métricas por semana
    cols = st.columns(4)
    
    for i, semana in enumerate([1, 2, 3, 4]):
        with cols[i]:
            st.markdown(f"### Semana {semana}")
            
            if semana in estadisticas_semanas:
                stats = estadisticas_semanas[semana]
                st.metric("Tareas", stats['tareas_totales'])
                st.metric("Tiempo", f"{stats['tiempo_total']//60}h {stats['tiempo_total']%60}min")
                st.metric("Roommates", len(stats['roommates']))
                st.metric("Días con Cocina", f"{len(stats['cocina_dias'])}/7")
            else:
                st.metric("Tareas", 0)
                st.metric("Tiempo", "0h 0min")
                st.metric("Roommates", 0)
                st.metric("Días con Cocina", "0/7")
    
    # Verificación de cocina diaria
    with st.expander("🍳 Verificación de Cocina Diaria", expanded=False):
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        cocina_matriz = {}
        for semana in [1, 2, 3, 4]:
            cocina_matriz[semana] = {dia: False for dia in dias_semana}
        
        for asig in cronograma.values():
            tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
            if tarea_obj and tarea_obj.categoria == 'Cocina':
                cocina_matriz[asig['semana']][asig['dia']] = True
        
        # Crear tabla de verificación
        verification_data = []
        for dia in dias_semana:
            fila = {'Día': dia}
            for semana in [1, 2, 3, 4]:
                fila[f'S{semana}'] = "✅" if cocina_matriz[semana][dia] else "❌"
            verification_data.append(fila)
        
        df_verification = pd.DataFrame(verification_data)
        st.dataframe(df_verification, use_container_width=True)
        
        # Contador de cumplimiento
        total_dias = 28
        dias_con_cocina = sum(1 for semana in cocina_matriz.values() 
                            for tiene_cocina in semana.values() if tiene_cocina)
        
        cumplimiento = (dias_con_cocina / total_dias) * 100
        st.metric("Cumplimiento Cocina Diaria", f"{cumplimiento:.1f}%")

def mostrar_calendario_individual(roommate):
    """Muestra calendario individual con intervalos de 30 minutos"""
    st.write(f"### 📅 Disponibilidad de {roommate.nombre}")
    
    # Crear intervalos de 30 minutos
    intervalos_30min = []
    for h in range(6, 24):
        intervalos_30min.append(h)
        intervalos_30min.append(h + 0.5)
    
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
        textfont={"size": 6},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>%{x}<br>%{text}<extra></extra>"
    ))
    
    fig.update_layout(
        title=f"Horarios de Disponibilidad - {roommate.nombre} (Intervalos 30min)",
        xaxis_title="Días",
        yaxis_title="Horarios (30 min)",
        height=500,
        font=dict(size=9)
    )
    
    # Mostrar solo cada hora en el eje Y para no saturar
    fig.update_yaxes(
        tickmode='array',
        tickvals=list(range(0, len(intervalos_labels), 2)),  # Cada hora
        ticktext=[intervalos_labels[i] for i in range(0, len(intervalos_labels), 2)]
    )
    
    fig.update_xaxes(side="top")
    
    st.plotly_chart(fig, use_container_width=True)

def mostrar_vista_tabla():
    """Vista en tabla del cronograma mensual"""
    cronograma = st.session_state.cronograma
    
    data = []
    for key, asig in cronograma.items():
        # Formatear hora en 30 minutos
        hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
        
        data.append({
            'Semana': f"S{asig['semana']}",
            'Día': asig['dia'],
            'Hora': hora_str,
            'Tarea': asig['tarea'],
            'Roommate': asig['roommate'],
            'Duración': f"{asig['duracion']}min"
        })
    
    df = pd.DataFrame(data)
    
    st.subheader("📋 Vista Tabla Completa - Cronograma Mensual")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        semana_filtro = st.selectbox("Filtrar por semana:", ["Todas"] + [f"S{i}" for i in range(1, 5)])
    
    with col2:
        roommate_filtro = st.selectbox("Filtrar por roommate:", ["Todos"] + [rm.nombre for rm in st.session_state.roommates])
    
    with col3:
        dia_filtro = st.selectbox("Filtrar por día:", ["Todos"] + ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if semana_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Semana'] == semana_filtro]
    
    if roommate_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Roommate'] == roommate_filtro]
    
    if dia_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Día'] == dia_filtro]
    
    # Ordenar por semana, día y hora
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df_filtrado['Día_Order'] = df_filtrado['Día'].map(lambda x: orden_dias.index(x))
    df_filtrado = df_filtrado.sort_values(['Semana', 'Día_Order', 'Hora'])
    df_filtrado = df_filtrado.drop('Día_Order', axis=1)
    
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    # Botón de descarga
    csv = df_filtrado.to_csv(index=False)
    st.download_button("📥 Descargar CSV", csv, "cronograma_mensual.csv", "text/csv")
    
    # Estadísticas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tareas", len(df_filtrado))
    
    with col2:
        tiempo_total = df_filtrado['Duración'].str.replace('min', '').astype(int).sum()
        st.metric("Tiempo Total", f"{tiempo_total//60}h {tiempo_total%60}min")
    
    with col3:
        st.metric("Roommates Activos", df_filtrado['Roommate'].nunique())
    
    with col4:
        st.metric("Días Cubiertos", df_filtrado['Día'].nunique())
        
def mostrar_opciones_exportacion():
    if not st.session_state.cronograma:
        return
    
    st.subheader("📥 Exportar Cronograma")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Exportar Excel Completo", type="primary"):
            exportar_excel_completo()
    
    with col2:
        if st.button("📋 Exportar CSV Simple"):
            exportar_csv_simple()
    
    with col3:
        if st.button("📅 Exportar Calendario PDF"):
            st.info("Función PDF próximamente...")

def exportar_excel_completo():
    try:
        from export_utils import ExportadorCalendarios
        
        with st.spinner("Generando archivo Excel..."):
            exportador = ExportadorCalendarios(
                st.session_state.cronograma,
                st.session_state.roommates,
                st.session_state.tareas
            )
            
            buffer = exportador.exportar_excel_completo()
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cronograma_mensual_{timestamp}.xlsx"
            
            st.download_button(
                label="⬇️ Descargar Excel",
                data=buffer,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Descarga el cronograma completo en formato Excel con múltiples hojas"
            )
            
            st.success("✅ Archivo Excel generado correctamente")
            
            # Mostrar vista previa del contenido
            with st.expander("📋 Vista previa del contenido del Excel", expanded=False):
                st.write("**Hojas incluidas en el archivo:**")
                st.write("1. 📊 **Resumen General** - Todas las asignaciones ordenadas")
                st.write("2. 📅 **Semana 1-4** - Calendarios semanales con intervalos de 30 min")
                st.write("3. 👥 **Por Roommates** - Vista organizada por persona")
                st.write("4. 📈 **Estadísticas** - Métricas y análisis del cronograma")
                st.write("5. 📋 **Lista de Tareas** - Catálogo completo de tareas disponibles")
    
    except Exception as e:
        st.error(f"Error al generar Excel: {e}")

def exportar_csv_simple():
    try:
        from export_utils import ExportadorCalendarios
        
        exportador = ExportadorCalendarios(
            st.session_state.cronograma,
            st.session_state.roommates,
            st.session_state.tareas
        )
        
        csv_data = exportador.exportar_csv_simple()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cronograma_simple_{timestamp}.csv"
        
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            help="Descarga el cronograma en formato CSV simple para Excel/Google Sheets"
        )
        
        st.success("✅ Archivo CSV generado correctamente")
    
    except Exception as e:
        st.error(f"Error al generar CSV: {e}")