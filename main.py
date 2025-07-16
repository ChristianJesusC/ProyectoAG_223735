import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas, EspacioHogar
from genetic_algorithm import AlgoritmoGeneticoOptimizado
from calendar_views import (
    crear_calendario_mensual, mostrar_calendario_individual,
    mostrar_vista_tabla, get_roommate_color
)
from ui_components import UIComponentsMejorado
from utils import DataUtilsMejorado
from rotation_manager import RotationManager
from analysis_components import AnalysisComponents

st.set_page_config(page_title="ROOMIETASKAI", page_icon="🏠", layout="wide")

def init_session():
    defaults = {
        'roommates': [],
        'tareas': [],
        'cronograma': None,
        'fitness_historia': [],
        'form_counter': 0,
        'espacio_hogar': EspacioHogar(),
        'demo_cargada': False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def cargar_datos_demo_simple():
    """Función simplificada que solo carga datos sin UI compleja"""
    roommates_demo, tareas_seleccionadas = DataUtilsMejorado.generar_datos_demo_aleatorios()
    
    st.session_state.roommates = roommates_demo
    st.session_state.tareas = tareas_seleccionadas
    st.session_state.demo_cargada = True
    
    return len(roommates_demo), len(tareas_seleccionadas)

def mostrar_resumen_demo():
    """Muestra el resumen de la demo cargada en el área principal"""
    if st.session_state.demo_cargada and st.session_state.roommates:
        st.info(f"🎲 **Demo cargada**: {len(st.session_state.roommates)} roommates aleatorios con {len(st.session_state.tareas)} tareas")
        
        with st.expander("📋 Ver detalles de roommates generados", expanded=False):
            analisis_roommates = DataUtilsMejorado.analizar_roommates_generados(st.session_state.roommates)
            
            for analisis in analisis_roommates:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👤 {analisis['nombre']}**")
                    st.write(f"⏰ {analisis['horas_totales']:.1f}h/semana disponibles")
                    st.write(f"🎯 Objetivo: {analisis['tiempo_objetivo']}h/semana")
                
                with col2:
                    if analisis['especialidades']:
                        st.write(f"**🌟 Especialidades:**")
                        for esp in analisis['especialidades']:
                            rm_obj = next(rm for rm in st.session_state.roommates if rm.nombre == analisis['nombre'])
                            nivel = rm_obj.habilidades[esp]
                            st.write(f"• {esp} ({nivel}/10)")
                    else:
                        st.write("**🌟 Sin especialidades marcadas**")
                
                with col3:
                    if analisis['debilidades']:
                        st.write(f"**⚠️ Debilidades:**")
                        for deb in analisis['debilidades']:
                            rm_obj = next(rm for rm in st.session_state.roommates if rm.nombre == analisis['nombre'])
                            nivel = rm_obj.habilidades[deb]
                            st.write(f"• {deb} ({nivel}/10)")
                    else:
                        st.write("**✅ Sin debilidades marcadas**")
                
                st.markdown("---")
        
        if st.button("✅ Entendido, ocultar resumen"):
            st.session_state.demo_cargada = False
            st.rerun()

def pagina_analisis_conflictos():
    st.header("⚠️ Análisis Detallado de Conflictos")
    st.markdown("*Detección y resolución de choques de horarios*")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        return
    
    from conflict_detector import DetectorConflictos
    
    detector = DetectorConflictos(
        st.session_state.cronograma,
        st.session_state.roommates,
        st.session_state.tareas
    )
    
    conflictos, tipos = detector.mostrar_resumen_conflictos()
    
    if conflictos:
        st.subheader("🔧 Sugerencias de Resolución")
        
        with st.expander("💡 Estrategias para Resolver Conflictos", expanded=True):
            st.write("**Opciones para reducir conflictos:**")
            st.write("1. **Re-optimizar** con mayor peso en 'compatibilidad'")
            st.write("2. **Ajustar horarios** de roommates con más disponibilidad")
            st.write("3. **Dividir tareas largas** en bloques más pequeños")
            st.write("4. **Cambiar frecuencias** de tareas menos críticas")
            st.write("5. **Asignar más tiempo objetivo** por semana a roommates")
        
        # Botón para re-optimizar enfocado en conflictos
        if st.button("🚀 Re-optimizar Priorizando Compatibilidad", type="primary"):
            st.info("Ejecutando optimización con mayor peso en compatibilidad de horarios...")
            # Aquí iría la lógica para re-ejecutar el AG con pesos ajustados

def mostrar_sidebar():
    st.sidebar.title("🏠 ROOMIETASKAI")
    st.sidebar.markdown("*Distribución Inteligente de Tareas (Mensual)*")
    
    paginas = {
        "🔧 Setup": pagina_setup,
        "🏠 Espacio": pagina_espacio,
        "🧠 Optimizar": pagina_optimizar,
        "🗓️ Calendario Mensual": pagina_calendario_mensual,
        "🔄 Plan Rotación": pagina_plan_rotacion,
        "📊 Análisis": pagina_analisis
    }
    
    pagina = st.sidebar.selectbox("Navegación", list(paginas.keys()), label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Roommates:** {len(st.session_state.roommates)}")
    st.sidebar.markdown(f"**Tareas:** {len(st.session_state.tareas)}")
    
    # Mostrar información del cronograma mensual si existe
    if st.session_state.cronograma:
        semanas_con_datos = set(asig['semana'] for asig in st.session_state.cronograma.values())
        st.sidebar.markdown(f"**Semanas:** {len(semanas_con_datos)}/4")
        st.sidebar.markdown(f"**Estado:** ✅ Cronograma mensual generado")
    else:
        st.sidebar.markdown(f"**Estado:** ⏳ Sin cronograma")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset"):
            for key in ['roommates', 'tareas', 'cronograma', 'fitness_historia', 'demo_cargada']:
                if key == 'cronograma':
                    st.session_state[key] = None
                elif key == 'demo_cargada':
                    st.session_state[key] = False
                else:
                    st.session_state[key] = []
            st.rerun()
    
    with col2:
        if st.button("📝 Demo"):
            num_roommates, num_tareas = cargar_datos_demo_simple()
            st.sidebar.success(f"Demo: {num_roommates} roommates, {num_tareas} tareas")
            st.rerun()
    
    return paginas[pagina]

def pagina_setup():
    st.header("🔧 Configuración del Sistema")
    mostrar_resumen_demo()
    
    ui = UIComponentsMejorado()
    ui.mostrar_configuracion_roommates()

def pagina_espacio():
    st.header("🏠 Características del Espacio")
    mostrar_resumen_demo()
    
    ui = UIComponentsMejorado()
    ui.mostrar_configuracion_espacio()

def pagina_optimizar():
    st.header("🧠 Optimización Mensual con Algoritmo Genético")
    st.markdown("*Genera cronogramas únicos para 4 semanas con intervalos de 30 minutos*")
    
    mostrar_resumen_demo()
    
    if not st.session_state.roommates or not st.session_state.tareas:
        st.error("Configura roommates y tareas primero")
        return
    
    # Verificar que hay tareas de cocina
    tareas_cocina = [t for t in st.session_state.tareas if t.categoria == 'Cocina']
    if not tareas_cocina:
        st.warning("⚠️ No hay tareas de cocina configuradas. Se recomienda agregar tareas de cocina para cumplir el requisito diario.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Roommates", len(st.session_state.roommates))
    with col2:
        st.metric("Tareas", len(st.session_state.tareas))
        st.caption(f"Cocina: {len(tareas_cocina)}")
    with col3:
        tiempo_total_mensual = sum(t.tiempo_estimado * t.get_repeticiones_semanales() * 4 for t in st.session_state.tareas)
        st.metric("Tiempo Total Mensual", f"{tiempo_total_mensual//60}h {tiempo_total_mensual%60}min")
    
    st.subheader("Parámetros del Algoritmo")
    col1, col2 = st.columns(2)
    
    with col1:
        poblacion = st.number_input("Población", 10, 1000, 50, step=10)
        generaciones = st.number_input("Generaciones", 5, 200, 40, step=5)
        
        st.info("💡 **Intervalos de 30 minutos**: El algoritmo programa tareas en intervalos de media hora para mayor precisión.")
    
    with col2:
        with st.expander("Pesos de optimización"):
            peso_equidad = st.slider("Equidad", 0, 100, 25)
            peso_compatibilidad = st.slider("Compatibilidad", 0, 100, 25)
            peso_habilidades = st.slider("Habilidades", 0, 100, 15)
            peso_preferencias = st.slider("Preferencias", 0, 100, 10)
            peso_rotacion = st.slider("Rotación entre semanas", 0, 100, 10)
            peso_cocina = st.slider("Cocina diaria", 0, 100, 15)
    
    # Advertencias de complejidad
    complejidad = poblacion * generaciones
    if complejidad > 10000:
        st.warning(f"⚠️ Configuración intensiva: {complejidad:,} evaluaciones. Tiempo estimado: 2-5 minutos.")
    elif complejidad > 5000:
        st.info(f"💡 Configuración moderada: {complejidad:,} evaluaciones. Tiempo estimado: 1-2 minutos.")
    else:
        st.success(f"✅ Configuración rápida: {complejidad:,} evaluaciones. Tiempo estimado: <1 minuto.")
    
    if st.button("🚀 Optimizar Cronograma Mensual", type="primary"):
        with st.spinner(f"Ejecutando algoritmo genético para 4 semanas..."):
            try:
                ag = AlgoritmoGeneticoOptimizado(
                    st.session_state.roommates,
                    st.session_state.tareas,
                    poblacion,
                    generaciones
                )
                
                ag.ajustar_pesos(
                    equidad=peso_equidad,
                    compatibilidad=peso_compatibilidad,
                    habilidades=peso_habilidades,
                    preferencias=peso_preferencias,
                    rotacion=peso_rotacion,
                    cocina_diaria=peso_cocina
                )
                
                mejor, historia = ag.ejecutar()
                
                st.session_state.cronograma = mejor
                st.session_state.fitness_historia = historia
                
                st.success("¡Optimización mensual completada!")
                
                # Métricas de resultado
                if historia:
                    fitness_inicial = historia[0]['mejor']
                    fitness_final = historia[-1]['mejor'] 
                    mejora = ((fitness_final - fitness_inicial) / fitness_inicial * 100) if fitness_inicial > 0 else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Fitness Inicial", f"{fitness_inicial:.3f}")
                    with col2:
                        st.metric("Fitness Final", f"{fitness_final:.3f}")
                    with col3:
                        st.metric("Mejora", f"{mejora:.1f}%")
                    with col4:
                        semanas_generadas = len(set(asig['semana'] for asig in mejor.values()))
                        st.metric("Semanas", f"{semanas_generadas}/4")
                
                # Verificar cocina diaria
                if tareas_cocina:
                    dias_con_cocina = set()
                    for asig in mejor.values():
                        tarea_obj = next((t for t in st.session_state.tareas if t.nombre == asig['tarea']), None)
                        if tarea_obj and tarea_obj.categoria == 'Cocina':
                            dias_con_cocina.add(f"S{asig['semana']}_{asig['dia']}")
                    
                    cumplimiento_cocina = len(dias_con_cocina) / 28 * 100  # 28 días en 4 semanas
                    
                    if cumplimiento_cocina >= 90:
                        st.success(f"🍳 Cocina diaria: {cumplimiento_cocina:.1f}% de cumplimiento")
                    else:
                        st.warning(f"🍳 Cocina diaria: {cumplimiento_cocina:.1f}% de cumplimiento (objetivo: 100%)")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Error en optimización: {e}")
    
    # Mostrar progreso de optimización
    if st.session_state.fitness_historia:
        st.subheader("📈 Progreso de Optimización")
        datos = st.session_state.fitness_historia
        gen = [d['generacion'] for d in datos]
        mejor = [d['mejor'] for d in datos]
        promedio = [d['promedio'] for d in datos]
        
        fig = px.line(x=gen, y=[mejor, promedio], 
                     title="Evolución del Fitness (Cronograma Mensual)")
        fig.update_layout(xaxis_title="Generación", yaxis_title="Fitness")
        fig.data[0].name = "Mejor"
        fig.data[1].name = "Promedio"
        st.plotly_chart(fig, use_container_width=True)

def pagina_calendario_mensual():
    st.header("🗓️ Calendario Mensual (4 Semanas)")
    st.markdown("*Vista completa del cronograma mensual con intervalos de 30 minutos*")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero para generar el cronograma mensual")
        return
    
    # Agregar opciones de exportación al inicio
    from calendar_views import mostrar_opciones_exportacion
    mostrar_opciones_exportacion()
    
    st.divider()
    
    # Tipo de vista
    tipo_vista = st.radio(
        "Tipo de vista:",
        ["🗓️ Calendario Visual", "📊 Tabla Completa"],
        horizontal=True
    )
    
    if tipo_vista == "🗓️ Calendario Visual":
        crear_calendario_mensual()
    else:
        mostrar_vista_tabla()
        
def pagina_plan_rotacion():
    st.header("🔄 Plan de Rotación Mensual")
    
    if not st.session_state.roommates or not st.session_state.tareas:
        st.warning("Configura roommates y tareas primero")
        return
    
    rotation_manager = RotationManager()
    rotation_manager.mostrar_plan_rotacion()

def pagina_analisis():
    st.header("📊 Análisis Completo del Sistema")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        return
    
    analysis = AnalysisComponents()
    analysis.mostrar_analisis_completo()

def main():
    init_session()
    
    st.title("🏠 ROOMIETASKAI")
    st.markdown("### *Sistema Inteligente de Distribución de Tareas Domésticas - Cronograma Mensual*")
    st.markdown("🕐 **Intervalos de 30 minutos** | 📅 **4 semanas diferentes** | 🍳 **Cocina garantizada diariamente**")
    
    pagina_ejecutar = mostrar_sidebar()
    pagina_ejecutar()

if __name__ == "__main__":
    main()