import streamlit as st
from datetime import date, datetime
from typing import List, Dict, Optional
import pandas as pd

class IntercambiadorTareas:
    
    def __init__(self, cronograma: Dict, roommates: List):
        self.cronograma = cronograma
        self.roommates = roommates
        self.intercambios_pendientes = []
        self.historial_intercambios = []
    
    def mostrar_sistema_intercambios(self):
        """Interfaz completa para intercambio de tareas"""
        st.subheader("🔄 Sistema de Intercambio de Tareas")
        st.markdown("*Permite a los roommates intercambiar tareas de manera flexible*")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Solicitar Intercambio", 
            "📋 Intercambios Pendientes", 
            "✅ Aprobar/Rechazar", 
            "📊 Historial"
        ])
        
        with tab1:
            self._formulario_solicitar_intercambio()
        
        with tab2:
            self._mostrar_intercambios_pendientes()
        
        with tab3:
            self._gestionar_aprobaciones()
        
        with tab4:
            self._mostrar_historial_intercambios()
    
    def _formulario_solicitar_intercambio(self):
        """Formulario para solicitar intercambio de tareas"""
        st.write("### 📝 Solicitar Intercambio")
        
        if not self.cronograma:
            st.warning("No hay cronograma disponible para intercambios")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔄 Dar mi tarea:**")
            
            roommate_origen = st.selectbox(
                "Tu nombre:",
                [rm.nombre for rm in self.roommates],
                key="origen"
            )
            
            # Obtener tareas del roommate
            tareas_origen = self._get_tareas_roommate(roommate_origen)
            
            if tareas_origen:
                tarea_origen_key = st.selectbox(
                    "Tarea a intercambiar:",
                    list(tareas_origen.keys()),
                    format_func=lambda x: self._format_tarea_display(tareas_origen[x]),
                    key="tarea_origen"
                )
                
                tarea_origen = tareas_origen[tarea_origen_key]
                
                # Mostrar detalles de la tarea
                self._mostrar_detalles_tarea(tarea_origen, "🔄 Tarea que das:")
            else:
                st.info("No tienes tareas asignadas para intercambiar")
                return
        
        with col2:
            st.write("**📥 Recibir tarea:**")
            
            roommate_destino = st.selectbox(
                "Roommate con quien intercambiar:",
                [rm.nombre for rm in self.roommates if rm.nombre != roommate_origen],
                key="destino"
            )
            
            tareas_destino = self._get_tareas_roommate(roommate_destino)
            
            if tareas_destino:
                tarea_destino_key = st.selectbox(
                    "Tarea a recibir:",
                    list(tareas_destino.keys()),
                    format_func=lambda x: self._format_tarea_display(tareas_destino[x]),
                    key="tarea_destino"
                )
                
                tarea_destino = tareas_destino[tarea_destino_key]
                
                # Mostrar detalles de la tarea
                self._mostrar_detalles_tarea(tarea_destino, "📥 Tarea que recibes:")
            else:
                st.info(f"{roommate_destino} no tiene tareas disponibles")
                return
        
        # Razón del intercambio
        razon = st.text_area(
            "Razón del intercambio:",
            placeholder="Ej: Tengo examen el martes, no puedo limpiar el baño...",
            help="Explica por qué necesitas este intercambio"
        )
        
        # Análisis de compatibilidad
        if st.button("🔍 Analizar Compatibilidad"):
            self._analizar_compatibilidad_intercambio(
                tarea_origen, tarea_destino, 
                roommate_origen, roommate_destino
            )
        
        # Botón para solicitar intercambio
        if st.button("📨 Enviar Solicitud de Intercambio", type="primary"):
            if razon.strip():
                self._crear_solicitud_intercambio(
                    tarea_origen_key, tarea_destino_key,
                    roommate_origen, roommate_destino, razon
                )
                st.success("✅ Solicitud de intercambio enviada")
                st.rerun()
            else:
                st.error("Por favor, explica la razón del intercambio")
    
    def _get_tareas_roommate(self, roommate_nombre: str) -> Dict:
        """Obtiene tareas asignadas a un roommate específico"""
        tareas = {}
        for key, asignacion in self.cronograma.items():
            if asignacion['roommate'] == roommate_nombre:
                tareas[key] = asignacion
        return tareas
    
    def _format_tarea_display(self, asignacion: Dict) -> str:
        """Formatea la visualización de una tarea"""
        return f"{asignacion['tarea']} - S{asignacion['semana']} {asignacion['dia']} {asignacion['hora']:02.0f}:{int((asignacion['hora'] % 1) * 60):02d}"
    
    def _mostrar_detalles_tarea(self, asignacion: Dict, titulo: str):
        """Muestra detalles de una tarea"""
        st.write(f"**{titulo}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📋 **Tarea:** {asignacion['tarea']}")
            st.write(f"📅 **Día:** {asignacion['dia']}")
        with col2:
            st.write(f"⏰ **Hora:** {asignacion['hora']:02.0f}:{int((asignacion['hora'] % 1) * 60):02d}")
            st.write(f"⏱️ **Duración:** {asignacion['duracion']} min")
    
    def _analizar_compatibilidad_intercambio(self, tarea1: Dict, tarea2: Dict, 
                                           roommate1: str, roommate2: str):
        """Analiza la compatibilidad del intercambio propuesto"""
        st.write("### 🔍 Análisis de Compatibilidad")
        
        # Verificar disponibilidad de horarios
        rm1_obj = next(rm for rm in self.roommates if rm.nombre == roommate1)
        rm2_obj = next(rm for rm in self.roommates if rm.nombre == roommate2)
        
        # Verificar si roommate1 puede hacer tarea2
        disponible_1_para_2 = rm1_obj.esta_disponible(tarea2['dia'], tarea2['hora'])
        disponible_2_para_1 = rm2_obj.esta_disponible(tarea1['dia'], tarea1['hora'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{roommate1} → Tarea de {roommate2}**")
            if disponible_1_para_2:
                st.success("✅ Horario compatible")
            else:
                st.error("❌ Horario no compatible")
            
            # Verificar habilidades
            tarea2_obj = self._get_tarea_objeto(tarea2['tarea'])
            if tarea2_obj:
                habilidad = rm1_obj.get_habilidad(tarea2_obj.categoria)
                if habilidad >= 6:
                    st.success(f"✅ Buena habilidad ({habilidad}/10)")
                elif habilidad >= 4:
                    st.warning(f"⚠️ Habilidad moderada ({habilidad}/10)")
                else:
                    st.error(f"❌ Habilidad baja ({habilidad}/10)")
        
        with col2:
            st.write(f"**{roommate2} → Tarea de {roommate1}**")
            if disponible_2_para_1:
                st.success("✅ Horario compatible")
            else:
                st.error("❌ Horario no compatible")
            
            # Verificar habilidades
            tarea1_obj = self._get_tarea_objeto(tarea1['tarea'])
            if tarea1_obj:
                habilidad = rm2_obj.get_habilidad(tarea1_obj.categoria)
                if habilidad >= 6:
                    st.success(f"✅ Buena habilidad ({habilidad}/10)")
                elif habilidad >= 4:
                    st.warning(f"⚠️ Habilidad moderada ({habilidad}/10)")
                else:
                    st.error(f"❌ Habilidad baja ({habilidad}/10)")
        
        # Recomendación general
        if disponible_1_para_2 and disponible_2_para_1:
            st.success("🎯 **Recomendación:** Intercambio factible")
        else:
            st.error("🚫 **Recomendación:** Intercambio problemático por horarios")
    
    def _get_tarea_objeto(self, nombre_tarea: str):
        """Obtiene el objeto Tarea por nombre"""
        # Esto debería conectarse con la lista de tareas de session_state
        if hasattr(st.session_state, 'tareas'):
            return next((t for t in st.session_state.tareas if t.nombre == nombre_tarea), None)
        return None
    
    def _crear_solicitud_intercambio(self, tarea_origen_key: str, tarea_destino_key: str,
                                   roommate_origen: str, roommate_destino: str, razon: str):
        """Crea una nueva solicitud de intercambio"""
        solicitud = {
            'id': len(self.intercambios_pendientes) + 1,
            'tarea_origen_key': tarea_origen_key,
            'tarea_destino_key': tarea_destino_key,
            'roommate_origen': roommate_origen,
            'roommate_destino': roommate_destino,
            'razon': razon,
            'fecha_solicitud': datetime.now(),
            'estado': 'pendiente',
            'respuesta': None,
            'fecha_respuesta': None
        }
        
        self.intercambios_pendientes.append(solicitud)
    
    def _mostrar_intercambios_pendientes(self):
        """Muestra intercambios pendientes"""
        st.write("### 📋 Intercambios Pendientes")
        
        if not self.intercambios_pendientes:
            st.info("No hay intercambios pendientes")
            return
        
        for solicitud in self.intercambios_pendientes:
            if solicitud['estado'] == 'pendiente':
                self._mostrar_tarjeta_intercambio(solicitud)
    
    def _mostrar_tarjeta_intercambio(self, solicitud: Dict):
        """Muestra tarjeta de una solicitud de intercambio"""
        with st.container():
            st.markdown("---")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**🔄 Solicitud #{solicitud['id']}**")
                st.write(f"**De:** {solicitud['roommate_origen']}")
                st.write(f"**Para:** {solicitud['roommate_destino']}")
                st.write(f"**Fecha:** {solicitud['fecha_solicitud'].strftime('%d/%m/%Y %H:%M')}")
            
            with col2:
                # Detalles de las tareas
                tarea_origen = self.cronograma[solicitud['tarea_origen_key']]
                tarea_destino = self.cronograma[solicitud['tarea_destino_key']]
                
                st.write("**📤 Da:**")
                st.write(f"• {self._format_tarea_display(tarea_origen)}")
                
                st.write("**📥 Recibe:**")
                st.write(f"• {self._format_tarea_display(tarea_destino)}")
            
            with col3:
                estado_color = {
                    'pendiente': '🟡',
                    'aprobado': '🟢',
                    'rechazado': '🔴'
                }
                st.write(f"{estado_color[solicitud['estado']]} {solicitud['estado'].title()}")
            
            # Razón del intercambio
            st.write(f"**💬 Razón:** {solicitud['razon']}")
    
    def _gestionar_aprobaciones(self):
        """Interfaz para aprobar/rechazar intercambios"""
        st.write("### ✅ Gestionar Solicitudes")
        
        solicitudes_pendientes = [s for s in self.intercambios_pendientes if s['estado'] == 'pendiente']
        
        if not solicitudes_pendientes:
            st.info("No hay solicitudes pendientes de aprobación")
            return
        
        solicitud_sel = st.selectbox(
            "Seleccionar solicitud:",
            range(len(solicitudes_pendientes)),
            format_func=lambda x: f"#{solicitudes_pendientes[x]['id']} - {solicitudes_pendientes[x]['roommate_origen']} ↔ {solicitudes_pendientes[x]['roommate_destino']}"
        )
        
        solicitud = solicitudes_pendientes[solicitud_sel]
        
        # Mostrar detalles completos
        self._mostrar_tarjeta_intercambio(solicitud)
        
        # Opciones de respuesta
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Aprobar Intercambio", type="primary"):
                self._procesar_intercambio(solicitud, 'aprobado')
                st.success("Intercambio aprobado y ejecutado")
                st.rerun()
        
        with col2:
            if st.button("❌ Rechazar Intercambio"):
                motivo_rechazo = st.text_input("Motivo del rechazo:")
                if motivo_rechazo:
                    self._procesar_intercambio(solicitud, 'rechazado', motivo_rechazo)
                    st.info("Intercambio rechazado")
                    st.rerun()
    
    def _procesar_intercambio(self, solicitud: Dict, decision: str, motivo: str = None):
        """Procesa la decisión sobre un intercambio"""
        solicitud['estado'] = decision
        solicitud['fecha_respuesta'] = datetime.now()
        solicitud['respuesta'] = motivo
        
        if decision == 'aprobado':
            # Ejecutar el intercambio
            self._ejecutar_intercambio(solicitud)
        
        # Mover al historial
        self.historial_intercambios.append(solicitud)
        self.intercambios_pendientes.remove(solicitud)
    
    def _ejecutar_intercambio(self, solicitud: Dict):
        """Ejecuta el intercambio aprobado"""
        # Intercambiar roommates en las tareas
        tarea_origen_key = solicitud['tarea_origen_key']
        tarea_destino_key = solicitud['tarea_destino_key']
        
        roommate_origen = solicitud['roommate_origen']
        roommate_destino = solicitud['roommate_destino']
        
        # Realizar el intercambio
        self.cronograma[tarea_origen_key]['roommate'] = roommate_destino
        self.cronograma[tarea_destino_key]['roommate'] = roommate_origen
        
        # Actualizar session_state si existe
        if hasattr(st.session_state, 'cronograma'):
            st.session_state.cronograma = self.cronograma
    
    def _mostrar_historial_intercambios(self):
        """Muestra historial de intercambios"""
        st.write("### 📊 Historial de Intercambios")
        
        if not self.historial_intercambios:
            st.info("No hay intercambios en el historial")
            return
        
        # Convertir a DataFrame para mejor visualización
        datos_historial = []
        for intercambio in self.historial_intercambios:
            datos_historial.append({
                'ID': intercambio['id'],
                'Fecha Solicitud': intercambio['fecha_solicitud'].strftime('%d/%m/%Y'),
                'Solicitante': intercambio['roommate_origen'],
                'Destinatario': intercambio['roommate_destino'],
                'Estado': intercambio['estado'].title(),
                'Fecha Respuesta': intercambio['fecha_respuesta'].strftime('%d/%m/%Y') if intercambio['fecha_respuesta'] else 'N/A'
            })
        
        df_historial = pd.DataFrame(datos_historial)
        
        # Métricas del historial
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Intercambios", len(self.historial_intercambios))
        with col2:
            aprobados = len([i for i in self.historial_intercambios if i['estado'] == 'aprobado'])
            st.metric("Aprobados", aprobados)
        with col3:
            rechazados = len([i for i in self.historial_intercambios if i['estado'] == 'rechazado'])
            st.metric("Rechazados", rechazados)
        with col4:
            tasa_aprobacion = (aprobados / len(self.historial_intercambios) * 100) if self.historial_intercambios else 0
            st.metric("Tasa Aprobación", f"{tasa_aprobacion:.1f}%")
        
        # Tabla del historial
        st.dataframe(df_historial, use_container_width=True, hide_index=True)