import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple
from collections import defaultdict

class DetectorConflictos:
    
    def __init__(self, cronograma, roommates, tareas):
        self.cronograma = cronograma
        self.roommates = roommates
        self.tareas = tareas
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    def detectar_conflictos_horarios(self) -> Dict:
        """Detecta todos los conflictos de horarios en el cronograma"""
        conflictos = defaultdict(list)
        
        # Crear mapa de ocupación: (semana, dia, intervalo_30min) -> [asignaciones]
        ocupacion_map = defaultdict(list)
        
        for key, asig in self.cronograma.items():
            semana = asig['semana']
            dia = asig['dia']
            hora_inicio = asig['hora']
            duracion_horas = asig['duracion'] / 60
            
            # Calcular todos los intervalos de 30 min que ocupa esta tarea
            intervalos_ocupados = self._calcular_intervalos_ocupados(hora_inicio, duracion_horas)
            
            for intervalo in intervalos_ocupados:
                slot_key = (semana, dia, intervalo)
                ocupacion_map[slot_key].append({
                    'key': key,
                    'asignacion': asig,
                    'intervalo': intervalo
                })
        
        # Identificar conflictos (slots con múltiples asignaciones)
        for slot_key, asignaciones in ocupacion_map.items():
            if len(asignaciones) > 1:
                semana, dia, intervalo = slot_key
                conflictos[slot_key] = {
                    'semana': semana,
                    'dia': dia,
                    'intervalo': intervalo,
                    'hora_str': self._intervalo_a_hora_str(intervalo),
                    'asignaciones': asignaciones,
                    'num_conflictos': len(asignaciones),
                    'roommates_involucrados': [asig['asignacion']['roommate'] for asig in asignaciones],
                    'tareas_involucradas': [asig['asignacion']['tarea'] for asig in asignaciones]
                }
        
        return dict(conflictos)
    
    def _calcular_intervalos_ocupados(self, hora_inicio: float, duracion_horas: float) -> List[float]:
        """Calcula todos los intervalos de 30 min ocupados por una tarea"""
        intervalos = []
        hora_actual = hora_inicio
        hora_fin = hora_inicio + duracion_horas
        
        while hora_actual < hora_fin:
            intervalos.append(hora_actual)
            hora_actual += 0.5
        
        return intervalos
    
    def _intervalo_a_hora_str(self, intervalo: float) -> str:
        """Convierte intervalo decimal a string de hora"""
        hora = int(intervalo)
        minutos = int((intervalo % 1) * 60)
        return f"{hora:02d}:{minutos:02d}"
    
    def analizar_tipos_conflictos(self, conflictos: Dict) -> Dict:
        """Analiza los tipos de conflictos encontrados"""
        tipos_conflictos = {
            'total_conflictos': len(conflictos),
            'conflictos_por_semana': defaultdict(int),
            'conflictos_por_dia': defaultdict(int),
            'conflictos_por_hora': defaultdict(int),
            'roommates_mas_conflictivos': defaultdict(int),
            'categorias_en_conflicto': defaultdict(int),
            'conflictos_criticos': []  # 3+ tareas al mismo tiempo
        }
        
        for conflict_key, conflict_data in conflictos.items():
            semana = conflict_data['semana']
            dia = conflict_data['dia']
            hora_str = conflict_data['hora_str']
            num_conflictos = conflict_data['num_conflictos']
            
            tipos_conflictos['conflictos_por_semana'][f'S{semana}'] += 1
            tipos_conflictos['conflictos_por_dia'][dia] += 1
            tipos_conflictos['conflictos_por_hora'][hora_str] += 1
            
            # Contar roommates involucrados
            for roommate in conflict_data['roommates_involucrados']:
                tipos_conflictos['roommates_mas_conflictivos'][roommate] += 1
            
            # Contar categorías en conflicto
            for asig in conflict_data['asignaciones']:
                tarea_nombre = asig['asignacion']['tarea']
                categoria = self._get_categoria_tarea(tarea_nombre)
                tipos_conflictos['categorias_en_conflicto'][categoria] += 1
            
            # Conflictos críticos (3+ tareas)
            if num_conflictos >= 3:
                tipos_conflictos['conflictos_criticos'].append(conflict_data)
        
        return tipos_conflictos
    
    def _get_categoria_tarea(self, nombre_tarea: str) -> str:
        """Obtiene la categoría de una tarea"""
        tarea = next((t for t in self.tareas if t.nombre == nombre_tarea), None)
        return tarea.categoria if tarea else 'Desconocida'
    
    def mostrar_resumen_conflictos(self):
        """Muestra resumen de conflictos en Streamlit"""
        conflictos = self.detectar_conflictos_horarios()
        tipos = self.analizar_tipos_conflictos(conflictos)
        
        st.subheader("⚠️ Análisis de Conflictos de Horarios")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Conflictos", tipos['total_conflictos'])
        
        with col2:
            if tipos['total_conflictos'] > 0:
                promedio_por_semana = tipos['total_conflictos'] / 4
                st.metric("Promedio/Semana", f"{promedio_por_semana:.1f}")
            else:
                st.metric("Promedio/Semana", "0")
        
        with col3:
            st.metric("Conflictos Críticos", len(tipos['conflictos_criticos']))
        
        with col4:
            if conflictos:
                max_conflicto = max(c['num_conflictos'] for c in conflictos.values())
                st.metric("Máx. Tareas Simultáneas", max_conflicto)
            else:
                st.metric("Máx. Tareas Simultáneas", "0")
        
        # Mostrar detalles si hay conflictos
        if tipos['total_conflictos'] > 0:
            # Estado general
            if tipos['total_conflictos'] > 10:
                st.error(f"🚨 **CRÍTICO**: {tipos['total_conflictos']} conflictos detectados. Requiere optimización urgente.")
            elif tipos['total_conflictos'] > 5:
                st.warning(f"⚠️ **MODERADO**: {tipos['total_conflictos']} conflictos detectados. Revisar asignaciones.")
            else:
                st.info(f"💡 **LEVE**: {tipos['total_conflictos']} conflictos menores detectados.")
            
            # Análisis detallado
            with st.expander("📊 Análisis Detallado de Conflictos", expanded=True):
                self._mostrar_graficos_conflictos(tipos)
                self._mostrar_tabla_conflictos(conflictos)
        
        else:
            st.success("✅ **PERFECTO**: No se detectaron conflictos de horarios en el cronograma.")
        
        return conflictos, tipos
    
    def _mostrar_graficos_conflictos(self, tipos: Dict):
        """Muestra gráficos de análisis de conflictos"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de conflictos por semana
            if tipos['conflictos_por_semana']:
                semanas = list(tipos['conflictos_por_semana'].keys())
                valores = list(tipos['conflictos_por_semana'].values())
                
                fig_semanas = px.bar(
                    x=semanas, y=valores,
                    title="Conflictos por Semana",
                    labels={'x': 'Semana', 'y': 'Número de Conflictos'},
                    color=valores,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_semanas, use_container_width=True)
        
        with col2:
            # Gráfico de roommates más conflictivos
            if tipos['roommates_mas_conflictivos']:
                roommates = list(tipos['roommates_mas_conflictivos'].keys())
                conflictos_rm = list(tipos['roommates_mas_conflictivos'].values())
                
                fig_roommates = px.bar(
                    x=roommates, y=conflictos_rm,
                    title="Roommates con Más Conflictos",
                    labels={'x': 'Roommate', 'y': 'Conflictos Involucrados'},
                    color=conflictos_rm,
                    color_continuous_scale='Oranges'
                )
                fig_roommates.update_xaxes(tickangle=45)
                st.plotly_chart(fig_roommates, use_container_width=True)
        
        # Heatmap de conflictos por día y hora
        if tipos['conflictos_por_dia'] and tipos['conflictos_por_hora']:
            st.write("### 🔥 Mapa de Calor de Conflictos")
            self._crear_heatmap_conflictos(tipos)
    
    def _crear_heatmap_conflictos(self, tipos: Dict):
        """Crea heatmap de conflictos por día y hora"""
        # Crear matriz de conflictos
        dias = self.dias_semana
        horas = [f"{h:02d}:00" for h in range(6, 24)] + [f"{h:02d}:30" for h in range(6, 24)]
        horas = sorted(horas)
        
        # Inicializar matriz
        matriz_conflictos = []
        for hora in horas:
            fila = []
            for dia in dias:
                # Contar conflictos en este slot
                count = 0
                for conflict_data in st.session_state.get('conflictos_detectados', {}).values():
                    if conflict_data['dia'] == dia and conflict_data['hora_str'] == hora:
                        count = conflict_data['num_conflictos']
                        break
                fila.append(count)
            matriz_conflictos.append(fila)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=matriz_conflictos,
            x=dias,
            y=horas,
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Conflictos"),
            hoverongaps=False,
            hovertemplate="<b>%{x}</b><br>%{y}<br>Conflictos: %{z}<extra></extra>"
        ))
        
        fig_heatmap.update_layout(
            title="Mapa de Calor: Conflictos por Día y Hora",
            xaxis_title="Días",
            yaxis_title="Horarios",
            height=400
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    def _mostrar_tabla_conflictos(self, conflictos: Dict):
        """Muestra tabla detallada de conflictos"""
        st.write("### 📋 Lista Detallada de Conflictos")
        
        # Preparar datos para la tabla
        datos_conflictos = []
        for conflict_key, conflict_data in conflictos.items():
            roommates_str = " vs ".join(conflict_data['roommates_involucrados'])
            tareas_str = " | ".join(conflict_data['tareas_involucradas'])
            
            datos_conflictos.append({
                'Semana': f"S{conflict_data['semana']}",
                'Día': conflict_data['dia'],
                'Hora': conflict_data['hora_str'],
                'Conflictos': conflict_data['num_conflictos'],
                'Roommates': roommates_str,
                'Tareas': tareas_str,
                'Severidad': self._calcular_severidad(conflict_data['num_conflictos'])
            })
        
        df_conflictos = pd.DataFrame(datos_conflictos)
        df_conflictos = df_conflictos.sort_values(['Severidad', 'Semana', 'Día', 'Hora'], ascending=[False, True, True, True])
        
        # Aplicar colores según severidad
        def color_severidad(val):
            if val == 'CRÍTICO':
                return 'background-color: #ffebee; color: #c62828'
            elif val == 'ALTO':
                return 'background-color: #fff3e0; color: #ef6c00'
            elif val == 'MEDIO':
                return 'background-color: #fffde7; color: #f57f17'
            else:
                return 'background-color: #f3e5f5; color: #7b1fa2'
        
        styled_df = df_conflictos.style.applymap(color_severidad, subset=['Severidad'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    def _calcular_severidad(self, num_conflictos: int) -> str:
        """Calcula la severidad del conflicto"""
        if num_conflictos >= 4:
            return 'CRÍTICO'
        elif num_conflictos == 3:
            return 'ALTO'
        elif num_conflictos == 2:
            return 'MEDIO'
        else:
            return 'BAJO'