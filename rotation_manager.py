import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from calendar_views import COLORES_ROOMMATES

class RotationManager:
    
    def __init__(self):
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    def mostrar_plan_rotacion(self):
        """Muestra el plan de rotación mensual completo"""
        st.markdown("*Sistema de rotación para asegurar variedad y experiencia equilibrada*")
        
        if not st.session_state.roommates or not st.session_state.tareas:
            st.warning("Configura roommates y tareas primero")
            return
        
        plan_rotacion = self.generar_plan_rotacion()
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            semana_seleccionada = st.selectbox(
                "Ver semana:",
                ["Todas", "Semana 1", "Semana 2", "Semana 3", "Semana 4"],
                index=0
            )
        
        if semana_seleccionada == "Todas":
            for semana in range(1, 5):
                self.mostrar_rotacion_semana(plan_rotacion, semana)
        else:
            semana_num = int(semana_seleccionada.split()[-1])
            self.mostrar_rotacion_semana(plan_rotacion, semana_num)
        
        st.subheader("📈 Análisis de Rotación")
        self.analizar_rotacion(plan_rotacion)
    
    def generar_plan_rotacion(self):
        """Genera un plan de rotación mensual"""
        roommates = [rm.nombre for rm in st.session_state.roommates]
        tareas_semanales = [t for t in st.session_state.tareas if t.frecuencia == 'semanal']
        
        plan = {}
        
        for semana in range(1, 5):
            plan[semana] = {}
            
            for i, tarea in enumerate(tareas_semanales):
                roommate_index = (i + semana - 1) % len(roommates)
                plan[semana][tarea.nombre] = roommates[roommate_index]
        
        return plan
    
    def mostrar_rotacion_semana(self, plan_rotacion, semana):
        """Muestra el plan de rotación para una semana específica"""
        st.markdown(f"### 📅 Semana {semana}")
        
        if semana not in plan_rotacion:
            st.warning(f"No hay plan para la semana {semana}")
            return
        
        data = []
        for tarea, roommate in plan_rotacion[semana].items():
            tarea_obj = next((t for t in st.session_state.tareas if t.nombre == tarea), None)
            if tarea_obj:
                data.append({
                    'Tarea': tarea,
                    'Roommate Asignado': roommate,
                    'Categoría': tarea_obj.categoria,
                    'Tiempo': f"{tarea_obj.tiempo_estimado}min",
                    'Dificultad': f"{tarea_obj.dificultad}/10",
                    'Área': getattr(tarea_obj, 'area_espacio', 'General')
                })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            resumen = {}
            for item in data:
                rm = item['Roommate Asignado']
                if rm not in resumen:
                    resumen[rm] = {'tareas': 0, 'tiempo': 0}
                resumen[rm]['tareas'] += 1
                resumen[rm]['tiempo'] += int(item['Tiempo'].replace('min', ''))
            
            st.write("**Resumen por Roommate:**")
            cols = st.columns(len(resumen))
            for i, (rm, stats) in enumerate(resumen.items()):
                with cols[i]:
                    st.metric(f"👤 {rm}", f"{stats['tareas']} tareas", f"{stats['tiempo']}min")
    
    def analizar_rotacion(self, plan_rotacion):
        """Analiza el balance y efectividad del plan de rotación"""
        conteo_roommate = {}
        tiempo_roommate = {}
        experiencia_categoria = {}
        
        for semana in plan_rotacion.values():
            for tarea_nombre, roommate in semana.items():
                if roommate not in conteo_roommate:
                    conteo_roommate[roommate] = 0
                    tiempo_roommate[roommate] = 0
                    experiencia_categoria[roommate] = set()
                
                conteo_roommate[roommate] += 1
                
                tarea_obj = next((t for t in st.session_state.tareas if t.nombre == tarea_nombre), None)
                if tarea_obj:
                    tiempo_roommate[roommate] += tarea_obj.tiempo_estimado
                    experiencia_categoria[roommate].add(tarea_obj.categoria)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if conteo_roommate:
                fig_tareas = px.bar(
                    x=list(conteo_roommate.keys()),
                    y=list(conteo_roommate.values()),
                    title="Distribución de Tareas Semanales por Roommate",
                    labels={'x': 'Roommate', 'y': 'Número de Tareas'},
                    color=list(conteo_roommate.keys()),
                    color_discrete_sequence=COLORES_ROOMMATES[:len(conteo_roommate)]
                )
                st.plotly_chart(fig_tareas, use_container_width=True)
        
        with col2:
            if experiencia_categoria:
                experiencia_datos = []
                for rm, categorias in experiencia_categoria.items():
                    experiencia_datos.append({
                        'Roommate': rm,
                        'Categorías Experimentadas': len(categorias),
                        'Diversidad': f"{len(categorias)}/6"
                    })
                
                df_exp = pd.DataFrame(experiencia_datos)
                fig_exp = px.bar(
                    df_exp,
                    x='Roommate',
                    y='Categorías Experimentadas',
                    title="Diversidad de Experiencia por Roommate",
                    color='Roommate',
                    color_discrete_sequence=COLORES_ROOMMATES[:len(experiencia_datos)]
                )
                st.plotly_chart(fig_exp, use_container_width=True)
        
        if conteo_roommate:
            col1, col2, col3 = st.columns(3)
            
            tareas_values = list(conteo_roommate.values())
            with col1:
                balance_tareas = (max(tareas_values) - min(tareas_values)) if tareas_values else 0
                st.metric("Diferencia Max Tareas", f"{balance_tareas}")
            
            tiempo_values = list(tiempo_roommate.values())
            with col2:
                balance_tiempo = (max(tiempo_values) - min(tiempo_values)) if tiempo_values else 0
                st.metric("Diferencia Max Tiempo", f"{balance_tiempo}min")
            
            with col3:
                diversidad_promedio = np.mean([len(cats) for cats in experiencia_categoria.values()]) if experiencia_categoria else 0
                st.metric("Diversidad Promedio", f"{diversidad_promedio:.1f}/6")