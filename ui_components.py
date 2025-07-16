import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
import calendar
from models import Roommate, Tarea, RangoTiempo, CronogramaSemanal, Asignacion, TAREAS_PREDETERMINADAS
from genetic_algorithm import AlgoritmoGenetico

class UIComponentsMejorado:
    
    def __init__(self):
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.categorias_tareas = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
        self.colores_roommates = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
            '#DDA0DD', '#FF7F50', '#87CEEB', '#DEB887', '#F0E68C'
        ]
        self._inicializar_contadores()
    
    def _inicializar_contadores(self):
        if 'form_counter_roommate' not in st.session_state:
            st.session_state.form_counter_roommate = 0
        if 'form_counter_tarea' not in st.session_state:
            st.session_state.form_counter_tarea = 0
    
    def mostrar_vista_calendario_mensual(self):
        """NUEVA: Vista de calendario mensual con 4 semanas"""
        st.subheader("📅 Vista de Calendario Mensual (4 Semanas)")
        
        if not st.session_state.cronograma:
            st.warning("No hay cronograma disponible")
            return
        
        # Selector de mes
        col1, col2 = st.columns([1, 3])
        
        with col1:
            año_actual = datetime.now().year
            mes_actual = datetime.now().month
            
            año_seleccionado = st.selectbox("Año:", range(año_actual, año_actual + 3), index=0)
            mes_seleccionado = st.selectbox("Mes:", range(1, 13), index=mes_actual-1, 
                                          format_func=lambda x: calendar.month_name[x])
        
        # Crear mapeo de colores
        roommates_unicos = list(set(asig['roommate'] for asig in st.session_state.cronograma.values()))
        color_map = {roommate: self.colores_roommates[i % len(self.colores_roommates)] 
                    for i, roommate in enumerate(roommates_unicos)}
        
        # Generar las 4 semanas del mes
        primer_dia = datetime(año_seleccionado, mes_seleccionado, 1)
        dias_mes = calendar.monthrange(año_seleccionado, mes_seleccionado)[1]
        
        # Dividir en 4 semanas
        semanas = []
        fecha_actual = primer_dia
        
        for semana_num in range(4):
            semana_dias = []
            inicio_semana = fecha_actual
            
            for _ in range(7):
                if fecha_actual.month == mes_seleccionado:
                    semana_dias.append(fecha_actual)
                else:
                    semana_dias.append(None)
                fecha_actual += timedelta(days=1)
            
            semanas.append({
                'numero': semana_num + 1,
                'dias': semana_dias,
                'inicio': inicio_semana
            })
        
        # Mostrar las 4 semanas en grid 2x2
        col1, col2 = st.columns(2)
        
        for i, semana in enumerate(semanas):
            with col1 if i % 2 == 0 else col2:
                self._mostrar_semana_calendario(semana, color_map, roommates_unicos)
        
        # Leyenda
        self._mostrar_leyenda_colores(roommates_unicos, color_map)
    
    def _mostrar_semana_calendario(self, semana, color_map, roommates_unicos):
        """Muestra una semana individual del calendario"""
        st.markdown(f"### 📅 Semana {semana['numero']}")
        
        # Crear matriz para la semana (intervalos de 30 min: 6:00 - 23:30)
        intervalos_30min = []
        for h in range(6, 24):
            for m in [0, 30]:
                intervalos_30min.append(f"{h:02d}:{m:02d}")
        
        # Días de la semana
        dias_nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        
        # Crear datos para heatmap
        calendar_data = np.zeros((len(intervalos_30min), 7))
        calendar_text = [['' for _ in range(7)] for _ in range(len(intervalos_30min))]
        calendar_colors = [['rgba(240,240,240,0.3)' for _ in range(7)] for _ in range(len(intervalos_30min))]
        
        # Mapear asignaciones a la semana
        for asignacion in st.session_state.cronograma.values():
            dia_idx = self.dias_semana.index(asignacion['dia'])
            hora_inicio = asignacion['hora']
            duracion_horas = asignacion['duracion'] / 60
            roommate = asignacion['roommate']
            tarea = asignacion['tarea']
            
            # Convertir a índices de 30 minutos
            inicio_idx = int((hora_inicio - 6) * 2)
            fin_idx = int(inicio_idx + (duracion_horas * 2))
            
            for idx in range(max(0, inicio_idx), min(len(intervalos_30min), fin_idx)):
                if 0 <= dia_idx < 7:
                    calendar_data[idx][dia_idx] = 1
                    calendar_text[idx][dia_idx] = f"{roommate}<br>{tarea[:15]}"
                    calendar_colors[idx][dia_idx] = color_map.get(roommate, '#CCCCCC')
        
        # Crear heatmap mejorado
        fig = go.Figure()
        
        # Agregar heatmap base
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
        
        # Agregar rectángulos de colores
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
        
        # Configurar layout
        fig.update_layout(
            title=f"Semana {semana['numero']} - {semana['inicio'].strftime('%d/%m')}",
            xaxis_title="Días",
            yaxis_title="Horarios",
            height=400,
            font=dict(size=10),
            margin=dict(l=50, r=20, t=50, b=20)
        )
        
        # Configurar ejes
        fig.update_xaxes(side="top", tickangle=0)
        fig.update_yaxes(
            tickmode='linear',
            tick0=0,
            dtick=4,  # Mostrar cada 2 horas
            tickvals=list(range(0, len(intervalos_30min), 4)),
            ticktext=[intervalos_30min[i] for i in range(0, len(intervalos_30min), 4)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _mostrar_leyenda_colores(self, roommates_unicos, color_map):
        """Muestra la leyenda de colores mejorada"""
        st.subheader("🎨 Leyenda de Roommates")
        
        # Crear grid de leyenda
        cols = st.columns(min(4, len(roommates_unicos)))
        
        for i, roommate in enumerate(roommates_unicos):
            with cols[i % len(cols)]:
                color = color_map[roommate]
                st.markdown(f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    margin-bottom: 10px;
                    padding: 8px;
                    border-radius: 8px;
                    background-color: {color}20;
                    border-left: 4px solid {color};
                ">
                    <div style="
                        width: 16px; 
                        height: 16px; 
                        background-color: {color}; 
                        border-radius: 50%; 
                        margin-right: 8px;
                        border: 2px solid white;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    "></div>
                    <span style="font-weight: bold; color: #333;"><b>{roommate}</b></span>
                </div>
                """, unsafe_allow_html=True)
    
    def mostrar_configuracion_roommates(self):
        """Configuración mejorada de roommates con vista individual"""
        st.subheader("👥 Gestión de Roommates")
        
        with st.expander("➕ Agregar Nuevo Roommate", expanded=True):
            self._formulario_roommate_30min()
        
        self._mostrar_roommates_existentes_con_calendario()
    
    def _formulario_roommate_30min(self):
        """Formulario con intervalos de 30 minutos"""
        counter = st.session_state.form_counter_roommate
        
        st.write("### 👤 Datos del Roommate")
        
        nombre = st.text_input("Nombre del roommate", key=f"nombre_rm_{counter}")
        tiempo_disponible = st.number_input("Horas objetivo por semana", min_value=1, max_value=50, value=15, key=f"tiempo_{counter}")
        
        st.write("**⏰ Horarios Disponibles (intervalos de 30 min):**")
        horarios_disponibles = {}
        
        for dia in self.dias_semana:
            st.write(f"**📅 {dia}**")
            num_rangos = st.number_input(f"Rangos horarios {dia}", min_value=0, max_value=4, value=0, key=f"num_rangos_{dia}_{counter}")
            
            rangos_dia = []
            for i in range(num_rangos):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Generar opciones de 30 en 30 minutos
                    opciones_hora = []
                    for h in range(5, 24):
                        opciones_hora.append(h)      # 8:00
                        opciones_hora.append(h + 0.5)  # 8:30
                    
                    inicio = st.selectbox(
                        f"Inicio Rango {i+1}", 
                        opciones_hora, 
                        index=6,  # Default 8:00
                        key=f"inicio_{dia}_{i}_{counter}",
                        format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}"
                    )
                
                with col2:
                    opciones_fin = [h for h in opciones_hora if h > inicio]
                    if not opciones_fin:
                        opciones_fin = [24.0]
                    
                    fin = st.selectbox(
                        f"Fin Rango {i+1}", 
                        opciones_fin,
                        index=min(4, len(opciones_fin)-1),
                        key=f"fin_{dia}_{i}_{counter}",
                        format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}" if x < 24 else "24:00"
                    )
                
                try:
                    rango = RangoTiempo(inicio, fin)
                    rangos_dia.append(rango)
                    duracion = fin - inicio
                    st.success(f"✅ Rango {i+1}: {duracion:.1f}h")
                except ValueError as e:
                    st.error(f"❌ Error: {e}")
            
            if rangos_dia:
                horarios_disponibles[dia] = rangos_dia
        
        # Habilidades y preferencias (mismo código anterior)
        st.write("**🎯 Habilidades (1-10):**")
        habilidades = {}
        cols = st.columns(3)
        for i, categoria in enumerate(self.categorias_tareas):
            with cols[i % 3]:
                habilidades[categoria] = st.slider(f"{categoria}", 1, 10, 5, key=f"hab_{categoria}_{counter}")
        
        st.write("**💭 Preferencias:**")
        preferencias = {}
        cols = st.columns(3)
        for i, categoria in enumerate(self.categorias_tareas):
            with cols[i % 3]:
                preferencias[categoria] = st.selectbox(f"{categoria}", ['neutro', 'prefiere', 'evita'], key=f"pref_{categoria}_{counter}")
        
        # Botones
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Agregar", type="primary", key=f"submit_{counter}"):
                if self._procesar_nuevo_roommate(nombre, horarios_disponibles, habilidades, preferencias, tiempo_disponible):
                    st.session_state.form_counter_roommate += 1
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Limpiar", key=f"clear_{counter}"):
                st.session_state.form_counter_roommate += 1
                st.rerun()
        
        with col3:
            if st.button("📝 Ejemplo", key=f"example_{counter}"):
                self._cargar_ejemplo_roommate()
    
    def _mostrar_roommates_existentes_con_calendario(self):
        """Muestra roommates con vista de calendario individual"""
        if st.session_state.roommates:
            st.subheader("👥 Roommates Registrados")
            
            for i, rm in enumerate(st.session_state.roommates):
                with st.expander(f"👤 {rm.nombre} - {rm.total_horas_disponibles():.1f}h disponibles", expanded=False):
                    
                    # Selector de vista
                    vista_tipo = st.radio(
                        f"Vista para {rm.nombre}:",
                        ["📋 Información Básica", "📅 Calendario de Disponibilidad"],
                        key=f"vista_rm_{i}",
                        horizontal=True
                    )
                    
                    if vista_tipo == "📋 Información Básica":
                        self._mostrar_info_basica_roommate(rm, i)
                    else:
                        self._mostrar_calendario_individual_roommate(rm)
    
    def _mostrar_info_basica_roommate(self, rm, index):
        """Muestra información básica del roommate"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📅 Horarios disponibles:**")
            for dia, rangos in rm.horarios_disponibles.items():
                if rangos:
                    st.write(f"**{dia}:**")
                    for j, rango in enumerate(rangos, 1):
                        st.write(f"  └ Rango {j}: {rango} ({rango.duracion_horas():.1f}h)")
        
        with col2:
            st.write("**🎯 Habilidades:**")
            for categoria, nivel in rm.habilidades.items():
                color = "🟢" if nivel >= 8 else "🔵" if nivel >= 6 else "🟡" if nivel >= 4 else "🔴"
                st.write(f"{color} {categoria}: {nivel}/10")
            
            st.write("**💭 Preferencias:**")
            for categoria, pref in rm.preferencias.items():
                emoji = {"prefiere": "💚", "evita": "❌", "neutro": "⚪"}[pref]
                st.write(f"{emoji} {categoria}: {pref.title()}")
        
        if st.button(f"🗑️ Eliminar {rm.nombre}", key=f"del_rm_{index}"):
            st.session_state.roommates.pop(index)
            st.rerun()
    
    def _mostrar_calendario_individual_roommate(self, roommate):
        """NUEVA: Muestra calendario individual de disponibilidad del roommate"""
        st.write(f"### 📅 Disponibilidad de {roommate.nombre}")
        
        # Crear matriz de disponibilidad (intervalos de 30 min)
        intervalos_30min = []
        for h in range(6, 24):
            for m in [0, 30]:
                intervalos_30min.append(h + m/60)
        
        intervalos_labels = [f"{int(h):02d}:{int((h % 1) * 60):02d}" for h in intervalos_30min]
        
        # Matriz de disponibilidad
        disponibilidad_data = np.zeros((len(intervalos_30min), 7))
        
        for dia_idx, dia in enumerate(self.dias_semana):
            if dia in roommate.horarios_disponibles:
                for rango in roommate.horarios_disponibles[dia]:
                    # Marcar intervalos disponibles
                    for i, hora in enumerate(intervalos_30min):
                        if rango.contiene_hora(hora):
                            disponibilidad_data[i][dia_idx] = 1
        
        # Crear heatmap de disponibilidad
        fig = go.Figure(data=go.Heatmap(
            z=disponibilidad_data,
            x=self.dias_semana,
            y=intervalos_labels,
            colorscale=[
                [0, 'rgba(255,200,200,0.3)'],  # No disponible - rojo claro
                [1, 'rgba(100,200,100,0.8)']   # Disponible - verde
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
            xaxis_title="Días de la Semana",
            yaxis_title="Horarios (intervalos de 30 min)",
            height=500,
            font=dict(size=10)
        )
        
        # Mostrar cada 2 horas en el eje Y
        fig.update_yaxes(
            tickmode='array',
            tickvals=list(range(0, len(intervalos_labels), 4)),
            ticktext=[intervalos_labels[i] for i in range(0, len(intervalos_labels), 4)]
        )
        
        fig.update_xaxes(side="top")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas de disponibilidad
        col1, col2, col3 = st.columns(3)
        
        total_slots = len(intervalos_30min) * 7
        slots_disponibles = int(np.sum(disponibilidad_data))
        porcentaje_disponibilidad = (slots_disponibles / total_slots) * 100
        
        with col1:
            st.metric("Total Intervalos", f"{slots_disponibles}/{total_slots}")
        with col2:
            st.metric("Disponibilidad", f"{porcentaje_disponibilidad:.1f}%")
        with col3:
            horas_totales = slots_disponibles * 0.5
            st.metric("Horas Totales", f"{horas_totales:.1f}h")
    
    def mostrar_configuracion_tareas_mejorada(self):
        """Configuración mejorada con tareas predeterminadas"""
        st.subheader("📋 Gestión de Tareas Domésticas")
        
        # Tabs para tareas predeterminadas y manuales
        tab1, tab2 = st.tabs(["🏪 Tareas Predeterminadas", "✏️ Tareas Manuales"])
        
        with tab1:
            self._mostrar_tareas_predeterminadas()
        
        with tab2:
            self._mostrar_formulario_tarea_manual()
        
        # Tareas existentes
        self._mostrar_tareas_existentes()
    
    def _mostrar_tareas_predeterminadas(self):
        """Catálogo de tareas predeterminadas"""
        st.write("### 🏪 Catálogo de Tareas Comunes")
        st.info("💡 Selecciona tareas del catálogo y agrégalas automáticamente")
        
        # Selector de categoría
        categoria_filtro = st.selectbox(
            "Filtrar por categoría:",
            ["Todas"] + self.categorias_tareas,
            key="filtro_categoria_pred"
        )
        
        # Mostrar tareas por categoría
        tareas_mostrar = TAREAS_PREDETERMINADAS if categoria_filtro == "Todas" else {categoria_filtro: TAREAS_PREDETERMINADAS.get(categoria_filtro, [])}
        
        for categoria, tareas_cat in tareas_mostrar.items():
            if tareas_cat:  # Solo mostrar si hay tareas
                st.write(f"#### {categoria}")
                
                # Grid de tareas
                cols = st.columns(2)
                
                for i, tarea_info in enumerate(tareas_cat):
                    with cols[i % 2]:
                        # Card de tarea
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                border: 1px solid #ddd;
                                border-radius: 8px;
                                padding: 12px;
                                margin-bottom: 10px;
                                background-color: #f9f9f9;
                            ">
                                <h5 style="margin: 0 0 8px 0; color: #333;">📝 {tarea_info['nombre']}</h5>
                                <p style="margin: 4px 0; font-size: 14px; color: #666;">
                                    ⏱️ {tarea_info['tiempo']} min | 
                                    📊 Dificultad: {tarea_info['dificultad']}/10 | 
                                    📅 {tarea_info['frecuencia'].title()}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Configuración adicional
                            config_expander = st.expander(f"⚙️ Configurar {tarea_info['nombre']}", expanded=False)
                            
                            with config_expander:
                                # Personalizar tarea
                                nombre_personalizado = st.text_input(
                                    "Nombre personalizado:", 
                                    value=tarea_info['nombre'],
                                    key=f"nombre_pred_{categoria}_{i}"
                                )
                                
                                col_a, col_b = st.columns(2)
                                
                                with col_a:
                                    tiempo_personalizado = st.selectbox(
                                        "Duración:", 
                                        [30, 60, 90, 120, 150, 180, 210, 240],
                                        index=[30, 60, 90, 120, 150, 180, 210, 240].index(tarea_info['tiempo']) if tarea_info['tiempo'] in [30, 60, 90, 120, 150, 180, 210, 240] else 1,
                                        key=f"tiempo_pred_{categoria}_{i}",
                                        format_func=lambda x: f"{x} min"
                                    )
                                
                                with col_b:
                                    dificultad_personalizada = st.slider(
                                        "Dificultad:", 
                                        1, 10, 
                                        tarea_info['dificultad'],
                                        key=f"dif_pred_{categoria}_{i}"
                                    )
                                
                                # Hora preferida
                                hora_preferida = st.selectbox(
                                    "Hora preferida:",
                                    [None] + [h + m/60 for h in range(6, 24) for m in [0, 30]],
                                    key=f"hora_pred_{categoria}_{i}",
                                    format_func=lambda x: "Sin preferencia" if x is None else f"{int(x):02d}:{int((x % 1) * 60):02d}"
                                )
                                
                                # Días específicos
                                if tarea_info['frecuencia'] == 'semanal':
                                    st.write("**Días específicos (opcional):**")
                                    dias_especificos = []
                                    cols_dias = st.columns(7)
                                    for j, dia in enumerate(self.dias_semana):
                                        with cols_dias[j]:
                                            if st.checkbox(dia, key=f"dia_pred_{categoria}_{i}_{j}"):
                                                dias_especificos.append(dia)
                                    if not dias_especificos:
                                        dias_especificos = None
                                else:
                                    dias_especificos = None
                                
                                # Botón para agregar
                                if st.button(f"➕ Agregar {nombre_personalizado}", key=f"add_pred_{categoria}_{i}", type="primary"):
                                    if self._agregar_tarea_predeterminada(
                                        nombre_personalizado, 
                                        categoria, 
                                        tarea_info['frecuencia'], 
                                        tiempo_personalizado, 
                                        dificultad_personalizada, 
                                        hora_preferida, 
                                        dias_especificos
                                    ):
                                        st.success(f"✅ Tarea '{nombre_personalizado}' agregada")
                                        st.rerun()
    
    def _agregar_tarea_predeterminada(self, nombre, categoria, frecuencia, tiempo, dificultad, hora_preferida, dias_especificos):
        """Agrega una tarea predeterminada a la lista"""
        
        # Verificar duplicados
        nombres_existentes = [tarea.nombre.lower() for tarea in st.session_state.tareas]
        if nombre.lower().strip() in nombres_existentes:
            st.error(f"❌ La tarea '{nombre}' ya existe")
            return False
        
        try:
            nueva_tarea = Tarea(
                nombre=nombre.strip(),
                frecuencia=frecuencia,
                tiempo_estimado=tiempo,
                dificultad=dificultad,
                categoria=categoria,
                dias_requeridos=dias_especificos or [],
                hora_preferida=hora_preferida
            )
            
            st.session_state.tareas.append(nueva_tarea)
            return True
            
        except ValueError as e:
            st.error(f"❌ Error: {e}")
            return False
    
    def _mostrar_formulario_tarea_manual(self):
        """Formulario para tareas manuales"""
        st.write("### ✏️ Crear Tarea Manual")
        
        counter = st.session_state.form_counter_tarea
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_tarea = st.text_input("Nombre de la tarea", key=f"nombre_manual_{counter}")
            categoria = st.selectbox("Categoría", self.categorias_tareas, key=f"cat_manual_{counter}")
            frecuencia = st.selectbox("Frecuencia", ["diaria", "semanal", "mensual"], key=f"freq_manual_{counter}")
        
        with col2:
            opciones_tiempo = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
            tiempo_estimado = st.selectbox("Duración", opciones_tiempo, index=1, 
                                         format_func=lambda x: f"{x} min", key=f"tiempo_manual_{counter}")
            dificultad = st.slider("Dificultad (1-10)", 1, 10, 5, key=f"dif_manual_{counter}")
            
            # Hora preferida con intervalos de 30 min
            opciones_hora = [None] + [h + m/60 for h in range(6, 24) for m in [0, 30]]
            hora_preferida = st.selectbox(
                "Hora preferida",
                opciones_hora,
                key=f"hora_manual_{counter}",
                format_func=lambda x: "Sin preferencia" if x is None else f"{int(x):02d}:{int((x % 1) * 60):02d}"
            )
        
        # Días específicos
        dias_especificos = None
        if frecuencia == "semanal":
            st.write("**Días específicos (opcional):**")
            dias_especificos = []
            cols = st.columns(7)
            for i, dia in enumerate(self.dias_semana):
                with cols[i]:
                    if st.checkbox(dia, key=f"dia_manual_{dia}_{counter}"):
                        dias_especificos.append(dia)
            if not dias_especificos:
                dias_especificos = None
        
        # Botones
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Agregar Tarea Manual", type="primary", key=f"submit_manual_{counter}"):
                if self._procesar_tarea_manual(nombre_tarea, categoria, frecuencia, tiempo_estimado, dificultad, hora_preferida, dias_especificos):
                    st.session_state.form_counter_tarea += 1
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Limpiar Formulario", key=f"clear_manual_{counter}"):
                st.session_state.form_counter_tarea += 1
                st.rerun()
    
    def _procesar_tarea_manual(self, nombre_tarea, categoria, frecuencia, tiempo_estimado, dificultad, hora_preferida, dias_especificos):
        """Procesa tarea manual"""
        if not nombre_tarea or not nombre_tarea.strip():
            st.error("❌ Nombre de tarea requerido")
            return False
        
        nombres_existentes = [tarea.nombre.lower() for tarea in st.session_state.tareas]
        if nombre_tarea.lower().strip() in nombres_existentes:
            st.error(f"❌ Tarea '{nombre_tarea.strip()}' ya existe")
            return False
        
        try:
            nueva_tarea = Tarea(
                nombre=nombre_tarea.strip(),
                frecuencia=frecuencia,
                tiempo_estimado=tiempo_estimado,
                dificultad=dificultad,
                categoria=categoria,
                dias_requeridos=dias_especificos or [],
                hora_preferida=hora_preferida
            )
            
            st.session_state.tareas.append(nueva_tarea)
            st.success(f"✅ Tarea manual '{nombre_tarea.strip()}' agregada")
            return True
            
        except ValueError as e:
            st.error(f"❌ Error: {e}")
            return False
    
    def _mostrar_tareas_existentes(self):
        """Muestra tareas existentes con mejor organización"""
        if st.session_state.tareas:
            st.subheader("📋 Tareas Registradas")
            
            # Resumen por categoría
            tareas_por_categoria = {}
            for tarea in st.session_state.tareas:
                if tarea.categoria not in tareas_por_categoria:
                    tareas_por_categoria[tarea.categoria] = []
                tareas_por_categoria[tarea.categoria].append(tarea)
            
            # Mostrar por categoría
            for categoria, tareas_cat in tareas_por_categoria.items():
                with st.expander(f"📁 {categoria} ({len(tareas_cat)} tareas)", expanded=False):
                    
                    for i, tarea in enumerate(tareas_cat):
                        col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
                        
                        with col1:
                            st.write(f"**{tarea.nombre}**")
                            if tarea.hora_preferida:
                                hora_str = f"{int(tarea.hora_preferida):02d}:{int((tarea.hora_preferida % 1) * 60):02d}"
                                st.caption(f"Hora preferida: {hora_str}")
                        
                        with col2:
                            st.write(f"⏱️ {tarea.tiempo_estimado} min")
                            st.write(f"📊 Dificultad: {tarea.dificultad}/10")
                        
                        with col3:
                            st.write(f"📅 {tarea.frecuencia.title()}")
                            if tarea.dias_requeridos:
                                st.caption(f"Días: {', '.join(tarea.dias_requeridos)}")
                        
                        with col4:
                            # Encontrar índice global
                            indice_global = st.session_state.tareas.index(tarea)
                            if st.button("🗑️", key=f"del_tarea_{indice_global}", help=f"Eliminar {tarea.nombre}"):
                                st.session_state.tareas.pop(indice_global)
                                st.rerun()
                        
                        st.divider()
            
            # Estadísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tareas", len(st.session_state.tareas))
            with col2:
                tiempo_total = sum(tarea.tiempo_estimado * tarea.get_repeticiones_semanales() for tarea in st.session_state.tareas)
                st.metric("Tiempo Total/Semana", f"{tiempo_total} min")
            with col3:
                st.metric("Categorías", len(tareas_por_categoria))
    
    def _procesar_nuevo_roommate(self, nombre, horarios, habilidades, preferencias, tiempo_disponible):
        """Procesa nuevo roommate (sin validar conflictos)"""
        if not nombre or not nombre.strip():
            st.error("❌ Nombre requerido")
            return False
        
        if not horarios:
            st.error("❌ Al menos un horario requerido")
            return False
        
        nombres_existentes = [rm.nombre.lower() for rm in st.session_state.roommates]
        if nombre.lower().strip() in nombres_existentes:
            st.error(f"❌ Roommate '{nombre.strip()}' ya existe")
            return False
        
        try:
            nuevo_roommate = Roommate(
                nombre=nombre.strip(),
                horarios_disponibles=horarios,
                habilidades=habilidades,
                preferencias=preferencias,
                tiempo_total_disponible=tiempo_disponible
            )
            
            st.session_state.roommates.append(nuevo_roommate)
            st.success(f"✅ Roommate '{nombre.strip()}' agregado")
            return True
            
        except ValueError as e:
            st.error(f"❌ Error: {e}")
            return False