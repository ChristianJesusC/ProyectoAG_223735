import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import plotly.graph_objects as go

def mostrar_exportacion():
    """Pantalla de exportación de datos"""
    if not st.session_state.cronograma:
        _mostrar_placeholder_exportacion()
        return
    
    st.markdown("""
    <div style='background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0;'>📊 Exportar Cronograma</h2>
        <p style='color: white; margin: 0; opacity: 0.9;'>
            Descarga tu cronograma en diferentes formatos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Opciones de exportación (SIN PDF)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 CSV Simple
        Ideal para Excel y Google Sheets
        """)
        if st.button("📋 Descargar CSV", type="primary", use_container_width=True):
            _exportar_csv()
    
    with col2:
        st.markdown("""
        ### 📊 Excel Completo
        Múltiples hojas con análisis
        """)
        if st.button("📊 Descargar Excel", type="primary", use_container_width=True):
            _exportar_excel()
    
    # Vista previa de datos
    st.markdown("---")
    _mostrar_vista_previa_datos()

def _mostrar_placeholder_exportacion():
    """Placeholder cuando no hay cronograma"""
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background: #f8f9fa; border-radius: 15px; margin: 2rem 0;'>
        <h2 style='color: #6c757d; margin-bottom: 1rem;'>📊 No hay datos para exportar</h2>
        <p style='color: #6c757d; font-size: 1.1rem;'>
            Genera un cronograma primero en la sección "🧠 Optimizar"
        </p>
    </div>
    """, unsafe_allow_html=True)

def _exportar_csv():
    """Exporta cronograma a CSV simple"""
    try:
        cronograma = st.session_state.cronograma
        
        # Preparar datos
        data = []
        for key, asig in cronograma.items():
            hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
            
            # Obtener categoría de la tarea
            categoria = "General"
            for tarea in st.session_state.tareas:
                if tarea.nombre == asig['tarea']:
                    categoria = tarea.categoria
                    break
            
            data.append({
                'ID': key,
                'Semana': f"S{asig['semana']}",
                'Día': asig['dia'],
                'Hora': hora_str,
                'Tarea': asig['tarea'],
                'Categoría': categoria,
                'Roommate': asig['roommate'],
                'Duración (min)': asig['duracion'],
                'Intervalos_30min': int(asig['duracion'] / 30)
            })
        
        df = pd.DataFrame(data)
        
        # Ordenar por semana, día y hora
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df['Día_Order'] = df['Día'].map(lambda x: orden_dias.index(x))
        df = df.sort_values(['Semana', 'Día_Order', 'Hora']).drop('Día_Order', axis=1)
        
        # Generar CSV
        csv_data = df.to_csv(index=False)
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cronograma_roomietaskai_{timestamp}.csv"
        
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            help="Archivo CSV compatible con Excel y Google Sheets"
        )
        
        st.success("✅ Archivo CSV generado correctamente")
        
    except Exception as e:
        st.error(f"❌ Error al generar CSV: {str(e)}")

def _exportar_excel():
    """Exporta cronograma a Excel con múltiples hojas - CORREGIDO"""
    try:
        with st.spinner("📊 Generando archivo Excel..."):
            # Crear buffer en memoria
            buffer = BytesIO()
            
            # CORREGIDO: Crear Excel completo
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Hoja 1: Resumen General
                _crear_hoja_resumen(writer)
                
                # Hojas 2-5: Calendarios por semana
                for semana in [1, 2, 3, 4]:
                    _crear_hoja_semana(writer, semana)
                
                # Hoja 6: Vista por roommates
                _crear_hoja_roommates(writer)
                
                # Hoja 7: Estadísticas
                _crear_hoja_estadisticas(writer)
                
                # Hoja 8: Catálogo de tareas
                _crear_hoja_tareas(writer)
            
            # Buscar desde el inicio del buffer
            buffer.seek(0)
            
            # Nombre del archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cronograma_completo_{timestamp}.xlsx"
            
            st.download_button(
                label="⬇️ Descargar Excel",
                data=buffer.getvalue(),  # CORREGIDO: usar getvalue()
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Archivo Excel con múltiples hojas y análisis"
            )
            
            st.success("✅ Archivo Excel generado correctamente")
            
            # Mostrar contenido del Excel
            with st.expander("📋 Contenido del archivo Excel", expanded=False):
                st.markdown("""
                **📊 Hojas incluidas:**
                1. **📋 Resumen General** - Todas las asignaciones con intervalos
                2. **📅 Semana 1-4** - Calendarios por semana
                3. **👥 Por Roommates** - Vista por persona
                4. **📈 Estadísticas** - Métricas y análisis
                5. **📋 Catálogo Tareas** - Lista de tareas generalizadas
                """)
    
    except Exception as e:
        st.error(f"❌ Error al generar Excel: {str(e)}")
        st.info("💡 Intenta con menos datos o contacta soporte")

def _crear_hoja_resumen(writer):
    """Crea hoja de resumen general"""
    cronograma = st.session_state.cronograma
    
    data = []
    for key, asig in cronograma.items():
        hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
        
        # Obtener información de la tarea
        categoria = "General"
        dificultad = "N/A"
        for tarea in st.session_state.tareas:
            if tarea.nombre == asig['tarea']:
                categoria = tarea.categoria
                dificultad = f"{tarea.dificultad}/10"
                break
        
        data.append({
            'ID': key,
            'Semana': f"S{asig['semana']}",
            'Día': asig['dia'],
            'Hora': hora_str,
            'Tarea': asig['tarea'],
            'Categoría': categoria,
            'Roommate': asig['roommate'],
            'Duración (min)': asig['duracion'],
            'Intervalos_30min': int(asig['duracion'] / 30),
            'Dificultad': dificultad
        })
    
    df = pd.DataFrame(data)
    
    # Ordenar
    orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    df['Día_Order'] = df['Día'].map(lambda x: orden_dias.index(x))
    df = df.sort_values(['Semana', 'Día_Order', 'Hora']).drop('Día_Order', axis=1)
    
    df.to_excel(writer, sheet_name='Resumen General', index=False)

def _crear_hoja_semana(writer, semana):
    """Crea hoja de calendario para una semana específica"""
    cronograma = st.session_state.cronograma
    
    # Crear matriz de horarios en intervalos de 30 min
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    intervalos = []
    
    # Generar intervalos de 30 minutos
    for h in range(6, 24):
        intervalos.extend([f"{h:02d}:00", f"{h:02d}:30"])
    
    # Crear DataFrame vacío
    calendario_df = pd.DataFrame(index=intervalos, columns=dias)
    
    # Llenar con asignaciones
    for asig in cronograma.values():
        if asig['semana'] == semana:
            hora_inicio = asig['hora']
            duracion_horas = asig['duracion'] / 60
            
            # Calcular slots ocupados (intervalos de 30 min)
            for i, intervalo_str in enumerate(intervalos):
                hora_decimal = 6 + (i * 0.5)
                
                if hora_inicio <= hora_decimal < hora_inicio + duracion_horas:
                    dia = asig['dia']
                    if dia in dias:
                        texto_actual = calendario_df.loc[intervalo_str, dia]
                        nueva_entrada = f"{asig['tarea']} ({asig['roommate']})"
                        
                        if pd.isna(texto_actual):
                            calendario_df.loc[intervalo_str, dia] = nueva_entrada
                        else:
                            calendario_df.loc[intervalo_str, dia] = f"{texto_actual} | {nueva_entrada}"
    
    # Rellenar valores vacíos
    calendario_df = calendario_df.fillna('')
    
    # Resetear index para incluir la columna de horas
    calendario_df.reset_index(inplace=True)
    calendario_df.rename(columns={'index': 'Hora_30min'}, inplace=True)
    
    calendario_df.to_excel(writer, sheet_name=f'Semana {semana}', index=False)

def _crear_hoja_roommates(writer):
    """Crea hoja con vista por roommates"""
    cronograma = st.session_state.cronograma
    
    data = []
    for asig in cronograma.values():
        hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
        
        # Obtener información del roommate
        habilidad = "N/A"
        preferencia = "N/A"
        for roommate in st.session_state.roommates:
            if roommate.nombre == asig['roommate']:
                # Buscar la tarea para obtener su categoría
                for tarea in st.session_state.tareas:
                    if tarea.nombre == asig['tarea']:
                        habilidad = f"{roommate.get_habilidad(tarea.categoria)}/10"
                        preferencia = roommate.get_preferencia(tarea.categoria)
                        break
                break
        
        data.append({
            'Roommate': asig['roommate'],
            'Semana': f"S{asig['semana']}",
            'Día': asig['dia'],
            'Hora': hora_str,
            'Tarea': asig['tarea'],
            'Duración (min)': asig['duracion'],
            'Intervalos_30min': int(asig['duracion'] / 30),
            'Habilidad': habilidad,
            'Preferencia': preferencia
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values(['Roommate', 'Semana', 'Día', 'Hora'])
    
    df.to_excel(writer, sheet_name='Por Roommates', index=False)

def _crear_hoja_estadisticas(writer):
    """Crea hoja con estadísticas del cronograma"""
    cronograma = st.session_state.cronograma
    
    # Estadísticas por semana
    stats_semanas = []
    for semana in [1, 2, 3, 4]:
        asig_semana = [asig for asig in cronograma.values() if asig['semana'] == semana]
        tiempo_total = sum(asig['duracion'] for asig in asig_semana)
        intervalos_total = int(tiempo_total / 30)
        roommates_activos = len(set(asig['roommate'] for asig in asig_semana))
        
        # Verificar cocina diaria
        dias_con_cocina = set()
        for asig in asig_semana:
            for tarea in st.session_state.tareas:
                if tarea.nombre == asig['tarea'] and tarea.categoria == 'Cocina':
                    dias_con_cocina.add(asig['dia'])
                    break
        
        stats_semanas.append({
            'Semana': f"S{semana}",
            'Total Tareas': len(asig_semana),
            'Tiempo Total (min)': tiempo_total,
            'Intervalos_30min': intervalos_total,
            'Tiempo Total (horas)': f"{tiempo_total//60}h {tiempo_total%60}min",
            'Roommates Activos': roommates_activos,
            'Días con Cocina': f"{len(dias_con_cocina)}/7"
        })
    
    # Estadísticas por roommate
    stats_roommates = []
    for roommate in st.session_state.roommates:
        asig_rm = [asig for asig in cronograma.values() if asig['roommate'] == roommate.nombre]
        tiempo_total = sum(asig['duracion'] for asig in asig_rm)
        intervalos_total = int(tiempo_total / 30)
        
        categorias = set()
        for asig in asig_rm:
            for tarea in st.session_state.tareas:
                if tarea.nombre == asig['tarea']:
                    categorias.add(tarea.categoria)
                    break
        
        stats_roommates.append({
            'Roommate': roommate.nombre,
            'Total Tareas': len(asig_rm),
            'Tiempo Total (min)': tiempo_total,
            'Intervalos_30min': intervalos_total,
            'Tiempo Total (horas)': f"{tiempo_total//60}h {tiempo_total%60}min",
            'Categorías': len(categorias),
            'Tiempo Objetivo (h/sem)': roommate.tiempo_total_disponible,
            'Cumplimiento': f"{(tiempo_total/4)/(roommate.tiempo_total_disponible*60)*100:.1f}%"
        })
    
    # Escribir ambas tablas en la misma hoja
    df_semanas = pd.DataFrame(stats_semanas)
    df_roommates = pd.DataFrame(stats_roommates)
    
    # Escribir semanas primero
    df_semanas.to_excel(writer, sheet_name='Estadísticas', index=False, startrow=0)
    
    # Escribir roommates debajo con espacio
    startrow = len(df_semanas) + 3
    df_roommates.to_excel(writer, sheet_name='Estadísticas', index=False, startrow=startrow)

def _crear_hoja_tareas(writer):
    """Crea hoja con catálogo de tareas"""
    data = []
    
    for tarea in st.session_state.tareas:
        # Contar apariciones en cronograma
        apariciones = len([asig for asig in st.session_state.cronograma.values() 
                          if asig['tarea'] == tarea.nombre])
        
        data.append({
            'Tarea': tarea.nombre,
            'Categoría': tarea.categoria,
            'Frecuencia': tarea.frecuencia,
            'Duración (min)': tarea.tiempo_estimado,
            'Intervalos_30min': int(tarea.tiempo_estimado / 30),
            'Dificultad (1-10)': tarea.dificultad,
            'Apariciones en Cronograma': apariciones,
            'Predeterminada': 'Sí' if tarea.es_predeterminada else 'No'
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values(['Categoría', 'Tarea'])
    
    df.to_excel(writer, sheet_name='Catálogo Tareas', index=False)

def _mostrar_vista_previa_datos():
    """Muestra vista previa de los datos a exportar"""
    st.markdown("### 👁️ Vista Previa de Datos")
    
    cronograma = st.session_state.cronograma
    
    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Asignaciones", len(cronograma))
    
    with col2:
        tiempo_total = sum(asig['duracion'] for asig in cronograma.values())
        intervalos_total = int(tiempo_total / 30)
        st.metric("Tiempo Total", f"{tiempo_total//60}h {tiempo_total%60}min")
        st.caption(f"🕐 {intervalos_total} intervalos de 30min")
    
    with col3:
        roommates_activos = len(set(asig['roommate'] for asig in cronograma.values()))
        st.metric("Roommates Activos", roommates_activos)
    
    with col4:
        semanas_cubiertas = len(set(asig['semana'] for asig in cronograma.values()))
        st.metric("Semanas Cubiertas", f"{semanas_cubiertas}/4")
    
    # Gráfico de distribución por categoría
    _grafico_distribucion_categorias(cronograma)

def _grafico_distribucion_categorias(cronograma: dict):
    """Gráfico de distribución por categorías de tareas"""
    categorias_count = {}
    tareas_dict = {t.nombre: t.categoria for t in st.session_state.tareas}
    
    for asig in cronograma.values():
        categoria = tareas_dict.get(asig['tarea'], 'Desconocida')
        categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
    
    if categorias_count:
        fig = go.Figure(data=[
            go.Bar(
                x=list(categorias_count.keys()),
                y=list(categorias_count.values()),
                marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3'],
                text=list(categorias_count.values()),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Distribución de Asignaciones por Categoría",
            xaxis_title="Categorías",
            yaxis_title="Número de Asignaciones",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)