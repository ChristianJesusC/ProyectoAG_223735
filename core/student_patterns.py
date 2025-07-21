import streamlit as st
from typing import Dict, Optional
from models import RangoTiempo
import plotly.graph_objects as go

class PatronesEstudiantiles:
    """Patrones de horarios típicos para estudiantes"""
    
    @staticmethod
    def get_patrones_predefinidos() -> Dict[str, Dict]:
        """Patrones de horario optimizados para diferentes tipos de estudiantes"""
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
    def mostrar_selector_patrones() -> Optional[Dict]:
        """Interfaz para seleccionar y personalizar patrones"""
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
            <h3 style='color: white; margin: 0;'>🎓 Patrones de Horarios Estudiantiles</h3>
            <p style='color: white; margin: 0; opacity: 0.9;'>
                Selecciona un patrón que se adapte a tu estilo de vida universitario
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        patrones = PatronesEstudiantiles.get_patrones_predefinidos()
        
        # Selector visual de patrones
        patron_seleccionado = st.selectbox(
            "Selecciona tu patrón de estudiante:",
            list(patrones.keys()),
            format_func=lambda x: f"{x} - {patrones[x]['descripcion']}",
            key="selector_patron"
        )
        
        patron = patrones[patron_seleccionado]
        
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
                help="Cantidad de horas que puedes dedicar a tareas domésticas"
            )
        
        # Aplicar patrón
        if st.button("✅ Aplicar Patrón Estudiantil", type="primary", use_container_width=True):
            return {
                'horarios': patron['horarios'],
                'tiempo_objetivo': tiempo_personalizado if 'tiempo_personalizado' in locals() else patron['tiempo_objetivo'],
                'habilidades': patron['habilidades'],
                'patron_nombre': patron_seleccionado,
                'patron_color': patron['color']
            }
        
        return None
    
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
    def get_patron_recomendado_por_disponibilidad(horas_disponibles: float) -> str:
        """Recomienda patrón basado en disponibilidad"""
        patrones = PatronesEstudiantiles.get_patrones_predefinidos()
        
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