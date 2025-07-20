import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import date, timedelta

# Importaciones originales
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas, EspacioHogar
from genetic_algorithm import AlgoritmoGeneticoOptimizado
from calendar_views import (
    crear_calendario_mensual, mostrar_calendario_individual,
    mostrar_vista_tabla, get_roommate_color, crear_calendario_mensual_con_conflictos
)
from ui_components import UIComponentsMejorado
from utils import DataUtilsMejorado
from rotation_manager import RotationManager
from analysis_components import AnalysisComponents

from enhanced_models import RoommateEnhanced, RestriccionMedica, Ausencia
from absence_manager import ManagerAusencias
from emergency_manager import ManagerEmergencias
from task_exchange import IntercambiadorTareas
from feedback_system import SistemaFeedback
from student_patterns import PatronesEstudiantiles
from enhanced_genetic_algorithm import AlgoritmoGeneticoMejorado

st.set_page_config(page_title="ROOMIETASKAI", page_icon="🏠", layout="wide")

def init_session():
    defaults = {
        'roommates': [],
        'tareas': [],
        'cronograma': None,
        'fitness_historia': [],
        'form_counter': 0,
        'espacio_hogar': EspacioHogar(),
        'demo_cargada': False,
        'sistema_feedback': None,
        'usar_algoritmo_mejorado': True,
        'emergencias_activas': [],
        'intercambios_pendientes': [],
        'historial_intercambios': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def cargar_datos_demo_simple():
    """Función simplificada que solo carga datos sin UI compleja"""
    roommates_demo, tareas_seleccionadas = DataUtilsMejorado.generar_datos_demo_aleatorios()
    
    # Convertir a RoommateEnhanced para aprovechar nuevas características
    roommates_enhanced = []
    for rm in roommates_demo:
        rm_enhanced = RoommateEnhanced(
            nombre=rm.nombre,
            horarios_disponibles=rm.horarios_disponibles,
            habilidades=rm.habilidades,
            preferencias=rm.preferencias,
            tiempo_total_disponible=rm.tiempo_total_disponible,
            restricciones_medicas=[],
            incompatibilidades=[],
            ausencias=[]
        )
        
        # Agregar algunas restricciones demo aleatorias
        if np.random.random() < 0.3:  # 30% chance de tener restricción
            tipo_restriccion = np.random.choice(['alergia', 'limitacion_fisica', 'medica'])
            categoria_afectada = np.random.choice(['Limpieza', 'Cocina', 'Mantenimiento'])
            severidad = np.random.choice(['limitado', 'con_ayuda'])
            
            restriccion = RestriccionMedica(
                categoria_tarea=categoria_afectada,
                tipo_restriccion=tipo_restriccion,
                descripcion=f"Demo: {tipo_restriccion} en {categoria_afectada}",
                severidad=severidad
            )
            rm_enhanced.restricciones_medicas.append(restriccion)
        
        roommates_enhanced.append(rm_enhanced)
    
    st.session_state.roommates = roommates_enhanced
    st.session_state.tareas = tareas_seleccionadas
    st.session_state.demo_cargada = True
    
    return len(roommates_enhanced), len(tareas_seleccionadas)

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
                
                # Mostrar restricciones si las hay
                rm_obj = next(rm for rm in st.session_state.roommates if rm.nombre == analisis['nombre'])
                if hasattr(rm_obj, 'restricciones_medicas') and rm_obj.restricciones_medicas:
                    st.write(f"**🏥 Restricciones:** {len(rm_obj.restricciones_medicas)}")
                
                st.markdown("---")
        
        if st.button("✅ Entendido, ocultar resumen"):
            st.session_state.demo_cargada = False
            st.rerun()

def mostrar_sidebar():
    st.sidebar.title("🏠 ROOMIETASKAI")
    st.sidebar.markdown("*Distribución Inteligente de Tareas (Mensual)*")
    
    paginas = {
        "🔧 Setup": pagina_setup,
        "🎓 Patrones Estudiantiles": pagina_patrones_estudiantiles,
        "🏥 Restricciones Médicas": pagina_restricciones_medicas,
        "🏠 Espacio": pagina_espacio,
        "🏖️ Ausencias": pagina_ausencias,
        "🚨 Emergencias": pagina_emergencias,
        "🧠 Optimizar": pagina_optimizar,
        "🗓️ Calendario Mensual": pagina_calendario_mensual,
        "⚠️ Conflictos": pagina_analisis_conflictos,
        "🔄 Intercambios": pagina_intercambios,
        "📝 Feedback": pagina_feedback,
        "🔄 Plan Rotación": pagina_plan_rotacion,
        "📊 Análisis": pagina_analisis
    }
    
    pagina = st.sidebar.selectbox("Navegación", list(paginas.keys()), label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    
    # Información del estado actual
    st.sidebar.markdown(f"**Roommates:** {len(st.session_state.roommates)}")
    if st.session_state.roommates and hasattr(st.session_state.roommates[0], 'restricciones_medicas'):
        restricciones_totales = sum(len(rm.restricciones_medicas) for rm in st.session_state.roommates)
        if restricciones_totales > 0:
            st.sidebar.markdown(f"**Restricciones médicas:** {restricciones_totales}")
    
    st.sidebar.markdown(f"**Tareas:** {len(st.session_state.tareas)}")
    
    # Mostrar información del cronograma mensual si existe
    if st.session_state.cronograma:
        semanas_con_datos = set(asig['semana'] for asig in st.session_state.cronograma.values())
        st.sidebar.markdown(f"**Semanas:** {len(semanas_con_datos)}/4")
        
        # Mostrar algoritmo utilizado
        if st.session_state.usar_algoritmo_mejorado:
            st.sidebar.markdown(f"**Estado:** ✅ Cronograma mejorado generado")
        else:
            st.sidebar.markdown(f"**Estado:** ✅ Cronograma básico generado")
    else:
        st.sidebar.markdown(f"**Estado:** ⏳ Sin cronograma")
    
    # Emergencias activas
    if hasattr(st.session_state, 'emergencias_activas') and st.session_state.emergencias_activas:
        emergencias_criticas = len([e for e in st.session_state.emergencias_activas if e.severidad == "critica"])
        if emergencias_criticas > 0:
            st.sidebar.error(f"🚨 Emergencias críticas: {emergencias_criticas}")
        else:
            st.sidebar.warning(f"⚠️ Emergencias activas: {len(st.session_state.emergencias_activas)}")
    
    # Controles principales
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset"):
            for key in ['roommates', 'tareas', 'cronograma', 'fitness_historia', 'demo_cargada', 
                       'sistema_feedback', 'emergencias_activas', 'intercambios_pendientes']:
                if key == 'cronograma':
                    st.session_state[key] = None
                elif key == 'demo_cargada':
                    st.session_state[key] = False
                elif key in ['sistema_feedback']:
                    st.session_state[key] = None
                else:
                    st.session_state[key] = []
            st.rerun()
    
    with col2:
        if st.button("📝 Demo"):
            num_roommates, num_tareas = cargar_datos_demo_simple()
            st.sidebar.success(f"Demo: {num_roommates} roommates, {num_tareas} tareas")
            st.rerun()
    
    # Configuración del algoritmo
    with st.sidebar.expander("⚙️ Configuración"):
        usar_mejorado = st.checkbox(
            "Usar algoritmo mejorado",
            value=st.session_state.usar_algoritmo_mejorado,
            help="Incluye restricciones médicas, ausencias e incompatibilidades"
        )
        st.session_state.usar_algoritmo_mejorado = usar_mejorado
    
    return paginas[pagina]

def pagina_setup():
    st.header("🔧 Configuración del Sistema")
    mostrar_resumen_demo()
    
    ui = UIComponentsMejorado()
    ui.mostrar_configuracion_roommates()

def pagina_patrones_estudiantiles():
    st.header("🎓 Patrones de Horarios Estudiantiles")
    patron_aplicado = PatronesEstudiantiles.mostrar_selector_patrones()
    
    if patron_aplicado:
        st.success(f"Patrón '{patron_aplicado['patron_nombre']}' listo para aplicar")
        
        # Permitir aplicar a roommate existente o crear nuevo
        if st.session_state.roommates:
            aplicar_a = st.selectbox(
                "Aplicar patrón a:",
                ["Nuevo roommate"] + [rm.nombre for rm in st.session_state.roommates]
            )
            
            if aplicar_a != "Nuevo roommate":
                if st.button("🔄 Actualizar Roommate Existente"):
                    # Actualizar roommate existente
                    for rm in st.session_state.roommates:
                        if rm.nombre == aplicar_a:
                            rm.horarios_disponibles = patron_aplicado['horarios']
                            rm.habilidades = patron_aplicado['habilidades']
                            rm.tiempo_total_disponible = patron_aplicado['tiempo_objetivo']
                            break
                    st.success(f"Patrón aplicado a {aplicar_a}")
                    st.rerun()
            else:
                # Crear nuevo roommate con el patrón
                st.write("### ➕ Crear Nuevo Roommate con Patrón")
                nuevo_nombre = st.text_input("Nombre del nuevo roommate:")
                
                if nuevo_nombre and st.button("✅ Crear Roommate"):
                    if nuevo_nombre.strip() not in [rm.nombre for rm in st.session_state.roommates]:
                        nuevo_roommate = RoommateEnhanced(
                            nombre=nuevo_nombre.strip(),
                            horarios_disponibles=patron_aplicado['horarios'],
                            habilidades=patron_aplicado['habilidades'],
                            preferencias={cat: 'neutro' for cat in patron_aplicado['habilidades'].keys()},
                            tiempo_total_disponible=patron_aplicado['tiempo_objetivo']
                        )
                        st.session_state.roommates.append(nuevo_roommate)
                        st.success(f"Roommate '{nuevo_nombre}' creado con patrón aplicado")
                        st.rerun()
                    else:
                        st.error("Ya existe un roommate con ese nombre")

def pagina_restricciones_medicas():
    st.header("🏥 Gestión de Restricciones Médicas")
    st.markdown("*Configura restricciones específicas para cada roommate*")
    
    if not st.session_state.roommates:
        st.warning("Configura roommates primero")
        return
    
    # Asegurar que todos los roommates sean RoommateEnhanced
    roommates_enhanced = []
    for rm in st.session_state.roommates:
        if isinstance(rm, RoommateEnhanced):
            roommates_enhanced.append(rm)
        else:
            # Convertir a RoommateEnhanced
            rm_enhanced = RoommateEnhanced(
                nombre=rm.nombre,
                horarios_disponibles=rm.horarios_disponibles,
                habilidades=rm.habilidades,
                preferencias=rm.preferencias,
                tiempo_total_disponible=rm.tiempo_total_disponible
            )
            roommates_enhanced.append(rm_enhanced)
    
    st.session_state.roommates = roommates_enhanced
    
    tab1, tab2 = st.tabs(["➕ Agregar Restricción", "📋 Restricciones Existentes"])
    
    with tab1:
        # Formulario para agregar restricción
        roommate_sel = st.selectbox(
            "Roommate:",
            [rm.nombre for rm in st.session_state.roommates]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            categoria_tarea = st.selectbox(
                "Categoría de tarea afectada:",
                ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
            )
            
            tipo_restriccion = st.selectbox(
                "Tipo de restricción:",
                ['alergia', 'limitacion_fisica', 'medica', 'temporal']
            )
        
        with col2:
            severidad = st.selectbox(
                "Severidad:",
                ['prohibido', 'limitado', 'con_ayuda'],
                help="Prohibido: No puede realizar, Limitado: Solo tareas fáciles, Con ayuda: Necesita asistencia"
            )
        
        descripcion = st.text_area(
            "Descripción detallada:",
            placeholder="Ej: Alergia a productos de limpieza químicos, usar solo productos naturales..."
        )
        
        productos_prohibidos = st.text_input(
            "Productos específicos prohibidos (separados por coma):",
            placeholder="Ej: Cloro, Amoniaco, Detergente X"
        )
        
        # Fechas para restricciones temporales
        if tipo_restriccion == 'temporal':
            col1, col2 = st.columns(2)
            with col1:
                fecha_inicio = st.date_input("Fecha inicio:", value=date.today())
            with col2:
                fecha_fin = st.date_input("Fecha fin:", value=date.today() + timedelta(days=30))
        
        if st.button("✅ Agregar Restricción", type="primary"):
            if descripcion.strip():
                roommate_obj = next(rm for rm in st.session_state.roommates if rm.nombre == roommate_sel)
                
                restriccion = RestriccionMedica(
                    categoria_tarea=categoria_tarea,
                    tipo_restriccion=tipo_restriccion,
                    descripcion=descripcion,
                    severidad=severidad,
                    productos_prohibidos=productos_prohibidos.split(',') if productos_prohibidos else [],
                    fecha_inicio=fecha_inicio if tipo_restriccion == 'temporal' else None,
                    fecha_fin=fecha_fin if tipo_restriccion == 'temporal' else None
                )
                
                roommate_obj.restricciones_medicas.append(restriccion)
                st.success("Restricción médica agregada exitosamente")
                st.rerun()
            else:
                st.error("Por favor, proporciona una descripción")
    
    with tab2:
        # Mostrar restricciones existentes
        st.write("### 📋 Restricciones Registradas")
        
        restricciones_encontradas = False
        for roommate in st.session_state.roommates:
            if hasattr(roommate, 'restricciones_medicas') and roommate.restricciones_medicas:
                restricciones_encontradas = True
                with st.expander(f"👤 {roommate.nombre} ({len(roommate.restricciones_medicas)} restricciones)"):
                    for i, restriccion in enumerate(roommate.restricciones_medicas):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            severidad_emoji = {
                                'prohibido': '🚫',
                                'limitado': '⚠️', 
                                'con_ayuda': '🤝'
                            }
                            
                            st.write(f"**{severidad_emoji[restriccion.severidad]} {restriccion.categoria_tarea}** - {restriccion.tipo_restriccion}")
                            st.write(f"📝 {restriccion.descripcion}")
                            
                            if restriccion.productos_prohibidos:
                                st.write(f"🚫 Productos prohibidos: {', '.join(restriccion.productos_prohibidos)}")
                            
                            if restriccion.fecha_inicio and restriccion.fecha_fin:
                                st.write(f"📅 Temporal: {restriccion.fecha_inicio} - {restriccion.fecha_fin}")
                                activa = restriccion.es_activa()
                                st.write(f"Estado: {'🟢 Activa' if activa else '🔴 Inactiva'}")
                        
                        with col2:
                            if st.button("🗑️ Eliminar", key=f"del_rest_{roommate.nombre}_{i}"):
                                roommate.restricciones_medicas.pop(i)
                                st.rerun()
        
        if not restricciones_encontradas:
            st.info("No hay restricciones médicas registradas")

def pagina_espacio():
    st.header("🏠 Características del Espacio")
    mostrar_resumen_demo()
    
    ui = UIComponentsMejorado()
    ui.mostrar_configuracion_espacio()

def pagina_ausencias():
    st.header("🏖️ Gestión de Ausencias")
    
    if not st.session_state.roommates:
        st.warning("Configura roommates primero")
        return
    
    # Asegurar que todos los roommates sean RoommateEnhanced
    roommates_enhanced = []
    for rm in st.session_state.roommates:
        if isinstance(rm, RoommateEnhanced):
            roommates_enhanced.append(rm)
        else:
            rm_enhanced = RoommateEnhanced(
                nombre=rm.nombre,
                horarios_disponibles=rm.horarios_disponibles,
                habilidades=rm.habilidades,
                preferencias=rm.preferencias,
                tiempo_total_disponible=rm.tiempo_total_disponible
            )
            roommates_enhanced.append(rm_enhanced)
    
    st.session_state.roommates = roommates_enhanced
    
    manager = ManagerAusencias(roommates_enhanced)
    manager.mostrar_gestion_ausencias()

def pagina_emergencias():
    st.header("🚨 Gestión de Emergencias")
    
    if not st.session_state.roommates:
        st.warning("Configura roommates primero")
        return
    
    if not st.session_state.cronograma:
        st.info("Ejecuta la optimización primero para poder redistribuir tareas")
    
    manager = ManagerEmergencias(
        st.session_state.cronograma or {}, 
        st.session_state.roommates
    )
    manager.mostrar_gestion_emergencias()

def pagina_optimizar():
    st.header("🧠 Optimización Mensual con Algoritmo Genético")
    
    if st.session_state.usar_algoritmo_mejorado:
        st.markdown("*🔬 **Algoritmo Mejorado**: Considera restricciones médicas, ausencias, incompatibilidades y aprendizaje histórico*")
    else:
        st.markdown("*Genera cronogramas únicos para 4 semanas con intervalos de 30 minutos*")
    
    mostrar_resumen_demo()
    
    if not st.session_state.roommates or not st.session_state.tareas:
        st.error("Configura roommates y tareas primero")
        return
    
    # Verificar que hay tareas de cocina
    tareas_cocina = [t for t in st.session_state.tareas if t.categoria == 'Cocina']
    if not tareas_cocina:
        st.warning("⚠️ No hay tareas de cocina configuradas. Se recomienda agregar tareas de cocina para cumplir el requisito diario.")
    
    # Mostrar información del sistema mejorado
    if st.session_state.usar_algoritmo_mejorado:
        restricciones_totales = 0
        ausencias_totales = 0
        if hasattr(st.session_state.roommates[0], 'restricciones_medicas'):
            restricciones_totales = sum(len(rm.restricciones_medicas) for rm in st.session_state.roommates)
            ausencias_totales = sum(len(rm.ausencias) for rm in st.session_state.roommates)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Roommates", len(st.session_state.roommates))
        with col2:
            st.metric("Restricciones Médicas", restricciones_totales)
        with col3:
            st.metric("Ausencias Registradas", ausencias_totales)
        with col4:
            tareas_cocina_count = len(tareas_cocina)
            st.metric("Tareas de Cocina", tareas_cocina_count)
            if tareas_cocina_count == 0:
                st.caption("⚠️ Requeridas para cumplimiento diario")
    else:
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
        
        if st.session_state.usar_algoritmo_mejorado:
            st.info("💡 **Algoritmo Mejorado**: Respeta restricciones médicas y ausencias automáticamente")
        else:
            st.info("💡 **Intervalos de 30 minutos**: El algoritmo programa tareas en intervalos de media hora para mayor precisión.")
    
    with col2:
        with st.expander("Pesos de optimización"):
            peso_equidad = st.slider("Equidad", 0, 100, 25)
            peso_compatibilidad = st.slider("Compatibilidad", 0, 100, 25)
            peso_habilidades = st.slider("Habilidades", 0, 100, 15)
            peso_preferencias = st.slider("Preferencias", 0, 100, 10)
            peso_rotacion = st.slider("Rotación entre semanas", 0, 100, 10)
            peso_cocina = st.slider("Cocina diaria", 0, 100, 15)
            
            if st.session_state.usar_algoritmo_mejorado:
                st.markdown("**Pesos del Algoritmo Mejorado:**")
                peso_restricciones = st.slider("Restricciones médicas", 0, 100, 30)
                peso_ausencias = st.slider("Ausencias", 0, 100, 25)
                peso_aprendizaje = st.slider("Aprendizaje histórico", 0, 100, 15)
                peso_incompatibilidades = st.slider("Incompatibilidades", 0, 100, 20)
    
    # Verificar si hay datos de aprendizaje
    ajustes_aprendizaje = {}
    if hasattr(st.session_state, 'sistema_feedback') and st.session_state.sistema_feedback:
        ajustes_aprendizaje = st.session_state.sistema_feedback.get_ajustes_sugeridos()
        
        if ajustes_aprendizaje and any(ajustes_aprendizaje.values()):
            st.success("🧠 **Sistema de aprendizaje activo**: Se aplicarán ajustes basados en experiencias previas")
    
    # Advertencias de complejidad
    complejidad = poblacion * generaciones
    if complejidad > 10000:
        st.warning(f"⚠️ Configuración intensiva: {complejidad:,} evaluaciones. Tiempo estimado: 2-5 minutos.")
    elif complejidad > 5000:
        st.info(f"💡 Configuración moderada: {complejidad:,} evaluaciones. Tiempo estimado: 1-2 minutos.")
    else:
        st.success(f"✅ Configuración rápida: {complejidad:,} evaluaciones. Tiempo estimado: <1 minuto.")
    
    # Botón de optimización
    boton_texto = "🚀 Optimizar Cronograma Mensual Mejorado" if st.session_state.usar_algoritmo_mejorado else "🚀 Optimizar Cronograma Mensual"
    
    if st.button(boton_texto, type="primary"):
        with st.spinner(f"Ejecutando algoritmo genético {'mejorado' if st.session_state.usar_algoritmo_mejorado else ''}..."):
            try:
                if st.session_state.usar_algoritmo_mejorado:
                    # Usar algoritmo mejorado
                    ag = AlgoritmoGeneticoMejorado(
                        st.session_state.roommates,
                        st.session_state.tareas,
                        poblacion,
                        generaciones,
                        ajustes_aprendizaje=ajustes_aprendizaje
                    )
                    
                    # Ajustar pesos del algoritmo mejorado
                    ag.ajustar_pesos(
                        equidad=peso_equidad,
                        compatibilidad=peso_compatibilidad,
                        habilidades=peso_habilidades,
                        preferencias=peso_preferencias,
                        rotacion=peso_rotacion,
                        cocina_diaria=peso_cocina,
                        restricciones_medicas=peso_restricciones,
                        ausencias=peso_ausencias,
                        aprendizaje_historico=peso_aprendizaje,
                        incompatibilidades=peso_incompatibilidades
                    )
                else:
                    # Usar algoritmo original
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
                
                algoritmo_usado = "mejorado" if st.session_state.usar_algoritmo_mejorado else "básico"
                st.success(f"¡Optimización {algoritmo_usado} completada!")
                
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
                
                # Verificar violaciones de restricciones si usa algoritmo mejorado
                if st.session_state.usar_algoritmo_mejorado:
                    violaciones = 0
                    roommates_dict = {rm.nombre: rm for rm in st.session_state.roommates}
                    tareas_dict = {t.nombre: t for t in st.session_state.tareas}
                    
                    for asig in mejor.values():
                        roommate_obj = roommates_dict.get(asig['roommate'])
                        tarea_obj = tareas_dict.get(asig['tarea'])
                        
                        if roommate_obj and tarea_obj and hasattr(roommate_obj, 'puede_realizar_tarea'):
                            puede_realizar, motivo = roommate_obj.puede_realizar_tarea(tarea_obj)
                            if not puede_realizar and "Restricción médica" in motivo:
                                violaciones += 1
                    
                    if violaciones == 0:
                        st.success("✅ Sin violaciones de restricciones médicas")
                    else:
                        st.warning(f"⚠️ {violaciones} posibles violaciones de restricciones detectadas")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Error en optimización: {e}")
                import traceback
                with st.expander("Detalles del error (para debugging)"):
                    st.code(traceback.format_exc())
    
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
        ["🗓️ Calendario Visual", "⚠️ Calendario con Conflictos", "📊 Tabla Completa"],
        horizontal=True
    )
    
    if tipo_vista == "🗓️ Calendario Visual":
        crear_calendario_mensual()
    elif tipo_vista == "⚠️ Calendario con Conflictos":
        crear_calendario_mensual_con_conflictos()
    else:
        mostrar_vista_tabla()

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
            # Aquí se podría implementar la re-optimización automática

def pagina_intercambios():
    st.header("🔄 Sistema de Intercambio de Tareas")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        return
    
    # Inicializar el sistema de intercambios en session_state si no existe
    if 'intercambiador' not in st.session_state:
        st.session_state.intercambiador = IntercambiadorTareas(
            st.session_state.cronograma, 
            st.session_state.roommates
        )
    
    st.session_state.intercambiador.mostrar_sistema_intercambios()

def pagina_feedback():
    st.header("📝 Sistema de Feedback y Aprendizaje")
    
    # Inicializar sistema de feedback si no existe
    if not st.session_state.sistema_feedback:
        st.session_state.sistema_feedback = SistemaFeedback()
    
    st.session_state.sistema_feedback.mostrar_sistema_feedback()

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
    st.markdown("### *Sistema Inteligente de Distribución de Tareas Domésticas - Versión Mejorada*")
    
    if st.session_state.usar_algoritmo_mejorado:
        st.markdown("🔬 **Modo Avanzado**: Restricciones médicas • Ausencias • Incompatibilidades • Aprendizaje automático")
    else:
        st.markdown("🕐 **Modo Básico**: Intervalos de 30 minutos • 4 semanas diferentes • Cocina garantizada diariamente")
    
    pagina_ejecutar = mostrar_sidebar()
    pagina_ejecutar()

if __name__ == "__main__":
    main()