import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas
from genetic_algorithm import AlgoritmoGeneticoOptimizado

from calendar_views import (
    crear_calendario_visual, crear_calendario_mensual, mostrar_calendario_individual,
    mostrar_vista_por_dias, mostrar_vista_tabla, get_roommate_color
)

st.set_page_config(page_title="ROOMIETASKAI", page_icon="🏠", layout="wide")

def init_session():
    defaults = {
        'roommates': [],
        'tareas': [],
        'cronograma': None,
        'fitness_historia': [],
        'form_counter': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def mostrar_sidebar():
    st.sidebar.title("🏠 ROOMIETASKAI")
    st.sidebar.markdown("*Distribución Inteligente de Tareas*")
    
    paginas = {
        "🔧 Setup": pagina_setup,
        "🧠 Optimizar": pagina_optimizar,
        "📅 Cronograma Semanal": pagina_cronograma_semanal,
        "🗓️ Calendario Mensual": pagina_calendario_mensual,
        "📊 Análisis": pagina_analisis
    }
    
    pagina = st.sidebar.selectbox("Navegación", list(paginas.keys()), label_visibility="collapsed")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Roommates:** {len(st.session_state.roommates)}")
    st.sidebar.markdown(f"**Tareas:** {len(st.session_state.tareas)}")
    st.sidebar.markdown(f"**Estado:** {'✅' if st.session_state.cronograma else '⏳'}")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset"):
            for key in ['roommates', 'tareas', 'cronograma', 'fitness_historia']:
                st.session_state[key] = [] if key != 'cronograma' else None
            st.rerun()
    
    with col2:
        if st.button("📝 Demo"):
            cargar_datos_demo()
            st.rerun()
    
    return paginas[pagina]

def cargar_datos_demo():
    roommates_demo = [
        Roommate(
            "Ana",
            {"Lunes": [RangoTiempo(8, 12), RangoTiempo(18, 22)], "Martes": [RangoTiempo(8, 12), RangoTiempo(18, 22)], 
             "Miércoles": [RangoTiempo(8, 12), RangoTiempo(18, 22)], "Jueves": [RangoTiempo(8, 12), RangoTiempo(18, 22)], 
             "Viernes": [RangoTiempo(8, 12), RangoTiempo(18, 22)], "Sábado": [RangoTiempo(9, 15)], "Domingo": [RangoTiempo(10, 20)]},
            {'Limpieza': 8, 'Cocina': 6, 'Lavandería': 7, 'Compras': 9, 'Mantenimiento': 4, 'Organización': 8},
            {'Limpieza': 'prefiere', 'Cocina': 'neutro', 'Lavandería': 'neutro', 'Compras': 'prefiere', 'Mantenimiento': 'evita', 'Organización': 'prefiere'},
            20
        ),
        Roommate(
            "Carlos",
            {"Lunes": [RangoTiempo(14, 18), RangoTiempo(20, 23)], "Martes": [RangoTiempo(14, 18), RangoTiempo(20, 23)], 
             "Miércoles": [RangoTiempo(14, 18), RangoTiempo(20, 23)], "Jueves": [RangoTiempo(14, 18), RangoTiempo(20, 23)], 
             "Viernes": [RangoTiempo(14, 18), RangoTiempo(20, 23)], "Sábado": [RangoTiempo(8, 20)], "Domingo": [RangoTiempo(8, 20)]},
            {'Limpieza': 5, 'Cocina': 9, 'Lavandería': 6, 'Compras': 7, 'Mantenimiento': 8, 'Organización': 5},
            {'Limpieza': 'neutro', 'Cocina': 'prefiere', 'Lavandería': 'neutro', 'Compras': 'neutro', 'Mantenimiento': 'prefiere', 'Organización': 'evita'},
            18
        ),
        Roommate(
            "María",
            {"Lunes": [RangoTiempo(6.5, 10), RangoTiempo(16, 19.5)], "Martes": [RangoTiempo(6.5, 10), RangoTiempo(16, 19.5)], 
             "Miércoles": [RangoTiempo(6.5, 10), RangoTiempo(16, 19.5)], "Jueves": [RangoTiempo(6.5, 10), RangoTiempo(16, 19.5)], 
             "Viernes": [RangoTiempo(6.5, 10), RangoTiempo(16, 19.5)], "Sábado": [RangoTiempo(10, 14)], "Domingo": [RangoTiempo(10, 22)]},
            {'Limpieza': 7, 'Cocina': 8, 'Lavandería': 9, 'Compras': 6, 'Mantenimiento': 6, 'Organización': 9},
            {'Limpieza': 'neutro', 'Cocina': 'prefiere', 'Lavandería': 'prefiere', 'Compras': 'evita', 'Mantenimiento': 'neutro', 'Organización': 'prefiere'},
            22
        )
    ]
    
    st.session_state.roommates = roommates_demo
    st.session_state.tareas = TareasPredeterminadas.get_tareas_basicas()[:10]

def pagina_setup():
    st.header("🔧 Configuración del Sistema")
    
    tab1, tab2 = st.tabs(["👥 Roommates", "📋 Tareas"])
    
    with tab1:
        configurar_roommates()
    
    with tab2:
        configurar_tareas()

def configurar_roommates():
    st.subheader("Roommates")
    
    with st.expander("➕ Agregar Roommate", expanded=True):
        formulario_roommate()
    
    if st.session_state.roommates:
        st.subheader("Registrados")
        for i, rm in enumerate(st.session_state.roommates):
            with st.expander(f"👤 {rm.nombre} - {rm.total_horas_disponibles():.1f}h disponibles"):
                
                vista_tipo = st.radio(
                    f"Vista para {rm.nombre}:",
                    ["📋 Información", "📅 Calendario Individual"],
                    key=f"vista_rm_{i}",
                    horizontal=True
                )
                
                if vista_tipo == "📋 Información":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Horarios:**")
                        for dia, rangos in rm.horarios_disponibles.items():
                            if rangos:
                                horas = ", ".join(str(r) for r in rangos)
                                st.write(f"• {dia}: {horas}")
                    
                    with col2:
                        st.write("**Habilidades:**")
                        for cat, niv in rm.habilidades.items():
                            color = "🟢" if niv >= 8 else "🔵" if niv >= 6 else "🟡" if niv >= 4 else "🔴"
                            st.write(f"{color} {cat}: {niv}/10")
                else:
                    mostrar_calendario_individual(rm)
                
                if st.button(f"🗑️ Eliminar", key=f"del_rm_{i}"):
                    st.session_state.roommates.pop(i)
                    st.rerun()

def formulario_roommate():
    counter = st.session_state.form_counter
    
    nombre = st.text_input("Nombre del roommate", key=f"nombre_{counter}")
    tiempo_obj = st.number_input("Horas objetivo/semana", 5, 50, 15, key=f"tiempo_{counter}")
    
    st.write("**Horarios disponibles (intervalos de 30 min):**")
    horarios = {}
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for dia in dias:
        with st.container():
            st.write(f"**{dia}:**")
            num_rangos = st.number_input(f"Rangos para {dia}", 0, 3, 0, key=f"rangos_{dia}_{counter}")
            
            rangos_dia = []
            for i in range(num_rangos):
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    opciones_hora = []
                    for h in range(5, 24):
                        opciones_hora.append(h)
                        opciones_hora.append(h + 0.5)
                    
                    inicio = st.selectbox(
                        f"Inicio rango {i+1}", 
                        opciones_hora, 
                        index=6, 
                        key=f"ini_{dia}_{i}_{counter}",
                        format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}"
                    )
                
                with col2:
                    opciones_fin = [h for h in opciones_hora if h > inicio]
                    if not opciones_fin:
                        opciones_fin = [24.0]
                    
                    fin = st.selectbox(
                        f"Fin rango {i+1}", 
                        opciones_fin, 
                        index=min(4, len(opciones_fin)-1), 
                        key=f"fin_{dia}_{i}_{counter}",
                        format_func=lambda x: f"{int(x):02d}:{int((x % 1) * 60):02d}" if x < 24 else "24:00"
                    )
                
                with col3:
                    st.write(f"⏱️ {fin-inicio:.1f}h")
                
                try:
                    rangos_dia.append(RangoTiempo(inicio, fin))
                except:
                    st.error("Rango inválido")
            
            if rangos_dia:
                horarios[dia] = rangos_dia
    
    st.write("**Habilidades (1-10):**")
    categorias = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
    habilidades = {}
    preferencias = {}
    
    cols = st.columns(3)
    for i, cat in enumerate(categorias):
        with cols[i % 3]:
            habilidades[cat] = st.slider(f"Habilidad en {cat}", 1, 10, 5, key=f"hab_{cat}_{counter}")
            preferencias[cat] = st.selectbox(f"Preferencia {cat}", ['neutro', 'prefiere', 'evita'], key=f"pref_{cat}_{counter}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Agregar", type="primary"):
            if nombre and horarios:
                try:
                    roommate = Roommate(nombre, horarios, habilidades, preferencias, tiempo_obj)
                    st.session_state.roommates.append(roommate)
                    st.session_state.form_counter += 1
                    st.success(f"Roommate {nombre} agregado")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Completa todos los campos")
    
    with col2:
        if st.button("🗑️ Limpiar"):
            st.session_state.form_counter += 1
            st.rerun()

def configurar_tareas():
    st.subheader("Tareas")
    
    tab1, tab2 = st.tabs(["🏪 Predeterminadas", "✏️ Personalizadas"])
    
    with tab1:
        st.write("### Catálogo de Tareas")
        
        categoria_filtro = st.selectbox("Filtrar por categoría:", ["Todas", "Limpieza", "Cocina", "Lavandería", "Compras", "Mantenimiento", "Organización"])
        
        tareas_basicas = TareasPredeterminadas.get_tareas_basicas()
        if categoria_filtro != "Todas":
            tareas_basicas = [t for t in tareas_basicas if t.categoria == categoria_filtro]
        
        tareas_actuales = {t.nombre for t in st.session_state.tareas}
        
        cols = st.columns(2)
        for i, tarea in enumerate(tareas_basicas):
            with cols[i % 2]:
                checked = st.checkbox(
                    f"**{tarea.nombre}**", 
                    value=tarea.nombre in tareas_actuales,
                    key=f"tarea_{tarea.nombre}"
                )
                
                st.caption(f"📅 {tarea.frecuencia} | ⏱️ {tarea.tiempo_estimado}min | 📊 Dificultad: {tarea.dificultad}/10")
                
                if checked and tarea.nombre not in tareas_actuales:
                    st.session_state.tareas.append(tarea)
                elif not checked and tarea.nombre in tareas_actuales:
                    st.session_state.tareas = [t for t in st.session_state.tareas if t.nombre != tarea.nombre]
    
    with tab2:
        formulario_tarea_personalizada()
    
    if st.session_state.tareas:
        st.subheader("Tareas Seleccionadas")
        
        data = []
        for i, t in enumerate(st.session_state.tareas):
            data.append({
                'Tarea': t.nombre,
                'Frecuencia': t.frecuencia,
                'Tiempo': f"{t.tiempo_estimado}min",
                'Categoría': t.categoria,
                'Tipo': '🏪' if t.es_predeterminada else '✏️'
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        if len(st.session_state.tareas) > 0:
            tarea_eliminar = st.selectbox("Eliminar tarea:", range(len(st.session_state.tareas)), format_func=lambda x: st.session_state.tareas[x].nombre)
            if st.button("🗑️ Eliminar seleccionada"):
                st.session_state.tareas.pop(tarea_eliminar)
                st.rerun()

def formulario_tarea_personalizada():
    st.write("### Crear Tarea Manual")
    
    nombre = st.text_input("Nombre de la tarea")
    
    col1, col2 = st.columns(2)
    with col1:
        categoria = st.selectbox("Categoría", ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización'])
        frecuencia = st.selectbox("Frecuencia", ['diaria', 'semanal', 'mensual'])
    
    with col2:
        tiempo = st.selectbox("Duración", [30, 60, 90, 120, 150, 180, 210, 240], format_func=lambda x: f"{x} min")
        dificultad = st.slider("Dificultad", 1, 10, 5)
    
    if st.button("➕ Agregar tarea personalizada"):
        if nombre:
            try:
                tarea = Tarea(nombre, frecuencia, tiempo, dificultad, categoria, es_predeterminada=False)
                st.session_state.tareas.append(tarea)
                st.success(f"Tarea {nombre} agregada")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Ingresa un nombre")

def pagina_optimizar():
    st.header("🧠 Optimización con Algoritmo Genético")
    
    if not st.session_state.roommates or not st.session_state.tareas:
        st.error("Configura roommates y tareas primero")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Roommates", len(st.session_state.roommates))
    with col2:
        st.metric("Tareas", len(st.session_state.tareas))
    with col3:
        tiempo_total = sum(t.tiempo_estimado * t.get_repeticiones_semanales() for t in st.session_state.tareas)
        st.metric("Tiempo Total", f"{tiempo_total//60}h {tiempo_total%60}min")
    
    st.subheader("Parámetros del Algoritmo")
    col1, col2 = st.columns(2)
    
    with col1:
        poblacion = st.number_input("Población", 10, 1000, 50, step=10, help="Número de cronogramas que compiten simultáneamente")
        generaciones = st.number_input("Generaciones", 5, 200, 30, step=5, help="Número de ciclos evolutivos")
    
    with col2:
        with st.expander("Pesos de optimización"):
            peso_equidad = st.slider("Equidad", 0, 100, 25)
            peso_compatibilidad = st.slider("Compatibilidad", 0, 100, 25)
            peso_habilidades = st.slider("Habilidades", 0, 100, 15)
            peso_preferencias = st.slider("Preferencias", 0, 100, 10)
    
    # Mostrar advertencia para configuraciones intensivas
    if poblacion * generaciones > 10000:
        st.warning(f"⚠️ Configuración intensiva: {poblacion} × {generaciones} = {poblacion * generaciones:,} evaluaciones. Puede tardar varios minutos.")
    elif poblacion * generaciones > 5000:
        st.info(f"💡 Configuración moderada: {poblacion} × {generaciones} = {poblacion * generaciones:,} evaluaciones. Tiempo estimado: 1-2 minutos.")
    
    if st.button("🚀 Optimizar Cronograma", type="primary"):
        with st.spinner(f"Ejecutando algoritmo genético... ({poblacion} individuos × {generaciones} generaciones)"):
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
                    preferencias=peso_preferencias
                )
                
                mejor, historia = ag.ejecutar()
                
                st.session_state.cronograma = mejor
                st.session_state.fitness_historia = historia
                
                st.success("¡Optimización completada!")
                
                # Mostrar estadísticas de la optimización
                if historia:
                    fitness_inicial = historia[0]['mejor']
                    fitness_final = historia[-1]['mejor'] 
                    mejora = ((fitness_final - fitness_inicial) / fitness_inicial * 100) if fitness_inicial > 0 else 0
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Fitness Inicial", f"{fitness_inicial:.3f}")
                    with col2:
                        st.metric("Fitness Final", f"{fitness_final:.3f}")
                    with col3:
                        st.metric("Mejora", f"{mejora:.1f}%")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.fitness_historia:
        st.subheader("📈 Progreso de Optimización")
        
        datos = st.session_state.fitness_historia
        gen = [d['generacion'] for d in datos]
        mejor = [d['mejor'] for d in datos]
        
        fig = px.line(x=gen, y=mejor, title="Evolución del Fitness")
        fig.update_layout(
            xaxis_title="Generación",
            yaxis_title="Fitness",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
def pagina_cronograma_semanal():
    st.header("📅 Cronograma Semanal")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        if st.button("🚀 Ir a Optimización", type="primary"):
            return
        return
    
    tipo_vista = st.radio(
        "Tipo de vista:",
        ["📅 Calendario Visual", "📋 Vista por Días", "📊 Tabla Completa"],
        horizontal=True
    )
    
    if tipo_vista == "📅 Calendario Visual":
        crear_calendario_visual()
    elif tipo_vista == "📋 Vista por Días":
        mostrar_vista_por_dias()
    else:
        mostrar_vista_tabla()
    
    cronograma = st.session_state.cronograma
    data = []
    for key, asig in cronograma.items():
        data.append({
            'Día': asig['dia'],
            'Hora': f"{asig['hora']:02d}:00",
            'Tarea': asig['tarea'],
            'Roommate': asig['roommate'],
            'Duración': f"{asig['duracion']}min"
        })
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    st.download_button("📥 Descargar CSV", csv, "cronograma.csv", "text/csv")

def pagina_calendario_mensual():
    st.header("🗓️ Vista Calendario Mensual")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        if st.button("🚀 Ir a Optimización", type="primary"):
            return
        return
    
    st.info("📅 Vista mensual dividida en 4 semanas con intervalos de 30 minutos")
    crear_calendario_mensual()

def pagina_analisis():
    st.header("📊 Análisis de Resultados")
    
    if not st.session_state.cronograma:
        st.warning("Ejecuta la optimización primero")
        return
    
    cronograma = st.session_state.cronograma
    
    carga = {}
    for asig in cronograma.values():
        rm = asig['roommate']
        carga[rm] = carga.get(rm, 0) + asig['duracion']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        promedio = np.mean(list(carga.values()))
        st.metric("Tiempo Promedio", f"{promedio:.0f}min")
    
    with col2:
        desviacion = np.std(list(carga.values()))
        st.metric("Desviación", f"{desviacion:.0f}min")
    
    with col3:
        equidad = max(0, 100 - (desviacion/promedio*100)) if promedio > 0 else 100
        st.metric("Índice Equidad", f"{equidad:.1f}%")
    
    with col4:
        intervalos_total = sum(carga.values()) // 30
        st.metric("Intervalos 30min", f"{intervalos_total}")
    
    colores_grafico = [get_roommate_color(rm, st.session_state.roommates) for rm in carga.keys()]
    
    fig = px.bar(
        x=list(carga.keys()),
        y=list(carga.values()),
        title="Distribución de Carga de Trabajo (minutos)",
        labels={'x': 'Roommate', 'y': 'Tiempo (min)'},
        color=list(carga.keys()),
        color_discrete_sequence=colores_grafico
    )
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        intervalos_por_rm = {rm: minutos // 30 for rm, minutos in carga.items()}
        fig_intervalos = px.pie(
            values=list(intervalos_por_rm.values()),
            names=list(intervalos_por_rm.keys()),
            title="Distribución de Intervalos de 30min"
        )
        st.plotly_chart(fig_intervalos, use_container_width=True)
    
    with col2:
        if st.session_state.fitness_historia:
            datos = st.session_state.fitness_historia
            gen = [d['generacion'] for d in datos]
            mejor = [d['mejor'] for d in datos]
            
            fig_evol = px.line(x=gen, y=mejor, title="Evolución del Algoritmo")
            st.plotly_chart(fig_evol, use_container_width=True)

def main():
    init_session()
    
    st.title("🏠 ROOMIETASKAI")
    st.markdown("### *Sistema Inteligente de Distribución de Tareas Domésticas*")
    
    pagina_ejecutar = mostrar_sidebar()
    pagina_ejecutar()

if __name__ == "__main__":
    main()