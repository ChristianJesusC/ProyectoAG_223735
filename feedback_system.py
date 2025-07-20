import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import numpy as np

@dataclass
class RegistroTarea:
    """Registro de ejecución de una tarea"""
    roommate: str
    tarea: str
    fecha_programada: date
    fecha_ejecutada: Optional[date]
    tiempo_programado: int  # minutos
    tiempo_real: Optional[int]  # minutos reales
    calidad: Optional[int]  # 1-10
    dificultad_percibida: Optional[int]  # 1-10
    comentarios: str = ""
    completada: bool = False
    requirio_ayuda: bool = False
    problemas_encontrados: List[str] = field(default_factory=list)

@dataclass
class FeedbackRoommate:
    """Feedback general de un roommate"""
    roommate: str
    fecha: date
    satisfaccion_general: int  # 1-10
    carga_percibida: int  # 1-10 (muy baja a muy alta)
    equidad_percibida: int  # 1-10
    sugerencias: str = ""
    tareas_preferidas: List[str] = field(default_factory=list)
    tareas_evitadas: List[str] = field(default_factory=list)

class SistemaFeedback:
    
    def __init__(self):
        self.registros_tareas = []
        self.feedback_roommates = []
        self.patrones_aprendidos = {}
    
    def mostrar_sistema_feedback(self):
        """Interfaz completa del sistema de feedback"""
        st.subheader("📝 Sistema de Feedback y Aprendizaje")
        st.markdown("*Registra experiencias para mejorar futuras asignaciones*")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "✅ Registrar Ejecución",
            "💭 Feedback General", 
            "📊 Análisis de Patrones",
            "🧠 Aprendizaje Automático"
        ])
        
        with tab1:
            self._registrar_ejecucion_tareas()
        
        with tab2:
            self._capturar_feedback_general()
        
        with tab3:
            self._analizar_patrones_ejecucion()
        
        with tab4:
            self._mostrar_aprendizaje_automatico()
    
    def _registrar_ejecucion_tareas(self):
        """Interfaz para registrar ejecución de tareas"""
        st.write("### ✅ Registrar Ejecución de Tareas")
        
        if not hasattr(st.session_state, 'cronograma') or not st.session_state.cronograma:
            st.warning("No hay cronograma disponible para registrar")
            return
        
        # Seleccionar tarea del cronograma
        tareas_disponibles = {}
        fecha_limite = date.today() + timedelta(days=7)  # Una semana hacia adelante
        
        for key, asignacion in st.session_state.cronograma.items():
            # Calcular fecha aproximada (semana 1 = esta semana, etc.)
            dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            dia_indice = dias_semana.index(asignacion['dia'])
            semana_offset = (asignacion['semana'] - 1) * 7
            fecha_estimada = date.today() + timedelta(days=dia_indice + semana_offset)
            
            if fecha_estimada <= fecha_limite:
                tareas_disponibles[key] = {
                    **asignacion,
                    'fecha_estimada': fecha_estimada,
                    'display': f"{asignacion['roommate']} - {asignacion['tarea']} ({fecha_estimada.strftime('%d/%m')} {asignacion['hora']:02.0f}:{int((asignacion['hora'] % 1) * 60):02d})"
                }
        
        if not tareas_disponibles:
            st.info("No hay tareas recientes para registrar")
            return
        
        # Selector de tarea
        tarea_key = st.selectbox(
            "Seleccionar tarea ejecutada:",
            list(tareas_disponibles.keys()),
            format_func=lambda x: tareas_disponibles[x]['display']
        )
        
        tarea_sel = tareas_disponibles[tarea_key]
        
        # Formulario de registro
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📋 Detalles de la Tarea**")
            st.write(f"**Roommate:** {tarea_sel['roommate']}")
            st.write(f"**Tarea:** {tarea_sel['tarea']}")
            st.write(f"**Programada:** {tarea_sel['fecha_estimada'].strftime('%d/%m/%Y')}")
            st.write(f"**Duración estimada:** {tarea_sel['duracion']} min")
            
            completada = st.checkbox("✅ Tarea completada")
            
            if completada:
                fecha_ejecutada = st.date_input(
                    "Fecha de ejecución:",
                    value=tarea_sel['fecha_estimada'],
                    max_value=date.today()
                )
                
                tiempo_real = st.number_input(
                    "Tiempo real (minutos):",
                    min_value=1,
                    max_value=480,
                    value=tarea_sel['duracion']
                )
        
        with col2:
            if completada:
                st.write("**⭐ Evaluación de la Experiencia**")
                
                calidad = st.slider(
                    "Calidad del trabajo (1-10):",
                    1, 10, 7,
                    help="¿Qué tan bien se completó la tarea?"
                )
                
                dificultad_percibida = st.slider(
                    "Dificultad percibida (1-10):",
                    1, 10, 5,
                    help="¿Qué tan difícil fue la tarea realmente?"
                )
                
                requirio_ayuda = st.checkbox("Requirió ayuda de otros")
                
                problemas = st.multiselect(
                    "Problemas encontrados:",
                    [
                        "Falta de tiempo",
                        "Falta de herramientas",
                        "Falta de conocimiento",
                        "Tarea más difícil de lo esperado",
                        "Interrupciones",
                        "Problemas de salud",
                        "Conflicto de horarios"
                    ]
                )
                
                comentarios = st.text_area(
                    "Comentarios adicionales:",
                    placeholder="Describe cualquier detalle importante sobre la ejecución..."
                )
        
        # Botón para guardar registro
        if st.button("💾 Guardar Registro", type="primary"):
            if completada:
                registro = RegistroTarea(
                    roommate=tarea_sel['roommate'],
                    tarea=tarea_sel['tarea'],
                    fecha_programada=tarea_sel['fecha_estimada'],
                    fecha_ejecutada=fecha_ejecutada,
                    tiempo_programado=tarea_sel['duracion'],
                    tiempo_real=tiempo_real,
                    calidad=calidad,
                    dificultad_percibida=dificultad_percibida,
                    comentarios=comentarios,
                    completada=True,
                    requirio_ayuda=requirio_ayuda,
                    problemas_encontrados=problemas
                )
            else:
                registro = RegistroTarea(
                    roommate=tarea_sel['roommate'],
                    tarea=tarea_sel['tarea'],
                    fecha_programada=tarea_sel['fecha_estimada'],
                    fecha_ejecutada=None,
                    tiempo_programado=tarea_sel['duracion'],
                    tiempo_real=None,
                    calidad=None,
                    dificultad_percibida=None,
                    comentarios=comentarios,
                    completada=False,
                    requirio_ayuda=False,
                    problemas_encontrados=[]
                )
            
            self.registros_tareas.append(registro)
            st.success("✅ Registro guardado exitosamente")
            
            # Actualizar patrones aprendidos
            self._actualizar_patrones_aprendidos(registro)
    
    def _capturar_feedback_general(self):
        """Captura feedback general de roommates"""
        st.write("### 💭 Feedback General de Roommates")
        
        if not hasattr(st.session_state, 'roommates') or not st.session_state.roommates:
            st.warning("No hay roommates registrados")
            return
        
        # Selector de roommate
        roommate_sel = st.selectbox(
            "Roommate que da feedback:",
            [rm.nombre for rm in st.session_state.roommates]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Evaluación General**")
            
            satisfaccion = st.slider(
                "Satisfacción general con el sistema (1-10):",
                1, 10, 7,
                help="¿Qué tan satisfecho estás con las asignaciones actuales?"
            )
            
            carga_percibida = st.slider(
                "Percepción de carga de trabajo (1-10):",
                1, 10, 5,
                help="1=Muy liviana, 5=Adecuada, 10=Muy pesada"
            )
            
            equidad_percibida = st.slider(
                "Percepción de equidad (1-10):",
                1, 10, 7,
                help="¿Te parece que la distribución es justa?"
            )
        
        with col2:
            st.write("**💡 Preferencias**")
            
            todas_las_tareas = list(set(t.nombre for t in st.session_state.tareas))
            
            tareas_preferidas = st.multiselect(
                "Tareas que prefieres hacer:",
                todas_las_tareas
            )
            
            tareas_evitadas = st.multiselect(
                "Tareas que prefieres evitar:",
                [t for t in todas_las_tareas if t not in tareas_preferidas]
            )
            
            sugerencias = st.text_area(
                "Sugerencias de mejora:",
                placeholder="¿Cómo podríamos mejorar el sistema de asignaciones?"
            )
        
        if st.button("📝 Enviar Feedback", type="primary"):
            feedback = FeedbackRoommate(
                roommate=roommate_sel,
                fecha=date.today(),
                satisfaccion_general=satisfaccion,
                carga_percibida=carga_percibida,
                equidad_percibida=equidad_percibida,
                sugerencias=sugerencias,
                tareas_preferidas=tareas_preferidas,
                tareas_evitadas=tareas_evitadas
            )
            
            self.feedback_roommates.append(feedback)
            st.success("✅ Feedback enviado exitosamente")
            
            # Mostrar recomendaciones inmediatas
            self._mostrar_recomendaciones_feedback(feedback)
    
    def _analizar_patrones_ejecucion(self):
        """Analiza patrones de ejecución de tareas"""
        st.write("### 📊 Análisis de Patrones de Ejecución")
        
        if not self.registros_tareas:
            st.info("No hay registros de ejecución para analizar")
            return
        
        # Convertir a DataFrame para análisis
        datos_registros = []
        for registro in self.registros_tareas:
            datos_registros.append({
                'Roommate': registro.roommate,
                'Tarea': registro.tarea,
                'Completada': registro.completada,
                'Tiempo_Programado': registro.tiempo_programado,
                'Tiempo_Real': registro.tiempo_real or 0,
                'Calidad': registro.calidad or 0,
                'Dificultad_Percibida': registro.dificultad_percibida or 0,
                'Requirio_Ayuda': registro.requirio_ayuda,
                'Num_Problemas': len(registro.problemas_encontrados),
                'Fecha': registro.fecha_ejecutada or registro.fecha_programada
            })
        
        df = pd.DataFrame(datos_registros)
        
        # Métricas generales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            tasa_completacion = (df['Completada'].sum() / len(df) * 100) if len(df) > 0 else 0
            st.metric("Tasa de Completación", f"{tasa_completacion:.1f}%")
        
        with col2:
            df_completadas = df[df['Completada'] == True]
            calidad_promedio = df_completadas['Calidad'].mean() if len(df_completadas) > 0 else 0
            st.metric("Calidad Promedio", f"{calidad_promedio:.1f}/10")
        
        with col3:
            if len(df_completadas) > 0:
                eficiencia = (df_completadas['Tiempo_Programado'].sum() / 
                            df_completadas['Tiempo_Real'].sum() * 100) if df_completadas['Tiempo_Real'].sum() > 0 else 0
                st.metric("Eficiencia Temporal", f"{eficiencia:.1f}%")
            else:
                st.metric("Eficiencia Temporal", "N/A")
        
        with col4:
            ayuda_requerida = (df['Requirio_Ayuda'].sum() / len(df) * 100) if len(df) > 0 else 0
            st.metric("% Requirió Ayuda", f"{ayuda_requerida:.1f}%")
        
        # Gráficos de análisis
        if len(df_completadas) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Calidad por roommate
                fig_calidad = px.box(
                    df_completadas, 
                    x='Roommate', 
                    y='Calidad',
                    title="Distribución de Calidad por Roommate"
                )
                st.plotly_chart(fig_calidad, use_container_width=True)
            
            with col2:
                # Eficiencia temporal por tarea
                df_completadas['Eficiencia'] = (df_completadas['Tiempo_Programado'] / 
                                              df_completadas['Tiempo_Real'] * 100)
                fig_eficiencia = px.bar(
                    df_completadas.groupby('Tarea')['Eficiencia'].mean().reset_index(),
                    x='Tarea',
                    y='Eficiencia',
                    title="Eficiencia Temporal por Tipo de Tarea"
                )
                fig_eficiencia.update_xaxes(tickangle=45)
                st.plotly_chart(fig_eficiencia, use_container_width=True)
        
        # Análisis de problemas
        st.write("#### 🚨 Análisis de Problemas Frecuentes")
        problemas_frecuentes = {}
        for registro in self.registros_tareas:
            for problema in registro.problemas_encontrados:
                problemas_frecuentes[problema] = problemas_frecuentes.get(problema, 0) + 1
        
        if problemas_frecuentes:
            df_problemas = pd.DataFrame(
                list(problemas_frecuentes.items()),
                columns=['Problema', 'Frecuencia']
            ).sort_values('Frecuencia', ascending=True)
            
            fig_problemas = px.bar(
                df_problemas,
                x='Frecuencia',
                y='Problema',
                orientation='h',
                title="Problemas Más Frecuentes"
            )
            st.plotly_chart(fig_problemas, use_container_width=True)
        else:
            st.info("No se han reportado problemas específicos")
    
    def _mostrar_aprendizaje_automatico(self):
        """Muestra sistema de aprendizaje automático"""
        st.write("### 🧠 Aprendizaje Automático del Sistema")
        
        if not self.patrones_aprendidos:
            st.info("El sistema aún no ha aprendido patrones suficientes")
            return
        
        # Mostrar patrones aprendidos
        st.write("#### 📈 Patrones Detectados")
        
        for roommate, patrones in self.patrones_aprendidos.items():
            with st.expander(f"👤 Patrones de {roommate}"):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**⏱️ Eficiencia Temporal**")
                    for tarea, datos in patrones.get('eficiencia_temporal', {}).items():
                        factor = datos.get('factor_tiempo', 1.0)
                        if factor < 0.8:
                            color = "🟢"  # Más rápido de lo esperado
                        elif factor > 1.2:
                            color = "🔴"  # Más lento de lo esperado
                        else:
                            color = "🟡"  # Tiempo esperado
                        
                        st.write(f"{color} **{tarea}:** {factor:.2f}x tiempo estimado")
                
                with col2:
                    st.write("**🎯 Calidad Promedio**")
                    for tarea, datos in patrones.get('calidad_promedio', {}).items():
                        calidad = datos.get('calidad', 0)
                        if calidad >= 8:
                            color = "🟢"
                        elif calidad >= 6:
                            color = "🟡"
                        else:
                            color = "🔴"
                        
                        st.write(f"{color} **{tarea}:** {calidad:.1f}/10")
        
        # Recomendaciones del sistema
        st.write("#### 💡 Recomendaciones del Sistema")
        recomendaciones = self._generar_recomendaciones_automaticas()
        
        for rec in recomendaciones:
            if rec['tipo'] == 'warning':
                st.warning(rec['mensaje'])
            elif rec['tipo'] == 'success':
                st.success(rec['mensaje'])
            else:
                st.info(rec['mensaje'])
    
    def _actualizar_patrones_aprendidos(self, registro: RegistroTarea):
        """Actualiza patrones aprendidos con nuevo registro"""
        roommate = registro.roommate
        tarea = registro.tarea
        
        if roommate not in self.patrones_aprendidos:
            self.patrones_aprendidos[roommate] = {
                'eficiencia_temporal': {},
                'calidad_promedio': {},
                'problemas_frecuentes': {},
                'total_registros': 0
            }
        
        patrones = self.patrones_aprendidos[roommate]
        patrones['total_registros'] += 1
        
        if registro.completada and registro.tiempo_real:
            # Actualizar eficiencia temporal
            if tarea not in patrones['eficiencia_temporal']:
                patrones['eficiencia_temporal'][tarea] = {
                    'factor_tiempo': 1.0,
                    'registros': 0
                }
            
            factor_actual = registro.tiempo_real / registro.tiempo_programado
            datos_tarea = patrones['eficiencia_temporal'][tarea]
            datos_tarea['registros'] += 1
            
            # Promedio ponderado
            peso_nuevo = 1 / datos_tarea['registros']
            datos_tarea['factor_tiempo'] = (
                datos_tarea['factor_tiempo'] * (1 - peso_nuevo) + 
                factor_actual * peso_nuevo
            )
            
            # Actualizar calidad promedio
            if registro.calidad:
                if tarea not in patrones['calidad_promedio']:
                    patrones['calidad_promedio'][tarea] = {
                        'calidad': 0,
                        'registros': 0
                    }
                
                datos_calidad = patrones['calidad_promedio'][tarea]
                datos_calidad['registros'] += 1
                peso_nuevo = 1 / datos_calidad['registros']
                datos_calidad['calidad'] = (
                    datos_calidad['calidad'] * (1 - peso_nuevo) +
                    registro.calidad * peso_nuevo
                )
        
        # Actualizar problemas frecuentes
        for problema in registro.problemas_encontrados:
            if problema not in patrones['problemas_frecuentes']:
                patrones['problemas_frecuentes'][problema] = 0
            patrones['problemas_frecuentes'][problema] += 1
    
    def _generar_recomendaciones_automaticas(self) -> List[Dict]:
        """Genera recomendaciones automáticas basadas en patrones"""
        recomendaciones = []
        
        for roommate, patrones in self.patrones_aprendidos.items():
            # Recomendar ajustes de tiempo
            for tarea, datos in patrones.get('eficiencia_temporal', {}).items():
                factor = datos['factor_tiempo']
                if factor > 1.3:  # Consistentemente lento
                    recomendaciones.append({
                        'tipo': 'warning',
                        'mensaje': f"⚠️ **{roommate}** necesita más tiempo para **{tarea}** (factor: {factor:.2f}x)"
                    })
                elif factor < 0.7:  # Consistentemente rápido
                    recomendaciones.append({
                        'tipo': 'success',
                        'mensaje': f"✅ **{roommate}** es muy eficiente en **{tarea}** (factor: {factor:.2f}x)"
                    })
            
            # Recomendar cambios por baja calidad
            for tarea, datos in patrones.get('calidad_promedio', {}).items():
                if datos['calidad'] < 6 and datos['registros'] >= 3:
                    recomendaciones.append({
                        'tipo': 'warning',
                        'mensaje': f"🔴 **{roommate}** tiene baja calidad en **{tarea}** (promedio: {datos['calidad']:.1f}/10)"
                    })
            
            # Alertar sobre problemas frecuentes
            for problema, frecuencia in patrones.get('problemas_frecuentes', {}).items():
                if frecuencia >= 3:
                    recomendaciones.append({
                        'tipo': 'warning',
                        'mensaje': f"🚨 **{roommate}** reporta frecuentemente: **{problema}** ({frecuencia} veces)"
                    })
        
        return recomendaciones
    
    def _mostrar_recomendaciones_feedback(self, feedback: FeedbackRoommate):
        """Muestra recomendaciones basadas en feedback inmediato"""
        st.write("#### 💡 Recomendaciones Basadas en tu Feedback")
        
        if feedback.satisfaccion_general < 6:
            st.warning("🔴 **Baja satisfacción detectada** - Revisaremos las asignaciones")
        
        if feedback.carga_percibida > 7:
            st.warning("⚠️ **Carga alta percibida** - Consideraremos redistribuir tareas")
        elif feedback.carga_percibida < 4:
            st.info("💡 **Carga baja detectada** - Podrías asumir más responsabilidades")
        
        if feedback.equidad_percibida < 6:
            st.error("🚨 **Problema de equidad** - Analizaremos la distribución actual")
        
        if feedback.tareas_evitadas:
            st.info(f"📝 **Tareas a evitar registradas:** {', '.join(feedback.tareas_evitadas)}")
        
        if feedback.tareas_preferidas:
            st.success(f"✅ **Preferencias registradas:** {', '.join(feedback.tareas_preferidas)}")
    
    def get_ajustes_sugeridos(self) -> Dict:
        """Obtiene ajustes sugeridos para el algoritmo genético"""
        ajustes = {
            'factores_tiempo': {},
            'penalizaciones_calidad': {},
            'bonificaciones_eficiencia': {}
        }
        
        for roommate, patrones in self.patrones_aprendidos.items():
            ajustes['factores_tiempo'][roommate] = {}
            
            for tarea, datos in patrones.get('eficiencia_temporal', {}).items():
                factor = datos['factor_tiempo']
                ajustes['factores_tiempo'][roommate][tarea] = factor
            
            # Penalizar asignaciones de baja calidad
            for tarea, datos in patrones.get('calidad_promedio', {}).items():
                if datos['calidad'] < 6:
                    if roommate not in ajustes['penalizaciones_calidad']:
                        ajustes['penalizaciones_calidad'][roommate] = {}
                    ajustes['penalizaciones_calidad'][roommate][tarea] = 0.5  # 50% penalización
        
        return ajustes