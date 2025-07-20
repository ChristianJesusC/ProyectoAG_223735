import streamlit as st
from typing import Dict, List
from models import RangoTiempo
from datetime import time

class PatronesEstudiantiles:
    
    @staticmethod
    def get_patrones_predefinidos() -> Dict[str, Dict]:
        """Patrones de horarios típicos para estudiantes"""
        return {
            "Estudiante Matutino": {
                "descripcion": "Clases por la mañana, libre por la tarde",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 22.0)],
                    'Martes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 22.0)],
                    'Miércoles': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 22.0)],
                    'Jueves': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 22.0)],
                    'Viernes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 22.0)],
                    'Sábado': [RangoTiempo(8.0, 23.0)],
                    'Domingo': [RangoTiempo(8.0, 23.0)]
                },
                "tiempo_objetivo": 15,
                "habilidades_tipicas": {
                    'Limpieza': 5, 'Cocina': 4, 'Lavandería': 6,
                    'Compras': 7, 'Mantenimiento': 4, 'Organización': 6
                }
            },
            
            "Estudiante Vespertino": {
                "descripcion": "Clases por la tarde, libre por la mañana",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 12.0), RangoTiempo(20.0, 23.0)],
                    'Martes': [RangoTiempo(6.0, 12.0), RangoTiempo(20.0, 23.0)],
                    'Miércoles': [RangoTiempo(6.0, 12.0), RangoTiempo(20.0, 23.0)],
                    'Jueves': [RangoTiempo(6.0, 12.0), RangoTiempo(20.0, 23.0)],
                    'Viernes': [RangoTiempo(6.0, 12.0), RangoTiempo(20.0, 23.0)],
                    'Sábado': [RangoTiempo(6.0, 23.0)],
                    'Domingo': [RangoTiempo(6.0, 23.0)]
                },
                "tiempo_objetivo": 16,
                "habilidades_tipicas": {
                    'Limpieza': 6, 'Cocina': 5, 'Lavandería': 5,
                    'Compras': 6, 'Mantenimiento': 5, 'Organización': 7
                }
            },
            
            "Estudiante Nocturno": {
                "descripcion": "Clases por la noche, día libre",
                "horarios": {
                    'Lunes': [RangoTiempo(8.0, 16.0)],
                    'Martes': [RangoTiempo(8.0, 16.0)],
                    'Miércoles': [RangoTiempo(8.0, 16.0)],
                    'Jueves': [RangoTiempo(8.0, 16.0)],
                    'Viernes': [RangoTiempo(8.0, 16.0)],
                    'Sábado': [RangoTiempo(9.0, 22.0)],
                    'Domingo': [RangoTiempo(9.0, 22.0)]
                },
                "tiempo_objetivo": 14,
                "habilidades_tipicas": {
                    'Limpieza': 4, 'Cocina': 6, 'Lavandería': 5,
                    'Compras': 5, 'Mantenimiento': 3, 'Organización': 5
                }
            },
            
            "Estudiante Part-time": {
                "descripcion": "Combina estudios con trabajo",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 22.0)],
                    'Martes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 22.0)],
                    'Miércoles': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 22.0)],
                    'Jueves': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 22.0)],
                    'Viernes': [RangoTiempo(6.0, 8.0), RangoTiempo(19.0, 22.0)],
                    'Sábado': [RangoTiempo(8.0, 14.0)],
                    'Domingo': [RangoTiempo(9.0, 22.0)]
                },
                "tiempo_objetivo": 12,
                "habilidades_tipicas": {
                    'Limpieza': 7, 'Cocina': 6, 'Lavandería': 7,
                    'Compras': 8, 'Mantenimiento': 6, 'Organización': 8
                }
            },
            
            "Estudiante Fin de Semana": {
                "descripcion": "Clases solo fines de semana",
                "horarios": {
                    'Lunes': [RangoTiempo(6.0, 23.0)],
                    'Martes': [RangoTiempo(6.0, 23.0)],
                    'Miércoles': [RangoTiempo(6.0, 23.0)],
                    'Jueves': [RangoTiempo(6.0, 23.0)],
                    'Viernes': [RangoTiempo(6.0, 23.0)],
                    'Sábado': [RangoTiempo(19.0, 23.0)],
                    'Domingo': [RangoTiempo(19.0, 23.0)]
                },
                "tiempo_objetivo": 20,
                "habilidades_tipicas": {
                    'Limpieza': 8, 'Cocina': 7, 'Lavandería': 8,
                    'Compras': 9, 'Mantenimiento': 7, 'Organización': 8
                }
            },
            
            "Estudiante Tesista": {
                "descripcion": "Horarios flexibles, mucho tiempo en casa",
                "horarios": {
                    'Lunes': [RangoTiempo(7.0, 12.0), RangoTiempo(15.0, 18.0), RangoTiempo(21.0, 23.0)],
                    'Martes': [RangoTiempo(7.0, 12.0), RangoTiempo(15.0, 18.0), RangoTiempo(21.0, 23.0)],
                    'Miércoles': [RangoTiempo(7.0, 12.0), RangoTiempo(15.0, 18.0), RangoTiempo(21.0, 23.0)],
                    'Jueves': [RangoTiempo(7.0, 12.0), RangoTiempo(15.0, 18.0), RangoTiempo(21.0, 23.0)],
                    'Viernes': [RangoTiempo(7.0, 12.0), RangoTiempo(15.0, 18.0), RangoTiempo(21.0, 23.0)],
                    'Sábado': [RangoTiempo(9.0, 14.0), RangoTiempo(16.0, 22.0)],
                    'Domingo': [RangoTiempo(9.0, 14.0), RangoTiempo(16.0, 22.0)]
                },
                "tiempo_objetivo": 18,
                "habilidades_tipicas": {
                    'Limpieza': 6, 'Cocina': 8, 'Lavandería': 6,
                    'Compras': 7, 'Mantenimiento': 5, 'Organización': 9
                }
            }
        }
    
    @staticmethod
    def mostrar_selector_patrones():
        """Interfaz para seleccionar patrones estudiantiles"""
        st.subheader("🎓 Patrones de Horarios Estudiantiles")
        st.markdown("*Selecciona un patrón típico y personalízalo según tus necesidades*")
        
        patrones = PatronesEstudiantiles.get_patrones_predefinidos()
        
        # Selector de patrón
        patron_seleccionado = st.selectbox(
            "Selecciona tu patrón de estudiante:",
            list(patrones.keys()),
            format_func=lambda x: f"{x} - {patrones[x]['descripcion']}"
        )
        
        patron = patrones[patron_seleccionado]
        
        # Mostrar detalles del patrón
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 📊 Características del Patrón")
            st.write(f"**Descripción:** {patron['descripcion']}")
            st.write(f"**Tiempo objetivo:** {patron['tiempo_objetivo']} horas/semana")
            
            # Mostrar horas totales disponibles
            horas_totales = PatronesEstudiantiles._calcular_horas_totales(patron['horarios'])
            st.write(f"**Horas disponibles:** {horas_totales:.1f} horas/semana")
            
            eficiencia = (patron['tiempo_objetivo'] / horas_totales * 100) if horas_totales > 0 else 0
            st.write(f"**Eficiencia:** {eficiencia:.1f}% del tiempo disponible")
        
        with col2:
            st.write("### 🎯 Habilidades Típicas")
            for categoria, nivel in patron['habilidades_tipicas'].items():
                color = "🟢" if nivel >= 7 else "🔵" if nivel >= 5 else "🟡" if nivel >= 3 else "🔴"
                st.write(f"{color} **{categoria}:** {nivel}/10")
        
        # Visualización de horarios
        st.write("### 📅 Horarios Semanales")
        PatronesEstudiantiles._mostrar_horarios_patron(patron['horarios'])
        
        # Opciones de personalización
        with st.expander("🛠️ Personalizar Patrón", expanded=False):
            st.write("**Ajustar tiempo objetivo:**")
            tiempo_personalizado = st.slider(
                "Horas/semana:", 
                5, 25, 
                patron['tiempo_objetivo']
            )
            
            st.write("**Ajustar habilidades:**")
            habilidades_personalizadas = {}
            cols = st.columns(3)
            
            for i, (categoria, nivel) in enumerate(patron['habilidades_tipicas'].items()):
                with cols[i % 3]:
                    habilidades_personalizadas[categoria] = st.slider(
                        f"{categoria}:", 
                        1, 10, 
                        nivel,
                        key=f"hab_{categoria}"
                    )
        
        # Botón para aplicar patrón
        if st.button("✅ Aplicar Patrón Estudiantil", type="primary"):
            return {
                'horarios': patron['horarios'],
                'tiempo_objetivo': tiempo_personalizado if 'tiempo_personalizado' in locals() else patron['tiempo_objetivo'],
                'habilidades': habilidades_personalizadas if 'habilidades_personalizadas' in locals() else patron['habilidades_tipicas'],
                'patron_nombre': patron_seleccionado
            }
        
        return None
    
    @staticmethod
    def _calcular_horas_totales(horarios: Dict[str, List[RangoTiempo]]) -> float:
        """Calcula total de horas disponibles en la semana"""
        total = 0
        for dia, rangos in horarios.items():
            for rango in rangos:
                total += rango.duracion_horas()
        return total
    
    @staticmethod
    def _mostrar_horarios_patron(horarios: Dict[str, List[RangoTiempo]]):
        """Muestra visualización de horarios del patrón"""
        import plotly.graph_objects as go
        import numpy as np
        
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        horas = list(range(6, 24))
        
        # Crear matriz de disponibilidad
        matriz = np.zeros((len(horas), len(dias)))
        
        for j, dia in enumerate(dias):
            if dia in horarios:
                for rango in horarios[dia]:
                    inicio_idx = max(0, int(rango.inicio) - 6)
                    fin_idx = min(len(horas), int(rango.fin) - 6)
                    
                    for i in range(inicio_idx, fin_idx):
                        hora_actual = i + 6
                        if rango.contiene_hora(hora_actual):
                            matriz[i][j] = 1
        
        fig = go.Figure(data=go.Heatmap(
            z=matriz,
            x=dias,
            y=[f"{h:02d}:00" for h in horas],
            colorscale=[[0, 'lightgray'], [1, 'lightgreen']],
            showscale=False,
            hoverongaps=False,
            hovertemplate="<b>%{x}</b><br>%{y}<br>%{customdata}<extra></extra>",
            customdata=[["Disponible" if matriz[i][j] == 1 else "No disponible" 
                        for j in range(len(dias))] for i in range(len(horas))]
        ))
        
        fig.update_layout(
            title="Disponibilidad Semanal del Patrón",
            xaxis_title="Días",
            yaxis_title="Horarios",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def get_periodo_examenes_pattern() -> Dict:
        """Patrón especial para período de exámenes"""
        return {
            "descripcion": "Horarios limitados durante época de exámenes",
            "horarios": {
                'Lunes': [RangoTiempo(6.0, 7.0), RangoTiempo(22.0, 23.0)],
                'Martes': [RangoTiempo(6.0, 7.0), RangoTiempo(22.0, 23.0)],
                'Miércoles': [RangoTiempo(6.0, 7.0), RangoTiempo(22.0, 23.0)],
                'Jueves': [RangoTiempo(6.0, 7.0), RangoTiempo(22.0, 23.0)],
                'Viernes': [RangoTiempo(6.0, 7.0), RangoTiempo(22.0, 23.0)],
                'Sábado': [RangoTiempo(7.0, 9.0), RangoTiempo(21.0, 23.0)],
                'Domingo': [RangoTiempo(7.0, 9.0), RangoTiempo(21.0, 23.0)]
            },
            "tiempo_objetivo": 8,
            "habilidades_tipicas": {
                'Limpieza': 3, 'Cocina': 4, 'Lavandería': 3,
                'Compras': 5, 'Mantenimiento': 2, 'Organización': 3
            }
        }
    
    @staticmethod
    def get_vacaciones_pattern() -> Dict:
        """Patrón especial para vacaciones"""
        return {
            "descripcion": "Máxima disponibilidad durante vacaciones",
            "horarios": {
                'Lunes': [RangoTiempo(8.0, 22.0)],
                'Martes': [RangoTiempo(8.0, 22.0)],
                'Miércoles': [RangoTiempo(8.0, 22.0)],
                'Jueves': [RangoTiempo(8.0, 22.0)],
                'Viernes': [RangoTiempo(8.0, 22.0)],
                'Sábado': [RangoTiempo(9.0, 23.0)],
                'Domingo': [RangoTiempo(9.0, 23.0)]
            },
            "tiempo_objetivo": 25,
            "habilidades_tipicas": {
                'Limpieza': 8, 'Cocina': 7, 'Lavandería': 8,
                'Compras': 9, 'Mantenimiento': 7, 'Organización': 8
            }
        }