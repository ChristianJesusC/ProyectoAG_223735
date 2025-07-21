import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import date

# Importaciones del sistema
from models import Roommate, Tarea, TareasPredeterminadas, EspacioHogar
from core.genetic_algorithm import AlgoritmoGenetico
from core.student_patterns import PatronesEstudiantiles
from ui.setup import mostrar_setup
from ui.calendar import mostrar_calendario
from ui.export import mostrar_exportacion

# Configuración de la página
st.set_page_config(
    page_title="ROOMIETASKAI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Inicializa el estado de la sesión"""
    defaults = {
        'roommates': [],
        'tareas': [],
        'cronograma': None,
        'fitness_historia': [],
        'espacio': EspacioHogar(),  # Espacio por defecto
        'version': '2.0'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def mostrar_sidebar():
    """Sidebar con navegación y estado del sistema"""
    st.sidebar.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;'>
        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>🏠 ROOMIETASKAI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación principal
    st.sidebar.markdown("### 🧭 Navegación")
    
    paginas = {
        "🔧 Setup": pagina_setup,
        "🎓 Patrones Estudiantiles": pagina_patrones,
        "🧠 Optimizar": pagina_optimizar,
        "🗓️ Calendario": pagina_calendario,
        "📊 Exportar": pagina_exportar
    }
    
    pagina_seleccionada = st.sidebar.selectbox(
        "Ir a:",
        list(paginas.keys()),
        label_visibility="collapsed"
    )
    
    # Estado del sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estado del Sistema")
    
    # Métricas del estado
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("👥 Roommates", len(st.session_state.roommates))
    with col2:
        st.metric("📋 Tareas", len(st.session_state.tareas))
    
    # Estado del cronograma
    if st.session_state.cronograma:
        semanas_generadas = len(set(asig['semana'] for asig in st.session_state.cronograma.values()))
        asignaciones_totales = len(st.session_state.cronograma)
        
        st.sidebar.success(f"✅ Cronograma generado")
        st.sidebar.caption(f"📅 {semanas_generadas}/4 semanas • {asignaciones_totales} asignaciones")
        
        # Verificación rápida de cocina
        tareas_cocina = sum(1 for asig in st.session_state.cronograma.values() 
                           if any(t.nombre == asig['tarea'] and t.categoria == 'Cocina' 
                                 for t in st.session_state.tareas))
        if tareas_cocina > 0:
            st.sidebar.caption(f"🍳 {tareas_cocina} asignaciones de cocina")
    else:
        st.sidebar.warning("⏳ Sin cronograma")
    
    # Estado del espacio
    if hasattr(st.session_state, 'espacio') and st.session_state.espacio:
        espacio = st.session_state.espacio
        factor_complejidad = espacio.get_factor_rotacion_complejidad()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏠 Espacio Configurado")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("🏠 Habitaciones", espacio.habitaciones)
        with col2:
            st.metric("🚿 Baños", espacio.banos)
        
        # Indicador de complejidad espacial
        if factor_complejidad > 1.5:
            st.sidebar.warning(f"🔴 Espacio complejo ({factor_complejidad:.1f}x)")
        elif factor_complejidad > 1.2:
            st.sidebar.info(f"🟡 Espacio moderado ({factor_complejidad:.1f}x)")
        else:
            st.sidebar.success(f"🟢 Espacio simple ({factor_complejidad:.1f}x)")
    
    # Controles rápidos
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Acciones Rápidas")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset", use_container_width=True, help="Reinicia todo el sistema"):
            _reset_sistema()
            st.rerun()
    
    with col2:
        if st.button("🎲 Demo", use_container_width=True, help="Carga datos de ejemplo"):
            _cargar_demo_rapido()
            st.rerun()
    
    # Información adicional con consideración del espacio
    if len(st.session_state.roommates) > 0 and len(st.session_state.tareas) > 0:
        tiempo_total_semanal = sum(t.tiempo_estimado for t in st.session_state.tareas 
                                  if t.frecuencia in ['diaria', 'semanal']) / 60
        tiempo_disponible_total = sum(rm.tiempo_total_disponible for rm in st.session_state.roommates)
        
        # Ajustar por factor espacial si existe
        if hasattr(st.session_state, 'espacio') and st.session_state.espacio:
            factor_limpieza = st.session_state.espacio.get_factor_tiempo_limpieza()
            tiempo_total_semanal *= factor_limpieza
        
        if tiempo_disponible_total > 0:
            carga_sistema = min(100, (tiempo_total_semanal / tiempo_disponible_total) * 100)
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 📈 Carga del Sistema")
            
            if carga_sistema <= 60:
                color = "🟢"
                estado = "Óptima"
            elif carga_sistema <= 80:
                color = "🟡"
                estado = "Moderada"
            else:
                color = "🔴"
                estado = "Alta"
            
            st.sidebar.metric(
                f"{color} Carga {estado}",
                f"{carga_sistema:.0f}%",
                help=f"Relación entre trabajo requerido y tiempo disponible (ajustado por espacio)"
            )
    
    return paginas[pagina_seleccionada]

def _reset_sistema():
    """Reinicia todo el sistema"""
    for key in ['roommates', 'tareas', 'cronograma', 'fitness_historia']:
        if key == 'cronograma':
            st.session_state[key] = None
        else:
            st.session_state[key] = []
    
    # Mantener espacio por defecto
    st.session_state.espacio = EspacioHogar()

def _cargar_demo_rapido():
    """Carga demo rápido para pruebas"""
    from ui.setup import _cargar_demo_estudiantes_30min
    _cargar_demo_estudiantes_30min()

# Páginas de la aplicación
def pagina_setup():
    """Página de configuración"""
    mostrar_setup()

def pagina_patrones():
    """Página de patrones estudiantiles"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0; font-size: 2.2rem;'>🎓 Patrones Estudiantiles</h1>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
            Configuración rápida basada en tu estilo de vida universitario
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    patron_aplicado = PatronesEstudiantiles.mostrar_selector_patrones()
    
    if patron_aplicado:
        st.success(f"✅ Patrón '{patron_aplicado['patron_nombre']}' listo para aplicar")
        
        # Permitir aplicar a roommate existente o crear nuevo
        if st.session_state.roommates:
            aplicar_a = st.selectbox(
                "Aplicar patrón a:",
                ["➕ Nuevo roommate"] + [f"🔄 {rm.nombre}" for rm in st.session_state.roommates]
            )
            
            if aplicar_a.startswith("🔄"):
                roommate_nombre = aplicar_a[2:]  # Remover emoji
                if st.button("🔄 Actualizar Roommate Existente", type="primary"):
                    for rm in st.session_state.roommates:
                        if rm.nombre == roommate_nombre:
                            rm.horarios_disponibles = patron_aplicado['horarios']
                            rm.habilidades = patron_aplicado['habilidades']
                            rm.tiempo_total_disponible = patron_aplicado['tiempo_objetivo']
                            break
                    st.success(f"✅ Patrón aplicado a {roommate_nombre}")
                    st.rerun()
            
            else:
                # Crear nuevo roommate
                nuevo_nombre = st.text_input("Nombre del nuevo roommate:", placeholder="Ej: María González")
                
                if nuevo_nombre and st.button("✅ Crear Roommate con Patrón", type="primary"):
                    if nuevo_nombre.strip() not in [rm.nombre for rm in st.session_state.roommates]:
                        nuevo_roommate = Roommate(
                            nombre=nuevo_nombre.strip(),
                            horarios_disponibles=patron_aplicado['horarios'],
                            habilidades=patron_aplicado['habilidades'],
                            preferencias={cat: 'neutro' for cat in patron_aplicado['habilidades'].keys()},
                            tiempo_total_disponible=patron_aplicado['tiempo_objetivo']
                        )
                        st.session_state.roommates.append(nuevo_roommate)
                        st.success(f"✅ Roommate '{nuevo_nombre}' creado con patrón aplicado")
                        st.rerun()
                    else:
                        st.error("❌ Ya existe un roommate con ese nombre")
        else:
            # No hay roommates, crear el primero
            nuevo_nombre = st.text_input("Nombre del roommate:", placeholder="Ej: María González")
            
            if nuevo_nombre and st.button("✅ Crear Primer Roommate", type="primary"):
                nuevo_roommate = Roommate(
                    nombre=nuevo_nombre.strip(),
                    horarios_disponibles=patron_aplicado['horarios'],
                    habilidades=patron_aplicado['habilidades'],
                    preferencias={cat: 'neutro' for cat in patron_aplicado['habilidades'].keys()},
                    tiempo_total_disponible=patron_aplicado['tiempo_objetivo']
                )
                st.session_state.roommates.append(nuevo_roommate)
                st.success(f"✅ Primer roommate '{nuevo_nombre}' creado")
                st.rerun()

def pagina_optimizar():
    """Página de optimización con algoritmo genético"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0; font-size: 2.2rem;'>🧠 Optimización Inteligente</h1>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;'>
            Algoritmo genético con intervalos de 30 minutos y cocina generalizada
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar prerequisitos
    if not st.session_state.roommates:
        st.error("❌ **Requisito faltante:** Configura al menos 1 roommate en la sección '🔧 Setup'")
        return
    
    if not st.session_state.tareas:
        st.error("❌ **Requisito faltante:** Configura al menos 1 tarea en la sección '🔧 Setup'")
        return
    
    # Verificar tareas de cocina
    tareas_cocina = [t for t in st.session_state.tareas if t.categoria == 'Cocina']
    if not tareas_cocina:
        st.warning("⚠️ **Recomendación:** Agrega tareas de cocina para cumplir el requisito diario")
    
    # Estado actual del sistema
    st.markdown("### 📊 Estado Actual del Sistema")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Roommates", len(st.session_state.roommates))
    
    with col2:
        st.metric("📋 Tareas", len(st.session_state.tareas))
        st.caption(f"🍳 {len(tareas_cocina)} de cocina")
    
    with col3:
        tiempo_total_semanal = sum(t.tiempo_estimado for t in st.session_state.tareas 
                                  if t.frecuencia in ['diaria', 'semanal'])
        intervalos_semanal = int(tiempo_total_semanal / 30)
        st.metric("⏱️ Trabajo/Semana", f"{tiempo_total_semanal//60}h {tiempo_total_semanal%60}min")
        st.caption(f"🕐 {intervalos_semanal} intervalos de 30min")
    
    with col4:
        tiempo_disponible = sum(rm.tiempo_total_disponible for rm in st.session_state.roommates)
        st.metric("🎯 Tiempo Disponible", f"{tiempo_disponible}h/semana")
    
    # ANÁLISIS DEL ESPACIO - NUEVA SECCIÓN
    if hasattr(st.session_state, 'espacio') and st.session_state.espacio:
        st.markdown("---")
        st.markdown("### 🏠 Impacto del Espacio en la Optimización")
        
        espacio = st.session_state.espacio
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            factor_limpieza = espacio.get_factor_tiempo_limpieza()
            color = "🟢" if factor_limpieza <= 1.2 else "🟡" if factor_limpieza <= 1.6 else "🔴"
            st.metric(f"{color} Factor Limpieza", f"{factor_limpieza:.2f}x")
            st.caption("Multiplica tiempo de limpieza")
        
        with col2:
            factor_rotacion = espacio.get_factor_rotacion_complejidad()
            color = "🟢" if factor_rotacion <= 1.3 else "🟡" if factor_rotacion <= 1.7 else "🔴"
            st.metric(f"{color} Complejidad Rotación", f"{factor_rotacion:.2f}x")
            st.caption("Aumenta diversidad requerida")
        
        with col3:
            tareas_extra = len(espacio.generar_tareas_espaciales())
            st.metric("➕ Tareas Extra", f"+{tareas_extra}")
            st.caption("Generadas por el espacio")
        
        with col4:
            # Calcular ahorro por equipamiento
            ahorros = []
            for cat in ['Limpieza', 'Cocina', 'Lavandería']:
                factor = espacio.get_factor_equipamiento(cat)
                if factor < 1.0:
                    ahorros.append((1-factor)*100)
            
            if ahorros:
                ahorro_promedio = sum(ahorros) / len(ahorros)
                st.metric("⚡ Eficiencia Equipos", f"-{ahorro_promedio:.0f}%")
                st.caption("Reducción de tiempo")
            else:
                st.metric("⚡ Eficiencia Equipos", "Estándar")
                st.caption("Sin equipamiento especial")
        
        # Mostrar equipamiento configurado
        if espacio.equipamiento:
            with st.expander("🔧 Equipamiento Configurado", expanded=False):
                cols = st.columns(min(4, len(espacio.equipamiento)))
                for i, equipo in enumerate(espacio.equipamiento):
                    with cols[i % len(cols)]:
                        st.write(f"✅ {equipo}")
    
    else:
        st.warning("⚠️ **Recomendación:** Configura las características del espacio en la sección '🏠 Espacio' para optimización completa")
    
    # Configuración del algoritmo
    st.markdown("---")
    st.markdown("### ⚙️ Configuración del Algoritmo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Parámetros básicos:**")
        poblacion = st.number_input("Población:", 20, 1000, 50, step=10, 
                                   help="Número de soluciones a evaluar simultáneamente")
        generaciones = st.number_input("Generaciones:", 10, 500, 30, step=5,
                                     help="Número de iteraciones del algoritmo")
    
    with col2:
        st.markdown("**Configuración avanzada:**")
        
        # Estimación de tiempo
        complejidad = poblacion * generaciones
        if complejidad > 5000:
            tiempo_estimado = "2-3 minutos"
            color_tiempo = "🔴"
        elif complejidad > 2000:
            tiempo_estimado = "1-2 minutos"
            color_tiempo = "🟡"
        else:
            tiempo_estimado = "< 1 minuto"
            color_tiempo = "🟢"
        
        st.info(f"{color_tiempo} **Tiempo estimado:** {tiempo_estimado}")
        st.caption(f"Complejidad: {complejidad:,} evaluaciones")
        
        # Impacto espacial en el tiempo
        if hasattr(st.session_state, 'espacio') and st.session_state.espacio:
            factor_espacial = st.session_state.espacio.get_factor_rotacion_complejidad()
            if factor_espacial > 1.3:
                st.caption(f"⚡ Espacio complejo: +{(factor_espacial-1)*100:.0f}% tiempo extra")
    
    # PESOS POR DEFECTO (CORREGIDO)
    # Usar pesos por defecto ajustados por espacio
    peso_equidad = 25
    peso_compatibilidad = 25
    peso_habilidades = 20
    peso_cocina = 15
    peso_preferencias = 10
    
    # Peso dinámico de rotación espacial
    if hasattr(st.session_state, 'espacio') and st.session_state.espacio:
        factor_rotacion = st.session_state.espacio.get_factor_rotacion_complejidad()
        peso_rotacion_espacial = int(5 * factor_rotacion)
    else:
        peso_rotacion_espacial = 5
    
    # Pesos del algoritmo (opcional) - INDENTACIÓN CORREGIDA
    with st.expander("🎛️ Ajustar Pesos del Algoritmo (Avanzado)", expanded=False):
        st.markdown("Personaliza la importancia de cada factor en la optimización:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            peso_equidad = st.slider("⚖️ Equidad (distribución justa)", 0, 50, peso_equidad)
            peso_compatibilidad = st.slider("⏰ Compatibilidad horarios", 0, 50, peso_compatibilidad)
            peso_habilidades = st.slider("🎯 Habilidades", 0, 30, peso_habilidades)
        
        with col2:
            peso_cocina = st.slider("🍳 Cocina diaria", 0, 30, peso_cocina)
            peso_preferencias = st.slider("💝 Preferencias", 0, 20, peso_preferencias)
            peso_rotacion_espacial = st.slider("🏠 Rotación espacial", 0, 20, peso_rotacion_espacial)
        
        total_pesos = peso_equidad + peso_compatibilidad + peso_habilidades + peso_cocina + peso_preferencias + peso_rotacion_espacial
        st.caption(f"Total de pesos: {total_pesos} (recomendado: 100)")
        
        if total_pesos != 100:
            st.warning("⚠️ **Advertencia:** La suma de los pesos no es 100. Se aplicarán proporcionalmente.")
    
    # Botón de optimización
    st.markdown("---")
    
    if st.button("🚀 Generar Cronograma Mensual (30min)", type="primary", use_container_width=True):
        with st.spinner("🧬 Ejecutando algoritmo genético con intervalos de 30 minutos..."):
            try:
                # Obtener espacio configurado
                espacio = getattr(st.session_state, 'espacio', EspacioHogar())
                
                # SOLUCIÓN TEMPORAL - CREAR ALGORITMO SIN PARÁMETRO ESPACIO
                algoritmo = AlgoritmoGenetico(
                    roommates=st.session_state.roommates,
                    tareas=st.session_state.tareas,
                    tam_poblacion=poblacion,
                    generaciones=generaciones
                )
                
                # Aplicar espacio después de crear el algoritmo (si tiene los métodos)
                if hasattr(algoritmo, 'espacio'):
                    algoritmo.espacio = espacio
                
                # Aplicar pesos personalizados
                algoritmo.pesos = {
                    'equidad': peso_equidad,
                    'compatibilidad': peso_compatibilidad,
                    'habilidades': peso_habilidades,
                    'cocina_diaria': peso_cocina,
                    'preferencias': peso_preferencias,
                    'rotacion_espacial': peso_rotacion_espacial
                }
                
                # Ejecutar optimización
                mejor_cronograma, historia_fitness = algoritmo.ejecutar()
                
                # Guardar resultados
                st.session_state.cronograma = mejor_cronograma
                st.session_state.fitness_historia = historia_fitness
                
                st.success("🎉 ¡Cronograma generado exitosamente con intervalos de 30 minutos!")
                
                # Mostrar resultados CON ANÁLISIS ESPACIAL
                _mostrar_resultados_optimizacion_espacial(mejor_cronograma, historia_fitness, espacio)
                
            except Exception as e:
                st.error(f"❌ Error durante la optimización: {str(e)}")
                st.info("💡 Intenta con parámetros más conservadores (población: 30, generaciones: 20)")

def _mostrar_resultados_optimizacion_espacial(cronograma: dict, historia: list, espacio: EspacioHogar):
    """Muestra resultados incluyendo impacto espacial"""
    st.markdown("### 🎯 Resultados de la Optimización")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Asignaciones", len(cronograma))
    
    with col2:
        semanas_generadas = len(set(asig['semana'] for asig in cronograma.values()))
        st.metric("📅 Semanas", f"{semanas_generadas}/4")
    
    with col3:
        if historia:
            fitness_final = historia[-1]['mejor']
            st.metric("🎯 Fitness Final", f"{fitness_final:.3f}")
        else:
            st.metric("🎯 Fitness Final", "N/A")
    
    with col4:
        tiempo_total = sum(asig['duracion'] for asig in cronograma.values())
        intervalos_total = int(tiempo_total / 30)
        st.metric("⏱️ Tiempo Total", f"{tiempo_total//60}h {tiempo_total%60}min")
        st.caption(f"🕐 {intervalos_total} intervalos de 30min")
    
    # ANÁLISIS DEL IMPACTO ESPACIAL - NUEVA SECCIÓN
    if hasattr(espacio, 'generar_tareas_espaciales'):
        st.markdown("---")
        st.markdown("### 🏠 Análisis del Impacto Espacial")
        
        # Identificar tareas generadas por el espacio
        tareas_espaciales_nombres = [t.nombre for t in espacio.generar_tareas_espaciales()]
        tareas_espaciales = [asig for asig in cronograma.values() 
                            if asig['tarea'] in tareas_espaciales_nombres]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏠 Tareas Espaciales", len(tareas_espaciales))
            if tareas_espaciales:
                tiempo_espacial = sum(asig['duracion'] for asig in tareas_espaciales)
                st.caption(f"Tiempo: {tiempo_espacial//60}h {tiempo_espacial%60}min")
        
        with col2:
            # Calcular eficiencias obtenidas
            ahorros_reales = []
            for categoria in ['Limpieza', 'Cocina', 'Lavandería']:
                factor = espacio.get_factor_equipamiento(categoria)
                if factor < 1.0:
                    # Calcular tiempo ahorrado en esta categoría
                    tareas_categoria = [asig for asig in cronograma.values() 
                                      if any(t.nombre == asig['tarea'] and t.categoria == categoria 
                                            for t in st.session_state.tareas)]
                    tiempo_categoria = sum(asig['duracion'] for asig in tareas_categoria)
                    ahorro = tiempo_categoria * (1 - factor)
                    ahorros_reales.append(ahorro)
            
            if ahorros_reales:
                ahorro_total = sum(ahorros_reales)
                st.metric("⚡ Tiempo Ahorrado", f"{ahorro_total//60}h {int(ahorro_total%60)}min")
                st.caption("Por equipamiento eficiente")
            else:
                st.metric("⚡ Tiempo Ahorrado", "0min")
                st.caption("Sin equipamiento especial")
        
        with col3:
            # Factor de complejidad aplicado
            factor_rotacion = espacio.get_factor_rotacion_complejidad()
            color_factor = "🟢" if factor_rotacion <= 1.3 else "🟡" if factor_rotacion <= 1.7 else "🔴"
            st.metric(f"{color_factor} Factor Aplicado", f"{factor_rotacion:.2f}x")
            st.caption("Complejidad espacial")
    
    # Verificación de cocina diaria
    st.markdown("---")
    st.markdown("### 🍳 Verificación de Cocina Diaria")
    
    tareas_cocina_asignadas = 0
    dias_con_cocina = set()
    
    for asig in cronograma.values():
        for tarea in st.session_state.tareas:
            if tarea.nombre == asig['tarea'] and tarea.categoria == 'Cocina':
                tareas_cocina_asignadas += 1
                dias_con_cocina.add(f"S{asig['semana']}_{asig['dia']}")
                break
    
    cumplimiento_cocina = (len(dias_con_cocina) / 28) * 100  # 28 días en 4 semanas
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🍳 Días con Cocina", f"{len(dias_con_cocina)}/28")
    
    with col2:
        st.metric("📊 Cumplimiento", f"{cumplimiento_cocina:.0f}%")
    
    with col3:
        if cumplimiento_cocina >= 90:
            st.success("✅ Excelente cumplimiento")
        elif cumplimiento_cocina >= 70:
            st.warning("⚠️ Cumplimiento aceptable")
        else:
            st.error("❌ Cumplimiento deficiente")
    
    # Mostrar eficiencias específicas por categoría
    if hasattr(espacio, 'get_factor_equipamiento'):
        st.markdown("---")
        st.markdown("### ⚡ Eficiencias por Equipamiento")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            factor_limpieza = espacio.get_factor_equipamiento('Limpieza')
            if factor_limpieza < 1.0:
                st.success(f"🧹 **Limpieza:** {(1-factor_limpieza)*100:.0f}% más eficiente")
                if "Robot aspirador" in espacio.equipamiento:
                    st.caption("🤖 Robot aspirador: -40% tiempo")
                elif "Aspiradora" in espacio.equipamiento:
                    st.caption("🌪️ Aspiradora: -20% tiempo")
            else:
                st.info("🧹 **Limpieza:** Tiempo estándar")
        
        with col2:
            factor_cocina = espacio.get_factor_equipamiento('Cocina')
            if factor_cocina < 1.0:
                st.success(f"🍳 **Cocina:** {(1-factor_cocina)*100:.0f}% más eficiente")
                if "Lavavajillas" in espacio.equipamiento:
                    st.caption("🍽️ Lavavajillas: -50% tiempo")
                if "Microondas" in espacio.equipamiento:
                    st.caption("⚡ Microondas: -10% tiempo")
            else:
                st.info("🍳 **Cocina:** Tiempo estándar")
        
        with col3:
            factor_lavanderia = espacio.get_factor_equipamiento('Lavandería')
            if factor_lavanderia < 1.0:
                st.success(f"👕 **Lavandería:** {(1-factor_lavanderia)*100:.0f}% más eficiente")
                if "Secadora" in espacio.equipamiento:
                    st.caption("🌪️ Secadora: -40% tiempo")
                if "Lavadora" in espacio.equipamiento:
                    st.caption("🌊 Lavadora: -30% tiempo")
            else:
                st.info("👕 **Lavandería:** Tiempo estándar")
    
    # Gráfico de evolución del fitness
    if historia and len(historia) > 1:
        st.markdown("---")
        st.markdown("### 📈 Evolución del Algoritmo")
        
        df_historia = pd.DataFrame(historia)
        
        fig = px.line(df_historia, x='generacion', y=['mejor', 'promedio'],
                     title="Evolución del Fitness Durante la Optimización con Intervalos 30min",
                     labels={'value': 'Fitness', 'generacion': 'Generación'})
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas de mejora
        mejora = ((historia[-1]['mejor'] - historia[0]['mejor']) / historia[0]['mejor'] * 100) if historia[0]['mejor'] > 0 else 0
        st.caption(f"📊 Mejora del fitness: {mejora:.1f}% en {len(historia)} generaciones con optimización espacial y intervalos de 30min")

def pagina_calendario():
    """Página del calendario"""
    mostrar_calendario()

def pagina_exportar():
    """Página de exportación"""
    mostrar_exportacion()

def main():
    """Función principal de la aplicación"""
    # Inicializar estado
    init_session_state()
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    
    .stMetric {
        background-color: white;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    
    .stAlert {
        border-radius: 0.5rem;
    }
    
    .stButton > button {
        border-radius: 0.5rem;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar aplicación
    pagina_ejecutar = mostrar_sidebar()
    
    # Ejecutar página seleccionada
    pagina_ejecutar()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6c757d; padding: 1rem;'>
        <p>🏠 <strong>ROOMIETASKAI </strong> • Sistema con Intervalos de 30 Minutos</p>
        <p style='font-size: 0.8rem;'>Algoritmo genético optimizado para horarios realistas y cocina generalizada</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()