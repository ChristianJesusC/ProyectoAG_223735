import streamlit as st
from typing import Dict, Optional
from models import RangoTiempo, Roommate
import plotly.graph_objects as go

class PatronesEstudiantiles:
    
    @staticmethod
    def get_patrones_predefinidos() -> Dict[str, Dict]:
        return {
            "🌅 Estudiante Matutino": {
                "descripcion": "Clases temprano, tardes libres",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                    'Martes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                    'Miércoles': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                    'Jueves': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                    'Viernes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                    'Sábado': [RangoTiempo(8.0, 22.0)],
                    'Domingo': [RangoTiempo(8.0, 22.0)]
                },
                "tiempo_objetivo": 15,
                "habilidades": {
                    'Limpieza': 5, 'Cocina': 4, 'Lavandería': 6,
                    'Compras': 7, 'Mantenimiento': 4, 'Organización': 6
                },
                "color": "#FF6B6B"
            },
            
            "🌆 Estudiante Vespertino": {
                "descripcion": "Mañanas libres, clases por la tarde",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                    'Martes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                    'Miércoles': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                    'Jueves': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                    'Viernes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                    'Sábado': [RangoTiempo(7.0, 22.0)],
                    'Domingo': [RangoTiempo(7.0, 22.0)]
                },
                "tiempo_objetivo": 16,
                "habilidades": {
                    'Limpieza': 6, 'Cocina': 5, 'Lavandería': 5,
                    'Compras': 6, 'Mantenimiento': 5, 'Organización': 7
                },
                "color": "#4ECDC4"
            },
            
            "⚡ Estudiante Flexible": {
                "descripcion": "Horarios variables, buena disponibilidad",
                "horarios": {
                    'Lunes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                    'Martes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                    'Miércoles': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                    'Jueves': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                    'Viernes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                    'Sábado': [RangoTiempo(9.0, 21.0)],
                    'Domingo': [RangoTiempo(9.0, 21.0)]
                },
                "tiempo_objetivo": 18,
                "habilidades": {
                    'Limpieza': 6, 'Cocina': 6, 'Lavandería': 6,
                    'Compras': 7, 'Mantenimiento': 5, 'Organización': 7
                },
                "color": "#45B7D1"
            },
            
            "💼 Estudiante Part-time": {
                "descripcion": "Combina estudios con trabajo",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 21.0)],
                    'Martes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 21.0)],
                    'Miércoles': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 21.0)],
                    'Jueves': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 21.0)],
                    'Viernes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 21.0)],
                    'Sábado': [RangoTiempo(8.0, 14.0)],
                    'Domingo': [RangoTiempo(9.0, 21.0)]
                },
                "tiempo_objetivo": 12,
                "habilidades": {
                    'Limpieza': 7, 'Cocina': 6, 'Lavandería': 7,
                    'Compras': 8, 'Mantenimiento': 6, 'Organización': 8
                },
                "color": "#96CEB4"
            },
            
            "📚 Estudiante Intensivo": {
                "descripcion": "Horarios limitados, época de exámenes",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 7.0), RangoTiempo(21.0, 22.0)],
                    'Martes': [RangoTiempo(6.0, 7.0), RangoTiempo(21.0, 22.0)],
                    'Miércoles': [RangoTiempo(6.0, 7.0), RangoTiempo(21.0, 22.0)],
                    'Jueves': [RangoTiempo(6.0, 7.0), RangoTiempo(21.0, 22.0)],
                    'Viernes': [RangoTiempo(6.0, 7.0), RangoTiempo(21.0, 22.0)],
                    'Sábado': [RangoTiempo(7.0, 9.0), RangoTiempo(20.0, 22.0)],
                    'Domingo': [RangoTiempo(7.0, 9.0), RangoTiempo(20.0, 22.0)]
                },
                "tiempo_objetivo": 8,
                "habilidades": {
                    'Limpieza': 3, 'Cocina': 4, 'Lavandería': 3,
                    'Compras': 5, 'Mantenimiento': 2, 'Organización': 3
                },
                "color": "#FECA57"
            }
        }
    
    @staticmethod
    def mostrar_interfaz_completa():
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>🎓 Patrones de Horarios Estudiantiles</h3>
            <p style='color: white; margin: 0; opacity: 0.9;'>
                Crea roommates automáticamente con patrones optimizados para estudiantes
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Inicializar session state para patrones
        if 'patron_seleccionado' not in st.session_state:
            st.session_state.patron_seleccionado = None
        
        patrones = PatronesEstudiantiles.get_patrones_predefinidos()
        
        # Selector visual de patrones
        patron_key = st.selectbox(
            "Selecciona tu patrón de estudiante:",
            list(patrones.keys()),
            format_func=lambda x: f"{x} - {patrones[x]['descripcion']}",
            key="selector_patron_estudiante"
        )
        
        patron = patrones[patron_key]
        st.session_state.patron_seleccionado = patron
        
        # Vista previa del patrón
        col1, col2 = st.columns([2, 1])
        
        with col1:
            PatronesEstudiantiles._mostrar_vista_previa_horarios(patron)
        
        with col2:
            PatronesEstudiantiles._mostrar_stats_patron(patron)
        
        # Personalización básica
        with st.expander("⚙️ Personalizar Patrón", expanded=False):
            tiempo_personalizado = st.slider(
                "Horas objetivo por semana:", 
                5, 25, 
                patron['tiempo_objetivo'],
                key="tiempo_patron_estudiante",
                help="Cantidad de horas que puedes dedicar a tareas domésticas"
            )
            patron['tiempo_objetivo'] = tiempo_personalizado
        
        # Sección de creación de roommate
        st.markdown("---")
        st.markdown("### 👤 Crear Roommate con este Patrón")
        
        # Input para nombre
        nombre_nuevo = st.text_input(
            "Nombre del roommate:", 
            placeholder="Ej: María González",
            key="nombre_nuevo_estudiante"
        )
        
        # Verificar si ya existe
        nombres_existentes = [rm.nombre for rm in st.session_state.roommates]
        
        if nombre_nuevo:
            if nombre_nuevo.strip() in nombres_existentes:
                st.error(f"❌ Ya existe un roommate con el nombre '{nombre_nuevo}'")
            else:
                st.success(f"✅ Nombre '{nombre_nuevo}' disponible")
                
                # Botón para crear
                if st.button(
                    f"🎓 Crear {nombre_nuevo} como {patron_key}", 
                    type="primary", 
                    use_container_width=True,
                    key="crear_roommate_estudiante"
                ):
                    return PatronesEstudiantiles._crear_roommate_con_patron(
                        nombre_nuevo.strip(), 
                        patron_key, 
                        patron
                    )
        
        # Opción para actualizar roommate existente
        if st.session_state.roommates:
            st.markdown("---")
            st.markdown("### 🔄 O actualizar roommate existente")
            
            roommate_actualizar = st.selectbox(
                "Seleccionar roommate para actualizar:",
                options=[None] + st.session_state.roommates,
                format_func=lambda x: "Seleccionar..." if x is None else f"🔄 {x.nombre}",
                key="roommate_actualizar_estudiante"
            )
            
            if roommate_actualizar:
                if st.button(
                    f"🔄 Actualizar {roommate_actualizar.nombre} con {patron_key}",
                    type="secondary",
                    use_container_width=True,
                    key="actualizar_roommate_estudiante"
                ):
                    return PatronesEstudiantiles._actualizar_roommate_con_patron(
                        roommate_actualizar, 
                        patron_key, 
                        patron
                    )
        
        return None
    
    @staticmethod
    def _crear_roommate_con_patron(nombre: str, patron_key: str, patron: Dict) -> bool:
        """Crea un nuevo roommate con el patrón seleccionado"""
        try:
            nuevo_roommate = Roommate(
                nombre=nombre,
                horarios_disponibles=patron['horarios'],
                habilidades=patron['habilidades'],
                preferencias={cat: 'neutro' for cat in patron['habilidades'].keys()},
                tiempo_total_disponible=patron['tiempo_objetivo']
            )
            
            st.session_state.roommates.append(nuevo_roommate)
            
            st.success(f"🎉 ¡Roommate '{nombre}' creado exitosamente!")
            st.info(f"✨ Patrón aplicado: **{patron_key}**")
            
            # Mostrar resumen
            with st.expander("📊 Resumen del roommate creado", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⏰ Horarios configurados:**")
                    for dia, rangos in patron['horarios'].items():
                        horas_dia = sum(r.duracion_horas() for r in rangos)
                        st.write(f"• **{dia}:** {horas_dia:.1f}h disponibles")
                
                with col2:
                    st.markdown("**🎯 Habilidades asignadas:**")
                    for categoria, nivel in patron['habilidades'].items():
                        st.write(f"• **{categoria}:** {nivel}/10")
                
                st.markdown(f"**📈 Tiempo objetivo:** {patron['tiempo_objetivo']} horas/semana")
            
            # Limpiar inputs
            for key in ['nombre_nuevo_estudiante', 'tiempo_patron_estudiante']:
                if key in st.session_state:
                    del st.session_state[key]
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al crear roommate: {str(e)}")
            return False
    
    @staticmethod
    def _actualizar_roommate_con_patron(roommate: Roommate, patron_key: str, patron: Dict) -> bool:
        """Actualiza un roommate existente con el patrón seleccionado"""
        try:
            # Guardar nombre original
            nombre_original = roommate.nombre
            
            # Actualizar atributos
            roommate.horarios_disponibles = patron['horarios']
            roommate.habilidades = patron['habilidades']
            roommate.tiempo_total_disponible = patron['tiempo_objetivo']
            
            st.success(f"🔄 ¡Roommate '{nombre_original}' actualizado exitosamente!")
            st.info(f"✨ Nuevo patrón aplicado: **{patron_key}**")
            
            # Mostrar cambios
            with st.expander("📊 Cambios aplicados", expanded=True):
                st.markdown(f"**👤 Roommate:** {nombre_original}")
                st.markdown(f"**🎓 Nuevo patrón:** {patron_key}")
                st.markdown(f"**⏰ Tiempo objetivo:** {patron['tiempo_objetivo']} horas/semana")
                
                st.markdown("**🎯 Habilidades actualizadas:**")
                for categoria, nivel in patron['habilidades'].items():
                    st.write(f"• **{categoria}:** {nivel}/10")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al actualizar roommate: {str(e)}")
            return False
    
    @staticmethod
    def _mostrar_vista_previa_horarios(patron: Dict):
        """Muestra vista previa visual de los horarios"""
        st.write("#### 📅 Vista Previa de Horarios")
        
        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        horas = list(range(6, 24))
        
        # Crear matriz de disponibilidad
        matriz = []
        for hora in horas:
            fila = []
            for i, dia_completo in enumerate(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']):
                disponible = False
                if dia_completo in patron['horarios']:
                    for rango in patron['horarios'][dia_completo]:
                        if rango.contiene_hora(hora):
                            disponible = True
                            break
                fila.append(1 if disponible else 0)
            matriz.append(fila)
        
        fig = go.Figure(data=go.Heatmap(
            z=matriz,
            x=dias,
            y=[f"{h:02d}:00" for h in horas],
            colorscale=[[0, '#f8f9fa'], [1, patron['color']]],
            showscale=False,
            hoverongaps=False,
            hovertemplate="<b>%{x}</b><br>%{y}<br>%{customdata}<extra></extra>",
            customdata=[["✅ Disponible" if matriz[i][j] == 1 else "❌ No disponible" 
                        for j in range(7)] for i in range(len(horas))]
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            font=dict(size=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _mostrar_stats_patron(patron: Dict):
        """Muestra estadísticas del patrón"""
        st.write("#### 📊 Estadísticas")
        
        # Calcular horas totales disponibles
        horas_totales = 0
        for rangos in patron['horarios'].values():
            for rango in rangos:
                horas_totales += rango.duracion_horas()
        
        # Métricas
        st.metric("⏰ Horas/semana disponibles", f"{horas_totales:.1f}h")
        st.metric("🎯 Objetivo tareas", f"{patron['tiempo_objetivo']}h")
        
        eficiencia = (patron['tiempo_objetivo'] / horas_totales * 100) if horas_totales > 0 else 0
        st.metric("📈 Eficiencia", f"{eficiencia:.0f}%")
        
        # Habilidades destacadas
        st.write("**🌟 Fortalezas:**")
        fortalezas = {k: v for k, v in patron['habilidades'].items() if v >= 6}
        if fortalezas:
            for categoria, nivel in fortalezas.items():
                st.write(f"• **{categoria}:** {nivel}/10")
        else:
            st.write("• Perfil equilibrado")
    
    @staticmethod
    def mostrar_selector_rapido():
        """Selector rápido para usar en otras páginas"""
        if 'patron_rapido_aplicado' not in st.session_state:
            st.session_state.patron_rapido_aplicado = False
        
        with st.expander("🎓 Aplicar Patrón Estudiantil Rápido", expanded=False):
            patrones = PatronesEstudiantiles.get_patrones_predefinidos()
            
            patron_key = st.selectbox(
                "Patrón:",
                list(patrones.keys()),
                key="patron_rapido_select"
            )
            
            nombre = st.text_input("Nombre:", key="patron_rapido_nombre")
            
            if nombre and st.button("Aplicar", key="patron_rapido_btn"):
                patron = patrones[patron_key]
                if PatronesEstudiantiles._crear_roommate_con_patron(nombre, patron_key, patron):
                    st.session_state.patron_rapido_aplicado = True
                    st.rerun()
    
    @staticmethod
    def get_patron_recomendado_por_disponibilidad(horas_disponibles: float) -> str:
        """Recomienda patrón basado en disponibilidad"""
        if horas_disponibles >= 50:
            return "⚡ Estudiante Flexible"
        elif horas_disponibles >= 30:
            return "🌆 Estudiante Vespertino"
        elif horas_disponibles >= 20:
            return "🌅 Estudiante Matutino"
        elif horas_disponibles >= 15:
            return "💼 Estudiante Part-time"
        else:
            return "📚 Estudiante Intensivo"