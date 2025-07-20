import streamlit as st
from datetime import date, timedelta
from typing import List, Dict
from enhanced_models import Ausencia, RoommateEnhanced
import pandas as pd

class ManagerAusencias:
    
    def __init__(self, roommates: List[RoommateEnhanced]):
        self.roommates = roommates
    
    def mostrar_gestion_ausencias(self):
        """Interfaz completa para gestión de ausencias"""
        st.subheader("🏖️ Gestión de Ausencias")
        
        tab1, tab2, tab3 = st.tabs(["➕ Nueva Ausencia", "📋 Ausencias Activas", "📊 Análisis de Impacto"])
        
        with tab1:
            self._formulario_nueva_ausencia()
        
        with tab2:
            self._mostrar_ausencias_activas()
        
        with tab3:
            self._analizar_impacto_ausencias()
    
    def _formulario_nueva_ausencia(self):
        """Formulario para agregar nueva ausencia"""
        st.write("### Registrar Nueva Ausencia")
        
        if not self.roommates:
            st.warning("No hay roommates registrados")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            roommate_sel = st.selectbox(
                "Roommate:", 
                [rm.nombre for rm in self.roommates]
            )
            
            tipo_ausencia = st.selectbox(
                "Tipo de ausencia:",
                ["vacaciones", "enfermedad", "trabajo", "emergencia", "familia", "estudios"]
            )
            
            es_parcial = st.checkbox(
                "Ausencia parcial (solo algunas horas del día)",
                help="Marcar si la persona estará disponible parte del día"
            )
        
        with col2:
            fecha_inicio = st.date_input(
                "Fecha inicio:",
                value=date.today(),
                min_value=date.today()
            )
            
            fecha_fin = st.date_input(
                "Fecha fin:",
                value=date.today() + timedelta(days=7),
                min_value=fecha_inicio
            )
            
            motivo = st.text_area(
                "Motivo detallado:",
                placeholder="Ej: Vacaciones familiares en la playa"
            )
        
        # Horarios disponibles si es ausencia parcial
        if es_parcial:
            st.write("**Horarios disponibles durante la ausencia:**")
            horarios_limitados = self._configurar_horarios_parciales()
        else:
            horarios_limitados = {}
        
        if st.button("✅ Registrar Ausencia", type="primary"):
            if self._registrar_ausencia(roommate_sel, fecha_inicio, fecha_fin, 
                                      motivo, tipo_ausencia, es_parcial, horarios_limitados):
                st.success(f"Ausencia registrada para {roommate_sel}")
                st.rerun()
    
    def _configurar_horarios_parciales(self) -> Dict:
        """Configurar horarios disponibles durante ausencia parcial"""
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        horarios = {}
        
        st.info("💡 Configura las horas en que estará disponible durante la ausencia")
        
        for dia in dias_semana:
            with st.expander(f"📅 {dia}"):
                disponible = st.checkbox(f"Disponible el {dia}", key=f"disp_{dia}")
                
                if disponible:
                    col1, col2 = st.columns(2)
                    with col1:
                        hora_inicio = st.time_input(f"Hora inicio {dia}", key=f"ini_{dia}")
                    with col2:
                        hora_fin = st.time_input(f"Hora fin {dia}", key=f"fin_{dia}")
                    
                    if hora_inicio < hora_fin:
                        inicio_decimal = hora_inicio.hour + hora_inicio.minute / 60
                        fin_decimal = hora_fin.hour + hora_fin.minute / 60
                        
                        from models import RangoTiempo
                        horarios[dia] = [RangoTiempo(inicio_decimal, fin_decimal)]
        
        return horarios
    
    def _registrar_ausencia(self, roommate_nombre: str, fecha_inicio: date, 
                          fecha_fin: date, motivo: str, tipo: str, 
                          es_parcial: bool, horarios_limitados: Dict) -> bool:
        """Registra nueva ausencia"""
        try:
            roommate = next(rm for rm in self.roommates if rm.nombre == roommate_nombre)
            
            ausencia = Ausencia(
                roommate=roommate_nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                motivo=motivo,
                tipo=tipo,
                es_parcial=es_parcial,
                horas_disponibles=horarios_limitados
            )
            
            roommate.ausencias.append(ausencia)
            return True
            
        except Exception as e:
            st.error(f"Error al registrar ausencia: {e}")
            return False
    
    def _mostrar_ausencias_activas(self):
        """Muestra ausencias activas y próximas"""
        st.write("### Ausencias Registradas")
        
        todas_ausencias = []
        for roommate in self.roommates:
            for ausencia in roommate.ausencias:
                todas_ausencias.append({
                    'Roommate': roommate.nombre,
                    'Tipo': ausencia.tipo.title(),
                    'Inicio': ausencia.fecha_inicio.strftime("%d/%m/%Y"),
                    'Fin': ausencia.fecha_fin.strftime("%d/%m/%Y"),
                    'Días': (ausencia.fecha_fin - ausencia.fecha_inicio).days + 1,
                    'Motivo': ausencia.motivo,
                    'Parcial': "✅" if ausencia.es_parcial else "❌",
                    'Estado': self._calcular_estado_ausencia(ausencia)
                })
        
        if todas_ausencias:
            df_ausencias = pd.DataFrame(todas_ausencias)
            
            # Filtros
            col1, col2, col3 = st.columns(3)
            with col1:
                filtro_estado = st.selectbox("Filtrar por estado:", 
                                           ["Todos", "Activa", "Próxima", "Pasada"])
            with col2:
                filtro_tipo = st.selectbox("Filtrar por tipo:", 
                                         ["Todos"] + list(df_ausencias['Tipo'].unique()))
            with col3:
                filtro_roommate = st.selectbox("Filtrar por roommate:", 
                                             ["Todos"] + list(df_ausencias['Roommate'].unique()))
            
            # Aplicar filtros
            df_filtrado = df_ausencias.copy()
            if filtro_estado != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]
            if filtro_tipo != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Tipo'] == filtro_tipo]
            if filtro_roommate != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Roommate'] == filtro_roommate]
            
            # Colorear filas según estado
            def colorear_fila(val):
                if val == 'Activa':
                    return 'background-color: #ffebee'
                elif val == 'Próxima':
                    return 'background-color: #fff3e0'
                else:
                    return 'background-color: #f5f5f5'
            
            styled_df = df_filtrado.style.applymap(colorear_fila, subset=['Estado'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            # Botón para eliminar ausencias
            if len(df_filtrado) > 0:
                ausencia_eliminar = st.selectbox(
                    "Eliminar ausencia:",
                    range(len(df_filtrado)),
                    format_func=lambda x: f"{df_filtrado.iloc[x]['Roommate']} - {df_filtrado.iloc[x]['Inicio']} a {df_filtrado.iloc[x]['Fin']}"
                )
                
                if st.button("🗑️ Eliminar Ausencia Seleccionada"):
                    self._eliminar_ausencia(ausencia_eliminar, df_filtrado)
        else:
            st.info("No hay ausencias registradas")
    
    def _calcular_estado_ausencia(self, ausencia: Ausencia) -> str:
        """Calcula el estado actual de una ausencia"""
        hoy = date.today()
        
        if ausencia.fecha_inicio <= hoy <= ausencia.fecha_fin:
            return "Activa"
        elif hoy < ausencia.fecha_inicio:
            return "Próxima"
        else:
            return "Pasada"
    
    def _analizar_impacto_ausencias(self):
        """Analiza el impacto de las ausencias en el cronograma"""
        st.write("### 📊 Análisis de Impacto")
        
        # Calendario de ausencias
        st.write("#### Calendario de Ausencias (Próximos 30 días)")
        self._mostrar_calendario_ausencias()
        
        # Estadísticas
        st.write("#### Estadísticas de Ausencias")
        self._mostrar_estadisticas_ausencias()
        
        # Recomendaciones
        st.write("#### 💡 Recomendaciones")
        self._mostrar_recomendaciones_ausencias()
    
    def _mostrar_calendario_ausencias(self):
        """Muestra calendario visual de ausencias"""
        import plotly.graph_objects as go
        
        # Generar datos para próximos 30 días
        fechas = [date.today() + timedelta(days=i) for i in range(30)]
        
        # Crear matriz de ausencias
        matriz_ausencias = []
        for roommate in self.roommates:
            fila_roommate = []
            for fecha in fechas:
                ausente = any(ausencia.esta_ausente(fecha) for ausencia in roommate.ausencias)
                fila_roommate.append(1 if ausente else 0)
            matriz_ausencias.append(fila_roommate)
        
        fig = go.Figure(data=go.Heatmap(
            z=matriz_ausencias,
            x=[f.strftime("%d/%m") for f in fechas],
            y=[rm.nombre for rm in self.roommates],
            colorscale=[[0, 'lightgreen'], [1, 'lightcoral']],
            showscale=True,
            colorbar=dict(
                title="Estado",
                tickvals=[0, 1],
                ticktext=["Disponible", "Ausente"]
            )
        ))
        
        fig.update_layout(
            title="Calendario de Ausencias - Próximos 30 días",
            xaxis_title="Fechas",
            yaxis_title="Roommates",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _mostrar_estadisticas_ausencias(self):
        """Muestra estadísticas de ausencias"""
        col1, col2, col3, col4 = st.columns(4)
        
        ausencias_activas = 0
        ausencias_proximas = 0
        total_dias_ausencia = 0
        
        for roommate in self.roommates:
            for ausencia in roommate.ausencias:
                estado = self._calcular_estado_ausencia(ausencia)
                if estado == "Activa":
                    ausencias_activas += 1
                elif estado == "Próxima":
                    ausencias_proximas += 1
                
                total_dias_ausencia += (ausencia.fecha_fin - ausencia.fecha_inicio).days + 1
        
        with col1:
            st.metric("Ausencias Activas", ausencias_activas)
        with col2:
            st.metric("Ausencias Próximas", ausencias_proximas)
        with col3:
            st.metric("Total Días de Ausencia", total_dias_ausencia)
        with col4:
            promedio_dias = total_dias_ausencia / len(self.roommates) if self.roommates else 0
            st.metric("Promedio Días/Roommate", f"{promedio_dias:.1f}")
    
    def _mostrar_recomendaciones_ausencias(self):
        """Muestra recomendaciones basadas en ausencias"""
        recomendaciones = []
        
        # Verificar solapamientos
        for i, rm1 in enumerate(self.roommates):
            for j, rm2 in enumerate(self.roommates[i+1:], i+1):
                for aus1 in rm1.ausencias:
                    for aus2 in rm2.ausencias:
                        if self._ausencias_se_solapan(aus1, aus2):
                            recomendaciones.append(
                                f"⚠️ **Solapamiento**: {rm1.nombre} y {rm2.nombre} ausentes {aus1.fecha_inicio} - {aus2.fecha_fin}"
                            )
        
        # Verificar períodos críticos
        for fecha in [date.today() + timedelta(days=i) for i in range(30)]:
            ausentes = sum(1 for rm in self.roommates 
                          if any(aus.esta_ausente(fecha) for aus in rm.ausencias))
            if ausentes >= len(self.roommates) * 0.6:  # Más del 60% ausente
                recomendaciones.append(
                    f"🚨 **Período crítico**: {fecha.strftime('%d/%m/%Y')} - {ausentes}/{len(self.roommates)} roommates ausentes"
                )
        
        if recomendaciones:
            for rec in recomendaciones:
                st.warning(rec)
        else:
            st.success("✅ No se detectaron problemas críticos con las ausencias")
    
    def _ausencias_se_solapan(self, aus1: Ausencia, aus2: Ausencia) -> bool:
        """Verifica si dos ausencias se solapan"""
        return not (aus1.fecha_fin < aus2.fecha_inicio or aus2.fecha_fin < aus1.fecha_inicio)
    
    def get_roommates_disponibles(self, fecha: date, hora: float = None) -> List[str]:
        """Obtiene lista de roommates disponibles en fecha/hora específica"""
        disponibles = []
        
        for roommate in self.roommates:
            ausente = any(ausencia.esta_ausente(fecha, hora) for ausencia in roommate.ausencias)
            if not ausente:
                disponibles.append(roommate.nombre)
        
        return disponibles