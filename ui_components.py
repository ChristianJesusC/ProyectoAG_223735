import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import List, Dict
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas, EspacioHogar
from calendar_views import mostrar_calendario_individual

class UIComponentsMejorado:
    
    def __init__(self):
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.categorias_tareas = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
    
    def mostrar_configuracion_roommates(self):
        """Configuración de roommates y tareas"""
        tab1, tab2 = st.tabs(["👥 Roommates", "📋 Tareas"])
        
        with tab1:
            self._configurar_roommates()
        
        with tab2:
            self._configurar_tareas()
    
    def _configurar_roommates(self):
        st.subheader("Gestión de Roommates")
        
        with st.expander("➕ Agregar Roommate", expanded=True):
            self._formulario_roommate()
        
        if st.session_state.roommates:
            st.subheader("Roommates Registrados")
            for i, rm in enumerate(st.session_state.roommates):
                with st.expander(f"👤 {rm.nombre} - {rm.total_horas_disponibles():.1f}h disponibles"):
                    vista_tipo = st.radio(
                        f"Vista para {rm.nombre}:",
                        ["📋 Información", "📅 Calendario Individual"],
                        key=f"vista_rm_{i}",
                        horizontal=True
                    )
                    
                    if vista_tipo == "📋 Información":
                        self._mostrar_info_roommate(rm)
                    else:
                        mostrar_calendario_individual(rm)
                    
                    if st.button(f"🗑️ Eliminar", key=f"del_rm_{i}"):
                        st.session_state.roommates.pop(i)
                        st.rerun()
    
    def _formulario_roommate(self):
        """Formulario para agregar roommate"""
        counter = st.session_state.get('form_counter', 0)
        
        nombre = st.text_input("Nombre del roommate", key=f"nombre_{counter}")
        tiempo_obj = st.number_input("Horas objetivo/semana", 5, 50, 15, key=f"tiempo_{counter}")
        
        st.write("**Horarios disponibles (intervalos de 30 min):**")
        horarios = {}
        
        for dia in self.dias_semana:
            with st.container():
                st.write(f"**{dia}:**")
                num_rangos = st.number_input(f"Rangos para {dia}", 0, 3, 0, key=f"rangos_{dia}_{counter}")
                
                rangos_dia = []
                for i in range(num_rangos):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        opciones_hora = []
                        for h in range(5, 24):
                            opciones_hora.append(h)
                            opciones_hora.append(h + 0.5)
                        
                        inicio = st.selectbox(
                            f"Inicio rango {i+1}", 
                            opciones_hora, 
                            index=6, 
                            key=f"ini_{dia}_{i}_{counter}",
                            format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}"
                        )
                    
                    with col2:
                        opciones_fin = [h for h in opciones_hora if h > inicio]
                        if not opciones_fin:
                            opciones_fin = [24.0]
                        
                        fin = st.selectbox(
                            f"Fin rango {i+1}", 
                            opciones_fin, 
                            index=min(4, len(opciones_fin)-1), 
                            key=f"fin_{dia}_{i}_{counter}",
                            format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}" if x < 24 else "24:00"
                        )
                    
                    with col3:
                        st.write(f"⏱️ {fin-inicio:.1f}h")
                    
                    try:
                        rangos_dia.append(RangoTiempo(inicio, fin))
                    except:
                        st.error("Rango inválido")
                
                if rangos_dia:
                    horarios[dia] = rangos_dia
        
        st.write("**Habilidades y Preferencias:**")
        habilidades = {}
        preferencias = {}
        
        cols = st.columns(3)
        for i, cat in enumerate(self.categorias_tareas):
            with cols[i % 3]:
                habilidades[cat] = st.slider(f"Habilidad en {cat}", 1, 10, 5, key=f"hab_{cat}_{counter}")
                preferencias[cat] = st.selectbox(f"Preferencia {cat}", ['neutro', 'prefiere', 'evita'], key=f"pref_{cat}_{counter}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Agregar", type="primary"):
                if self._procesar_roommate(nombre, horarios, habilidades, preferencias, tiempo_obj):
                    st.session_state.form_counter = counter + 1
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Limpiar"):
                st.session_state.form_counter = counter + 1
                st.rerun()
    
    def _procesar_roommate(self, nombre, horarios, habilidades, preferencias, tiempo_obj):
        """Procesa y agrega un nuevo roommate"""
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
            roommate = Roommate(nombre.strip(), horarios, habilidades, preferencias, tiempo_obj)
            st.session_state.roommates.append(roommate)
            st.success(f"✅ Roommate '{nombre.strip()}' agregado")
            return True
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return False
    
    def _mostrar_info_roommate(self, rm):
        """Muestra información básica del roommate"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Horarios:**")
            for dia, rangos in rm.horarios_disponibles.items():
                if rangos:
                    horas = ", ".join(str(r) for r in rangos)
                    st.write(f"• {dia}: {horas}")
        
        with col2:
            st.write("**Habilidades:**")
            for cat, niv in rm.habilidades.items():
                color = "🟢" if niv >= 8 else "🔵" if niv >= 6 else "🟡" if niv >= 4 else "🔴"
                st.write(f"{color} {cat}: {niv}/10")
            
            st.write("**Preferencias:**")
            for cat, pref in rm.preferencias.items():
                emoji = {"prefiere": "💚", "evita": "❌", "neutro": "⚪"}[pref]
                st.write(f"{emoji} {cat}: {pref.title()}")
    
    def _configurar_tareas(self):
        """Configuración de tareas"""
        st.subheader("Gestión de Tareas")
        
        tab1, tab2 = st.tabs(["🏪 Predeterminadas", "✏️ Personalizadas"])
        
        with tab1:
            self._mostrar_tareas_predeterminadas()
        
        with tab2:
            self._formulario_tarea_personalizada()
        
        self._mostrar_tareas_existentes()
    
    def _mostrar_tareas_predeterminadas(self):
        """Catálogo de tareas predeterminadas"""
        st.write("### Catálogo de Tareas")
        
        categoria_filtro = st.selectbox(
            "Filtrar por categoría:",
            ["Todas"] + self.categorias_tareas
        )
        
        tareas_basicas = TareasPredeterminadas.get_tareas_basicas()
        if categoria_filtro != "Todas":
            tareas_basicas = [t for t in tareas_basicas if t.categoria == categoria_filtro]
        
        tareas_actuales = {t.nombre for t in st.session_state.tareas}
        
        cols = st.columns(2)
        for i, tarea in enumerate(tareas_basicas):
            with cols[i % 2]:
                checked = st.checkbox(
                    f"**{tarea.nombre}**", 
                    value=tarea.nombre in tareas_actuales,
                    key=f"tarea_{tarea.nombre}"
                )
                
                st.caption(f"📅 {tarea.frecuencia} | ⏱️ {tarea.tiempo_estimado}min | 📊 Dificultad: {tarea.dificultad}/10")
                
                if checked and tarea.nombre not in tareas_actuales:
                    st.session_state.tareas.append(tarea)
                elif not checked and tarea.nombre in tareas_actuales:
                    st.session_state.tareas = [t for t in st.session_state.tareas if t.nombre != tarea.nombre]
    
    def _formulario_tarea_personalizada(self):
        """Formulario para tareas personalizadas"""
        st.write("### Crear Tarea Manual")
        
        nombre = st.text_input("Nombre de la tarea")
        
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Categoría", self.categorias_tareas)
            frecuencia = st.selectbox("Frecuencia", ['diaria', 'semanal', 'mensual'])
        
        with col2:
            tiempo = st.selectbox("Duración", [30, 60, 90, 120, 150, 180, 210, 240], format_func=lambda x: f"{x} min")
            dificultad = st.slider("Dificultad", 1, 10, 5)
        
        if st.button("➕ Agregar tarea personalizada"):
            if self._procesar_tarea_manual(nombre, categoria, frecuencia, tiempo, dificultad):
                st.rerun()
    
    def _procesar_tarea_manual(self, nombre, categoria, frecuencia, tiempo, dificultad):
        """Procesa tarea manual"""
        if not nombre or not nombre.strip():
            st.error("❌ Nombre de tarea requerido")
            return False
        
        nombres_existentes = [tarea.nombre.lower() for tarea in st.session_state.tareas]
        if nombre.lower().strip() in nombres_existentes:
            st.error(f"❌ Tarea '{nombre.strip()}' ya existe")
            return False
        
        try:
            nueva_tarea = Tarea(nombre.strip(), frecuencia, tiempo, dificultad, categoria, es_predeterminada=False)
            st.session_state.tareas.append(nueva_tarea)
            st.success(f"✅ Tarea '{nombre.strip()}' agregada")
            return True
        except Exception as e:
            st.error(f"❌ Error: {e}")
            return False
    
    def _mostrar_tareas_existentes(self):
        """Muestra tareas existentes"""
        if st.session_state.tareas:
            st.subheader("Tareas Registradas")
            
            data = []
            for i, t in enumerate(st.session_state.tareas):
                data.append({
                    'Tarea': t.nombre,
                    'Frecuencia': t.frecuencia,
                    'Tiempo': f"{t.tiempo_estimado}min",
                    'Categoría': t.categoria,
                    'Tipo': '🏪' if t.es_predeterminada else '✏️'
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            if len(st.session_state.tareas) > 0:
                tarea_eliminar = st.selectbox(
                    "Eliminar tarea:", 
                    range(len(st.session_state.tareas)), 
                    format_func=lambda x: st.session_state.tareas[x].nombre
                )
                if st.button("🗑️ Eliminar seleccionada"):
                    st.session_state.tareas.pop(tarea_eliminar)
                    st.rerun()
    
    def mostrar_configuracion_espacio(self):
        """Configuración del espacio del hogar"""
        st.markdown("*Define las características de tu hogar para una mejor asignación de tareas*")
        
        espacio = st.session_state.espacio_hogar
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📐 Estructura Básica")
            habitaciones = st.number_input("Número de habitaciones", 1, 10, espacio.habitaciones)
            banos = st.number_input("Número de baños", 1, 5, espacio.banos)
            metros_cuadrados = st.number_input("Metros cuadrados", 30, 500, espacio.metros_cuadrados)
            
            st.subheader("🏡 Espacios Adicionales")
            tiene_jardin = st.checkbox("Jardín", espacio.tiene_jardin)
            tiene_balcon = st.checkbox("Balcón/Terraza", espacio.tiene_balcon)
            tiene_garage = st.checkbox("Garage", espacio.tiene_garage)
        
        with col2:
            st.subheader("🏛️ Áreas Comunes")
            areas_disponibles = ["Sala", "Cocina", "Comedor", "Estudio", "Gimnasio", "Lavandería", "Despensa", "Biblioteca"]
            areas_comunes = st.multiselect("Selecciona las áreas comunes:", areas_disponibles, default=espacio.areas_comunes)
            
            st.subheader("🔧 Equipamiento")
            equipamiento_disponible = ["Aspiradora", "Lavadora", "Lavavajillas", "Secadora", "Robot aspirador", "Hidrolavadora", "Pulidora", "Manguera de jardín", "Cortacésped"]
            equipamiento = st.multiselect("Equipamiento disponible:", equipamiento_disponible, default=espacio.equipamiento)
        
        if st.button("💾 Guardar Configuración del Espacio", type="primary"):
            st.session_state.espacio_hogar = EspacioHogar(
                habitaciones=habitaciones,
                banos=banos,
                areas_comunes=areas_comunes,
                equipamiento=equipamiento,
                metros_cuadrados=metros_cuadrados,
                tiene_jardin=tiene_jardin,
                tiene_balcon=tiene_balcon,
                tiene_garage=tiene_garage
            )
            st.success("✅ Configuración del espacio guardada")
            st.rerun()
        
        self._mostrar_analisis_espacio(espacio)
    
    def _mostrar_analisis_espacio(self, espacio):
        """Análisis del espacio configurado"""
        st.subheader("📊 Análisis del Espacio")
        
        factor_complejidad = espacio.get_factor_complejidad()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Factor Complejidad", f"{factor_complejidad:.2f}")
        with col2:
            tiempo_estimado = len(espacio.areas_comunes) * 45 + espacio.habitaciones * 30
            st.metric("Tiempo Est. Limpieza", f"{tiempo_estimado}min")
        with col3:
            st.metric("Áreas Totales", f"{len(espacio.areas_comunes) + espacio.habitaciones + espacio.banos}")
        with col4:
            nivel_equipamiento = min(10, len(espacio.equipamiento))
            st.metric("Nivel Equipamiento", f"{nivel_equipamiento}/10")
        
        with st.expander("💡 Recomendaciones basadas en tu espacio", expanded=False):
            if factor_complejidad > 1.5:
                st.warning("🏠 **Espacio grande**: Considera más roommates o ajustar tiempos")
            elif factor_complejidad < 0.8:
                st.info("🏠 **Espacio compacto**: Tiempos pueden ser menores")
            
            if not espacio.equipamiento:
                st.warning("🔧 **Sin equipamiento**: Considera agregar herramientas")
            
            if len(espacio.areas_comunes) > 5:
                st.info("🏛️ **Muchas áreas**: Considera rotación semanal")