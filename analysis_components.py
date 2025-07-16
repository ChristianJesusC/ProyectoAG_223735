import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class AnalysisComponents:
    
    def mostrar_analisis_completo(self):
        """Análisis completo del sistema"""
        st.subheader("⚖️ Distribución Equitativa")
        self.mostrar_analisis_equidad()
        
        st.divider()
        
        st.subheader("🎯 Análisis de Compatibilidad")
        self.mostrar_analisis_compatibilidad()
        
        st.divider()
        
        st.subheader("🏠 Análisis por Área del Hogar")
        self.mostrar_analisis_espacio()
    
    def mostrar_analisis_equidad(self):
        """Análisis detallado de equidad"""
        cronograma = st.session_state.cronograma
        
        carga_roommate = {}
        tareas_roommate = {}
        dificultad_roommate = {}
        
        for asig in cronograma.values():
            rm = asig['roommate']
            
            if rm not in carga_roommate:
                carga_roommate[rm] = 0
                tareas_roommate[rm] = 0
                dificultad_roommate[rm] = []
            
            carga_roommate[rm] += asig['duracion']
            tareas_roommate[rm] += 1
            
            tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
            if tarea_obj:
                dificultad_roommate[rm].append(tarea_obj.dificultad)
        
        data_equidad = []
        for rm in st.session_state.roommates:
            nombre = rm.nombre
            tiempo_asignado = carga_roommate.get(nombre, 0)
            num_tareas = tareas_roommate.get(nombre, 0)
            tiempo_objetivo = rm.tiempo_total_disponible * 60
            
            dificultad_promedio = np.mean(dificultad_roommate.get(nombre, [5])) if dificultad_roommate.get(nombre) else 5
            cumplimiento = (tiempo_asignado / tiempo_objetivo * 100) if tiempo_objetivo > 0 else 0
            
            data_equidad.append({
                'Roommate': nombre,
                'Tiempo Asignado': f"{tiempo_asignado}min ({tiempo_asignado//60}h {tiempo_asignado%60}min)",
                'Tiempo Objetivo': f"{tiempo_objetivo}min ({tiempo_objetivo//60}h {tiempo_objetivo%60}min)",
                'Cumplimiento': f"{cumplimiento:.1f}%",
                'Número Tareas': num_tareas,
                'Dificultad Promedio': f"{dificultad_promedio:.1f}/10",
                'Carga/Hora': f"{tiempo_asignado/(rm.total_horas_disponibles() or 1):.1f}min/h disponible"
            })
        
        df_equidad = pd.DataFrame(data_equidad)
        st.dataframe(df_equidad, use_container_width=True)
        
        tiempos = list(carga_roommate.values())
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            promedio = np.mean(tiempos) if tiempos else 0
            st.metric("Tiempo Promedio", f"{promedio:.0f}min")
        
        with col2:
            desviacion = np.std(tiempos) if tiempos else 0
            st.metric("Desviación Estándar", f"{desviacion:.0f}min")
        
        with col3:
            equidad = max(0, 100 - (desviacion/promedio*100)) if promedio > 0 else 100
            st.metric("Índice de Equidad", f"{equidad:.1f}%")
        
        with col4:
            diferencia_max = (max(tiempos) - min(tiempos)) if tiempos else 0
            st.metric("Diferencia Máxima", f"{diferencia_max:.0f}min")
    
    def mostrar_analisis_compatibilidad(self):
        """Análisis de compatibilidad con habilidades y preferencias"""
        cronograma = st.session_state.cronograma
        
        compatibilidad_habilidades = []
        compatibilidad_preferencias = []
        compatibilidad_horarios = []
        
        roommates_dict = {rm.nombre: rm for rm in st.session_state.roommates}
        tareas_dict = {t.nombre: t for t in st.session_state.tareas}
        
        for asig in cronograma.values():
            roommate_obj = roommates_dict.get(asig['roommate'])
            tarea_obj = tareas_dict.get(asig['tarea'])
            
            if roommate_obj and tarea_obj:
                habilidad = roommate_obj.get_habilidad(tarea_obj.categoria)
                compatibilidad_habilidades.append(habilidad / 10.0)
                
                preferencia = roommate_obj.get_preferencia(tarea_obj.categoria)
                if preferencia == 'prefiere':
                    compatibilidad_preferencias.append(1.0)
                elif preferencia == 'neutro':
                    compatibilidad_preferencias.append(0.5)
                else:
                    compatibilidad_preferencias.append(0.0)
                
                disponible = roommate_obj.esta_disponible(asig['dia'], asig['hora'])
                compatibilidad_horarios.append(1.0 if disponible else 0.0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            compatibilidad_por_roommate = {}
            
            for asig in cronograma.values():
                rm = asig['roommate']
                if rm not in compatibilidad_por_roommate:
                    compatibilidad_por_roommate[rm] = {'habilidades': [], 'preferencias': [], 'horarios': []}
                
                roommate_obj = roommates_dict.get(rm)
                tarea_obj = tareas_dict.get(asig['tarea'])
                
                if roommate_obj and tarea_obj:
                    habilidad = roommate_obj.get_habilidad(tarea_obj.categoria) / 10.0
                    compatibilidad_por_roommate[rm]['habilidades'].append(habilidad)
                    
                    preferencia = roommate_obj.get_preferencia(tarea_obj.categoria)
                    pref_score = {'prefiere': 1.0, 'neutro': 0.5, 'evita': 0.0}[preferencia]
                    compatibilidad_por_roommate[rm]['preferencias'].append(pref_score)
                    
                    disponible = roommate_obj.esta_disponible(asig['dia'], asig['hora'])
                    compatibilidad_por_roommate[rm]['horarios'].append(1.0 if disponible else 0.0)
            
            roommates_nombres = list(compatibilidad_por_roommate.keys())
            habilidades_promedio = [np.mean(compatibilidad_por_roommate[rm]['habilidades']) * 100 
                                   for rm in roommates_nombres]
            preferencias_promedio = [np.mean(compatibilidad_por_roommate[rm]['preferencias']) * 100 
                                    for rm in roommates_nombres]
            horarios_promedio = [np.mean(compatibilidad_por_roommate[rm]['horarios']) * 100 
                                for rm in roommates_nombres]
            
            fig_compatibilidad = go.Figure()
            
            fig_compatibilidad.add_trace(go.Scatterpolar(
                r=habilidades_promedio,
                theta=roommates_nombres,
                fill='toself',
                name='Habilidades',
                line_color='blue'
            ))
            
            fig_compatibilidad.add_trace(go.Scatterpolar(
                r=preferencias_promedio,
                theta=roommates_nombres,
                fill='toself',
                name='Preferencias',
                line_color='green'
            ))
            
            fig_compatibilidad.add_trace(go.Scatterpolar(
                r=horarios_promedio,
                theta=roommates_nombres,
                fill='toself',
                name='Horarios',
                line_color='red'
            ))
            
            fig_compatibilidad.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title="Compatibilidad por Roommate (%)",
                showlegend=True
            )
            
            st.plotly_chart(fig_compatibilidad, use_container_width=True)
        
        with col2:
            st.write("### Métricas Globales")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                habilidades_avg = np.mean(compatibilidad_habilidades) * 100 if compatibilidad_habilidades else 0
                st.metric("Habilidades", f"{habilidades_avg:.1f}%")
            
            with col_b:
                preferencias_avg = np.mean(compatibilidad_preferencias) * 100 if compatibilidad_preferencias else 0
                st.metric("Preferencias", f"{preferencias_avg:.1f}%")
            
            with col_c:
                horarios_avg = np.mean(compatibilidad_horarios) * 100 if compatibilidad_horarios else 0
                st.metric("Horarios", f"{horarios_avg:.1f}%")
            
            st.write("### Distribución de Compatibilidad")
            
            scores_data = []
            for i, asig in enumerate(cronograma.values()):
                roommate_obj = roommates_dict.get(asig['roommate'])
                tarea_obj = tareas_dict.get(asig['tarea'])
                
                if roommate_obj and tarea_obj:
                    habilidad_score = roommate_obj.get_habilidad(tarea_obj.categoria)
                    scores_data.append({
                        'Asignación': f"Asig {i+1}",
                        'Habilidad': habilidad_score,
                        'Tarea': asig['tarea'],
                        'Roommate': asig['roommate']
                    })
            
            if scores_data:
                df_scores = pd.DataFrame(scores_data)
                fig_hist = px.histogram(
                    df_scores,
                    x='Habilidad',
                    nbins=10,
                    title="Distribución de Niveles de Habilidad",
                    labels={'Habilidad': 'Nivel de Habilidad (1-10)', 'count': 'Número de Asignaciones'}
                )
                st.plotly_chart(fig_hist, use_container_width=True)
    
    def mostrar_analisis_espacio(self):
        """Análisis por área del hogar"""
        cronograma = st.session_state.cronograma
        espacio = st.session_state.espacio_hogar
        
        tareas_por_area = {}
        tiempo_por_area = {}
        
        for asig in cronograma.values():
            tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
            if tarea_obj:
                area = getattr(tarea_obj, 'area_espacio', 'General')
                
                if area not in tareas_por_area:
                    tareas_por_area[area] = []
                    tiempo_por_area[area] = 0
                
                tareas_por_area[area].append(asig)
                tiempo_por_area[area] += asig['duracion']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if tiempo_por_area:
                fig_areas = px.pie(
                    values=list(tiempo_por_area.values()),
                    names=list(tiempo_por_area.keys()),
                    title="Distribución de Tiempo por Área del Hogar"
                )
                st.plotly_chart(fig_areas, use_container_width=True)
        
        with col2:
            st.write("### Estadísticas por Área")
            
            area_stats = []
            for area, tiempo in tiempo_por_area.items():
                num_tareas = len(tareas_por_area[area])
                roommates_involucrados = len(set(asig['roommate'] for asig in tareas_por_area[area]))
                
                area_stats.append({
                    'Área': area,
                    'Tiempo Total': f"{tiempo}min",
                    'Número Tareas': num_tareas,
                    'Roommates': roommates_involucrados,
                    'Tiempo/Tarea': f"{tiempo//num_tareas if num_tareas > 0 else 0}min"
                })
            
            df_areas = pd.DataFrame(area_stats)
            st.dataframe(df_areas, use_container_width=True)
        
        st.write("### 💡 Recomendaciones")
        
        factor_complejidad = espacio.get_factor_complejidad()
        
        if factor_complejidad > 1.5:
            st.info("🏠 **Espacio complejo**: Considera dividir tareas grandes")
        
        if tiempo_por_area:
            area_max_tiempo = max(tiempo_por_area, key=tiempo_por_area.get)
            tiempo_max = tiempo_por_area[area_max_tiempo]
            
            if tiempo_max > sum(tiempo_por_area.values()) * 0.4:
                st.warning(f"⚠️ **{area_max_tiempo}** requiere {tiempo_max}min ({tiempo_max/sum(tiempo_por_area.values())*100:.1f}% del tiempo total)")