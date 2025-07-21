import streamlit as st
import random
from typing import List
from datetime import time
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas, EspacioHogar
from core.student_patterns import PatronesEstudiantiles

class ConfiguracionUI:
    """Interfaz de configuración con rangos de 30 minutos"""
    
    def __init__(self):
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.categorias_tareas = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
        
        # HORARIOS EN INTERVALOS DE 30 MINUTOS
        self.horarios_disponibles = self._generar_horarios_30min()
    
    def _generar_horarios_30min(self):
        """Genera lista de horarios en intervalos de 30 minutos"""
        horarios = []
        for hora in range(6, 24):  # De 6:00 AM a 11:30 PM
            horarios.append(time(hora, 0))      # :00
            horarios.append(time(hora, 30))     # :30
        return horarios

def mostrar_setup():
    """Pantalla principal de configuración"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem;'>🏠 ROOMIETASKAI</h1>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;'>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Roommates", "🍳 Tareas", "🏠 Espacio", "🎲 Demo"])
    
    with tab1:
        _mostrar_configuracion_roommates()
    
    with tab2:
        _mostrar_configuracion_tareas()
    
    with tab3:
        _mostrar_configuracion_espacio()
    
    with tab4:
        _mostrar_demo_rapido()

def _mostrar_configuracion_roommates():
    """Configuración de roommates con horarios de 30 min"""
    st.markdown("### 👥 Configuración de Roommates")
    
    # Opciones de creación
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎓 Crear con Patrón Estudiantil", type="primary", use_container_width=True):
            st.session_state.modo_roommate = "patron"
    
    with col2:
        if st.button("✏️ Crear Manualmente", use_container_width=True):
            st.session_state.modo_roommate = "manual"
    
    # Formulario según modo seleccionado
    if hasattr(st.session_state, 'modo_roommate'):
        if st.session_state.modo_roommate == "patron":
            _formulario_roommate_con_patron()
        else:
            _formulario_roommate_manual()
    
    # Lista de roommates existentes
    if st.session_state.roommates:
        st.markdown("---")
        _mostrar_roommates_existentes()

def _formulario_roommate_con_patron():
    """Formulario usando patrones estudiantiles"""
    st.markdown("#### 🎓 Crear Roommate con Patrón Estudiantil")
    
    patron_aplicado = PatronesEstudiantiles.mostrar_selector_patrones()
    
    if patron_aplicado:
        nombre = st.text_input("Nombre del roommate:", placeholder="Ej: María González")
        
        if nombre and st.button("➕ Agregar Roommate", type="primary"):
            if _validar_nombre_roommate(nombre):
                nuevo_roommate = Roommate(
                    nombre=nombre.strip(),
                    horarios_disponibles=patron_aplicado['horarios'],
                    habilidades=patron_aplicado['habilidades'],
                    preferencias={cat: 'neutro' for cat in patron_aplicado['habilidades'].keys()},
                    tiempo_total_disponible=patron_aplicado['tiempo_objetivo']
                )
                st.session_state.roommates.append(nuevo_roommate)
                st.success(f"✅ {nombre} agregado con patrón '{patron_aplicado['patron_nombre']}'")
                st.rerun()

def _formulario_roommate_manual():
    """Formulario manual con rangos de 30 minutos"""
    st.markdown("#### ✏️ Crear Roommate Manualmente")
    
    nombre = st.text_input("Nombre:", placeholder="Ej: Carlos Pérez")
    tiempo_objetivo = st.number_input("Horas objetivo/semana:", 5, 30, 15)
    
    # CONFIGURACIÓN DE HORARIOS EN INTERVALOS DE 30 MINUTOS
    st.markdown("**📅 Horarios Disponibles (intervalos de 30 min):**")
    horarios = _configurar_horarios_30min()
    
    # Habilidades con sliders visuales
    st.markdown("**🎯 Habilidades (1-10):**")
    habilidades = {}
    cols = st.columns(3)
    for i, categoria in enumerate(['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']):
        with cols[i % 3]:
            habilidades[categoria] = st.slider(
                f"{categoria}:", 1, 10, 5, key=f"hab_{categoria}"
            )
    
    # Preferencias
    st.markdown("**💝 Preferencias:**")
    preferencias = {}
    for categoria in habilidades.keys():
        preferencias[categoria] = st.selectbox(
            f"{categoria}:", 
            ['neutro', 'prefiere', 'evita'], 
            key=f"pref_{categoria}"
        )
    
    # Restricciones médicas
    st.markdown("**🏥 Restricciones Médicas (opcional):**")
    restricciones = st.multiselect(
        "Categorías con restricciones:",
        ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización'],
        help="Selecciona categorías que esta persona no puede realizar por motivos médicos"
    )
    
    # VISTA PREVIA DEL CALENDARIO CON INTERVALOS DE 30 MIN
    if horarios:
        st.markdown("---")
        st.markdown("**👁️ Vista Previa de Horarios (intervalos de 30 min):**")
        _mostrar_calendario_horarios_30min(horarios)
    
    if nombre and horarios and st.button("➕ Crear Roommate", type="primary"):
        if _validar_nombre_roommate(nombre):
            nuevo_roommate = Roommate(
                nombre=nombre.strip(),
                horarios_disponibles=horarios,
                habilidades=habilidades,
                preferencias=preferencias,
                tiempo_total_disponible=tiempo_objetivo,
                restricciones_medicas=restricciones
            )
            st.session_state.roommates.append(nuevo_roommate)
            st.success(f"✅ {nombre} creado exitosamente")
            st.rerun()

def _configurar_horarios_30min():
    """Configuración de horarios en intervalos de 30 minutos"""
    horarios = {}
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Generar opciones de horarios (intervalos de 30 min)
    opciones_horarios = []
    horarios_labels = []
    
    for hora in range(6, 24):
        for minuto in [0, 30]:
            tiempo = time(hora, minuto)
            decimal = hora + (minuto / 60)
            opciones_horarios.append(decimal)
            horarios_labels.append(f"{hora:02d}:{minuto:02d}")
    
    # Opción rápida: mismo horario todos los días
    usar_mismo_horario = st.checkbox("📅 Usar mismo patrón para todos los días")
    
    if usar_mismo_horario:
        st.markdown("**🕐 Configurar patrón base (intervalos de 30 min):**")
        
        # Inicializar horarios base si no existen
        if 'horarios_base_30min' not in st.session_state:
            st.session_state.horarios_base_30min = []
        
        # Selector de horario de inicio y fin
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            idx_inicio = st.selectbox(
                "🕐 Hora inicio:", 
                range(len(horarios_labels)), 
                format_func=lambda x: horarios_labels[x],
                key="inicio_30min"
            )
        
        with col2:
            # Filtrar opciones de fin para que sean posteriores al inicio
            opciones_fin = [(i, label) for i, label in enumerate(horarios_labels) if i > idx_inicio]
            
            if opciones_fin:
                idx_fin = st.selectbox(
                    "🕐 Hora fin:",
                    [x[0] for x in opciones_fin],
                    format_func=lambda x: horarios_labels[x],
                    key="fin_30min"
                )
            else:
                st.warning("⚠️ Selecciona una hora de inicio para ver opciones de fin")
                idx_fin = None
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Agregar", key="agregar_30min"):
                if idx_fin is not None:
                    inicio_decimal = opciones_horarios[idx_inicio]
                    fin_decimal = opciones_horarios[idx_fin]
                    
                    if _validar_rango_30min(inicio_decimal, fin_decimal, st.session_state.horarios_base_30min):
                        nuevo_rango = RangoTiempo(inicio_decimal, fin_decimal)
                        st.session_state.horarios_base_30min.append(nuevo_rango)
                        st.success(f"✅ Rango agregado: {horarios_labels[idx_inicio]} - {horarios_labels[idx_fin]}")
                        st.rerun()
        
        # Mostrar rangos configurados
        if st.session_state.horarios_base_30min:
            st.markdown("**📋 Rangos configurados:**")
            
            for i, rango in enumerate(st.session_state.horarios_base_30min):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    inicio_str = f"{int(rango.inicio):02d}:{int((rango.inicio % 1) * 60):02d}"
                    fin_str = f"{int(rango.fin):02d}:{int((rango.fin % 1) * 60):02d}"
                    duracion = rango.fin - rango.inicio
                    st.write(f"🕐 **{inicio_str} - {fin_str}** ({duracion:.1f}h)")
                
                with col2:
                    if st.button("🗑️", key=f"eliminar_30min_{i}", help="Eliminar rango"):
                        st.session_state.horarios_base_30min.pop(i)
                        st.rerun()
            
            # Aplicar a todos los días
            for dia in dias_semana:
                horarios[dia] = st.session_state.horarios_base_30min.copy()
        
        # Limpiar horarios base
        if st.button("🔄 Limpiar patrones", help="Eliminar todos los rangos configurados"):
            st.session_state.horarios_base_30min = []
            st.rerun()
    
    else:
        # Configuración individual por día
        dias_configurar = st.multiselect(
            "📅 Días a configurar:",
            dias_semana,
            default=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        )
        
        for dia in dias_configurar:
            with st.expander(f"📅 {dia}", expanded=True):
                _configurar_dia_30min(dia, horarios, opciones_horarios, horarios_labels)
    
    return horarios

def _configurar_dia_30min(dia: str, horarios: dict, opciones_horarios: list, horarios_labels: list):
    """Configura horarios para un día específico en intervalos de 30 min"""
    
    # Inicializar horarios del día si no existen
    key_dia = f"horarios_30min_{dia}"
    if key_dia not in st.session_state:
        st.session_state[key_dia] = []
    
    # Formulario para nuevo rango
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        idx_inicio = st.selectbox(
            f"🕐 Inicio", 
            range(len(horarios_labels)), 
            format_func=lambda x: horarios_labels[x],
            key=f"inicio_{dia}_30min"
        )
    
    with col2:
        # Filtrar opciones de fin
        opciones_fin = [(i, label) for i, label in enumerate(horarios_labels) if i > idx_inicio]
        
        if opciones_fin:
            idx_fin = st.selectbox(
                f"🕐 Fin",
                [x[0] for x in opciones_fin],
                format_func=lambda x: horarios_labels[x],
                key=f"fin_{dia}_30min"
            )
        else:
            idx_fin = None
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕", key=f"agregar_{dia}_30min", help="Agregar rango"):
            if idx_fin is not None:
                inicio_decimal = opciones_horarios[idx_inicio]
                fin_decimal = opciones_horarios[idx_fin]
                
                if _validar_rango_30min(inicio_decimal, fin_decimal, st.session_state[key_dia]):
                    nuevo_rango = RangoTiempo(inicio_decimal, fin_decimal)
                    st.session_state[key_dia].append(nuevo_rango)
                    st.success(f"✅ Rango agregado")
                    st.rerun()
    
    # Mostrar rangos del día
    if st.session_state[key_dia]:
        st.markdown(f"**Rangos de {dia}:**")
        
        for i, rango in enumerate(st.session_state[key_dia]):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                inicio_str = f"{int(rango.inicio):02d}:{int((rango.inicio % 1) * 60):02d}"
                fin_str = f"{int(rango.fin):02d}:{int((rango.fin % 1) * 60):02d}"
                duracion = rango.fin - rango.inicio
                st.write(f"🕐 {inicio_str} - {fin_str} ({duracion:.1f}h)")
            
            with col2:
                if st.button("🗑️", key=f"eliminar_{dia}_{i}_30min", help="Eliminar"):
                    st.session_state[key_dia].pop(i)
                    st.rerun()
        
        # Asignar al diccionario final
        horarios[dia] = st.session_state[key_dia].copy()
        
        # Mostrar total de horas del día
        total_horas = sum(rango.fin - rango.inicio for rango in st.session_state[key_dia])
        color = "🟢" if total_horas >= 4 else "🟡" if total_horas >= 2 else "🔴"
        st.caption(f"{color} Total {dia}: {total_horas:.1f} horas")

def _validar_rango_30min(inicio: float, fin: float, rangos_existentes: list) -> bool:
    """Valida rangos en intervalos de 30 minutos"""
    
    # Validar que fin > inicio (ya garantizado por la UI)
    if fin <= inicio:
        st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
        return False
    
    # Validar que sean múltiplos de 0.5 (intervalos de 30 min)
    if inicio % 0.5 != 0 or fin % 0.5 != 0:
        st.error("❌ Solo se permiten intervalos de 30 minutos")
        return False
    
    # Validar que no se solape con rangos existentes
    for rango_existente in rangos_existentes:
        if _rangos_se_solapan(inicio, fin, rango_existente.inicio, rango_existente.fin):
            inicio_str = f"{int(rango_existente.inicio):02d}:{int((rango_existente.inicio % 1) * 60):02d}"
            fin_str = f"{int(rango_existente.fin):02d}:{int((rango_existente.fin % 1) * 60):02d}"
            st.error(f"❌ Se solapa con rango existente: {inicio_str} - {fin_str}")
            return False
    
    return True

def _rangos_se_solapan(inicio1: float, fin1: float, inicio2: float, fin2: float) -> bool:
    """Verifica si dos rangos de tiempo se solapan"""
    return not (fin1 <= inicio2 or fin2 <= inicio1)

def _mostrar_calendario_horarios_30min(horarios: dict):
    """Vista previa de calendario con intervalos de 30 minutos"""
    
    dias_abrev = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    dias_completos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Generar intervalos de 30 minutos
    intervalos = []
    intervalos_decimales = []
    
    for hora in range(6, 24):
        for minuto in [0, 30]:
            intervalos.append(f"{hora:02d}:{minuto:02d}")
            intervalos_decimales.append(hora + minuto/60)
    
    css_calendario_30min = """
    <style>
    .calendario-30min {
        width: 100%;
        margin: 10px 0;
        font-family: 'Segoe UI', sans-serif;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-height: 400px;
        overflow-y: auto;
    }
    
    .calendario-30min table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        font-size: 10px;
    }
    
    .calendario-30min th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 2px;
        text-align: center;
        font-weight: 600;
        font-size: 9px;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .calendario-30min td {
        border: 1px solid #e0e0e0;
        padding: 1px;
        height: 20px;
        text-align: center;
        font-size: 8px;
    }
    
    .hora-col-30min {
        background: #f8f9fa;
        font-weight: 600;
        color: #495057;
        width: 60px;
        font-size: 8px;
        position: sticky;
        left: 0;
        z-index: 5;
    }
    
    .disponible-30min {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        font-weight: 600;
    }
    
    .no-disponible-30min {
        background: #f8f9fa;
    }
    
    .intervalo-inicio {
        border-top: 2px solid #ffc107;
    }
    
    .intervalo-fin {
        border-bottom: 2px solid #ffc107;
    }
    </style>
    """
    
    html_calendario = css_calendario_30min + '<div class="calendario-30min">'
    html_calendario += '<table>'
    
    # Header
    html_calendario += '<tr><th class="hora-col-30min">Hora</th>'
    for dia_abrev in dias_abrev:
        html_calendario += f'<th>{dia_abrev}</th>'
    html_calendario += '</tr>'
    
    # Filas por intervalo de 30 minutos
    for i, (intervalo, tiempo_decimal) in enumerate(zip(intervalos, intervalos_decimales)):
        html_calendario += f'<tr><td class="hora-col-30min">{intervalo}</td>'
        
        for dia_completo in dias_completos:
            # Verificar si este intervalo está disponible
            disponible = False
            es_inicio = False
            es_fin = False
            
            if dia_completo in horarios:
                for rango in horarios[dia_completo]:
                    if rango.inicio <= tiempo_decimal < rango.fin:
                        disponible = True
                        # Verificar si es inicio o fin exacto
                        if abs(rango.inicio - tiempo_decimal) < 0.01:  # Tolerancia para flotantes
                            es_inicio = True
                        if abs(rango.fin - tiempo_decimal - 0.5) < 0.01:  # Siguiente intervalo sería el fin
                            es_fin = True
                        break
            
            # Determinar clases CSS
            clases = []
            if disponible:
                clases.append("disponible-30min")
            else:
                clases.append("no-disponible-30min")
            
            if es_inicio:
                clases.append("intervalo-inicio")
            if es_fin:
                clases.append("intervalo-fin")
            
            clase_final = " ".join(clases)
            contenido = "●" if disponible else ""
            
            html_calendario += f'<td class="{clase_final}" title="{dia_completo} {intervalo}">{contenido}</td>'
        
        html_calendario += '</tr>'
    
    html_calendario += '</table></div>'
    
    st.markdown(html_calendario, unsafe_allow_html=True)
    
    # Mostrar métricas de resumen
    total_horas_semana = 0
    for dia, rangos in horarios.items():
        if rangos:
            total_dia = sum(rango.fin - rango.inicio for rango in rangos)
            total_horas_semana += total_dia
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏰ Horas/Semana", f"{total_horas_semana:.1f}h")
    
    with col2:
        dias_activos = len([d for d, r in horarios.items() if r])
        st.metric("📅 Días Activos", f"{dias_activos}/7")
    
    with col3:
        intervalos_total = int(total_horas_semana * 2)  # Intervalos de 30 min
        st.metric("🕐 Intervalos", f"{intervalos_total}")

def _mostrar_roommates_existentes():
    """Lista de roommates con vista de intervalos de 30 min"""
    st.markdown("### 👥 Roommates Configurados")
    
    for i, roommate in enumerate(st.session_state.roommates):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Información básica
                horas_disponibles = roommate.total_horas_disponibles()
                intervalos_disponibles = int(horas_disponibles * 2)
                
                st.markdown(f"""
                **👤 {roommate.nombre}**  
                ⏰ {horas_disponibles:.1f}h disponibles/semana ({intervalos_disponibles} intervalos de 30min)  
                🎯 Objetivo: {roommate.tiempo_total_disponible}h/semana
                """)
                
                # Habilidades destacadas
                fortalezas = [cat for cat, nivel in roommate.habilidades.items() if nivel >= 7]
                if fortalezas:
                    st.markdown(f"🌟 **Fortalezas:** {', '.join(fortalezas)}")
                
                # Restricciones médicas
                if hasattr(roommate, 'restricciones_medicas') and roommate.restricciones_medicas:
                    st.markdown(f"🏥 **Restricciones:** {', '.join(roommate.restricciones_medicas)}")
            
            with col2:
                if st.button("👁️ Ver Detalles", key=f"ver_{i}"):
                    st.session_state[f"mostrar_detalles_{i}"] = True
            
            with col3:
                if st.button("🗑️ Eliminar", key=f"del_{i}", type="secondary"):
                    st.session_state.roommates.pop(i)
                    st.rerun()
            
            # Mostrar detalles si está expandido
            if st.session_state.get(f"mostrar_detalles_{i}", False):
                _mostrar_detalles_roommate_30min(roommate, i)
            
            st.markdown("---")

def _mostrar_detalles_roommate_30min(roommate: Roommate, index: int):
    """Detalles de roommate con vista de 30 minutos"""
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📅 Calendario 30min", "🎯 Habilidades", "⚙️ Configuración"])
    
    with tab1:
        st.markdown("**📅 Horarios Semanales (intervalos de 30 min):**")
        _mostrar_calendario_roommate_30min(roommate)
    
    with tab2:
        st.markdown("**🎯 Habilidades y Preferencias:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Habilidades:**")
            for categoria, nivel in roommate.habilidades.items():
                color = "🟢" if nivel >= 7 else "🟡" if nivel >= 5 else "🔴"
                # Crear barra de progreso visual
                progreso = "█" * (nivel // 2) + "░" * (5 - nivel // 2)
                st.write(f"{color} **{categoria}:** {progreso} {nivel}/10")
        
        with col2:
            st.markdown("**Preferencias:**")
            for categoria, preferencia in roommate.preferencias.items():
                emoji = "💚" if preferencia == "prefiere" else "❌" if preferencia == "evita" else "➖"
                st.write(f"{emoji} **{categoria}:** {preferencia}")
    
    with tab3:
        st.markdown("**⚙️ Configuración Técnica:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Nombre:** {roommate.nombre}")
            st.write(f"**Tiempo objetivo:** {roommate.tiempo_total_disponible}h/semana")
            horas_reales = roommate.total_horas_disponibles()
            intervalos_reales = int(horas_reales * 2)
            st.write(f"**Tiempo disponible:** {horas_reales:.1f}h/semana ({intervalos_reales} intervalos)")
            
            # Indicador de cumplimiento del objetivo
            if horas_reales >= roommate.tiempo_total_disponible:
                st.success("✅ Cumple tiempo objetivo")
            else:
                deficit = roommate.tiempo_total_disponible - horas_reales
                st.warning(f"⚠️ Faltan {deficit:.1f}h para cumplir objetivo")
        
        with col2:
            if hasattr(roommate, 'restricciones_medicas') and roommate.restricciones_medicas:
                st.markdown("**🏥 Restricciones médicas:**")
                for restriccion in roommate.restricciones_medicas:
                    st.write(f"🚫 {restriccion}")
            else:
                st.info("✅ Sin restricciones médicas")
            
            # Intervalos por día
            st.markdown("**🕐 Intervalos por día:**")
            for dia, rangos in roommate.horarios_disponibles.items():
                if rangos:
                    horas_dia = sum(r.fin - r.inicio for r in rangos)
                    intervalos_dia = int(horas_dia * 2)
                    st.caption(f"{dia}: {intervalos_dia} intervalos")
    
    # Botón para cerrar
    if st.button("❌ Cerrar Detalles", key=f"close_{index}"):
        st.session_state[f"mostrar_detalles_{index}"] = False
        st.rerun()

def _mostrar_calendario_roommate_30min(roommate: Roommate):
    """Calendario completo con intervalos de 30 minutos"""
    
    horarios = roommate.horarios_disponibles
    
    if not horarios or not any(rangos for rangos in horarios.values()):
        st.warning("⚠️ No hay horarios configurados")
        return
    
    # Mostrar vista resumida de intervalos
    st.markdown("**📊 Resumen por intervalos de 30 minutos:**")
    
    total_horas = roommate.total_horas_disponibles()
    total_intervalos = int(total_horas * 2)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏰ Total Horas", f"{total_horas:.1f}h")
    
    with col2:
        st.metric("🕐 Total Intervalos", f"{total_intervalos}")
    
    with col3:
        dias_activos = len([d for d, r in horarios.items() if r])
        promedio_intervalos = total_intervalos / max(dias_activos, 1)
        st.metric("📊 Prom. Intervalos/Día", f"{promedio_intervalos:.1f}")
    
    # Vista de calendario compacta
    _mostrar_calendario_horarios_30min(horarios)
    
    # Desglose por día con intervalos
    st.markdown("**📋 Desglose por Día (intervalos de 30 min):**")
    
    dias_completos = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for dia_completo in dias_completos:
        if dia_completo in horarios and horarios[dia_completo]:
            rangos = horarios[dia_completo]
            total_dia = sum(r.fin - r.inicio for r in rangos)
            intervalos_dia = int(total_dia * 2)
            
            # Formatear rangos en intervalos de 30 min
            rangos_str = []
            for rango in rangos:
                inicio_str = f"{int(rango.inicio):02d}:{int((rango.inicio % 1) * 60):02d}"
                fin_str = f"{int(rango.fin):02d}:{int((rango.fin % 1) * 60):02d}"
                rangos_str.append(f"{inicio_str}-{fin_str}")
            
            emoji_dia = "🟢" if intervalos_dia >= 8 else "🟡" if intervalos_dia >= 4 else "🔴"
            
            st.write(f"{emoji_dia} **{dia_completo}:** {', '.join(rangos_str)} ({intervalos_dia} intervalos)")

# CONFIGURACIÓN DE TAREAS GENERALIZADAS (SIN COMIDAS ESPECÍFICAS)
def _mostrar_configuracion_tareas():
    """Configuración de tareas generalizadas"""
    st.markdown("### 🍳 Configuración de Tareas")
    st.info("🍳 **Nuevo:** Tareas de cocina generalizadas - sin categorías específicas de comidas")
    
    # Selector de nivel de tareas
    nivel_tareas = st.radio(
        "Nivel de tareas:",
        ["🏠 Esenciales Generalizadas", "🏡 Completo Generalizado", "✏️ Personalizado"],
        horizontal=True
    )
    
    if nivel_tareas == "🏠 Esenciales Generalizadas":
        if st.button("✅ Cargar Tareas Esenciales", type="primary"):
            st.session_state.tareas = _get_tareas_esenciales_generalizadas()
            st.success("✅ Tareas esenciales generalizadas cargadas")
            st.rerun()
    
    elif nivel_tareas == "🏡 Completo Generalizado":
        if st.button("✅ Cargar Tareas Completas", type="primary"):
            tareas_completas = (_get_tareas_esenciales_generalizadas() + 
                             _get_tareas_extras_generalizadas())
            st.session_state.tareas = tareas_completas
            st.success("✅ Tareas completas generalizadas cargadas")
            st.rerun()
    
    else:
        _configuracion_tareas_personalizada()
    
    # Mostrar tareas configuradas
    if st.session_state.tareas:
        _mostrar_tareas_configuradas()

def _get_tareas_esenciales_generalizadas():
    """Tareas esenciales con cocina generalizada"""
    return [
        # COCINA GENERALIZADA
        Tarea("Preparar comida", "diaria", 60, 5, "Cocina"),
        Tarea("Cocinar", "diaria", 90, 6, "Cocina"), 
        Tarea("Lavar platos", "diaria", 30, 3, "Cocina"),
        Tarea("Limpiar cocina", "diaria", 30, 4, "Cocina"),
        
        # LIMPIEZA
        Tarea("Aspirar", "semanal", 60, 3, "Limpieza"),
        Tarea("Trapear", "semanal", 60, 4, "Limpieza"),
        Tarea("Limpiar baños", "semanal", 90, 6, "Limpieza"),
        Tarea("Sacudir muebles", "semanal", 30, 2, "Limpieza"),
        
        # LAVANDERÍA
        Tarea("Lavar ropa", "semanal", 120, 3, "Lavandería"),
        Tarea("Tender ropa", "semanal", 30, 2, "Lavandería"),
        
        # COMPRAS
        Tarea("Comprar comestibles", "semanal", 90, 4, "Compras"),
        
        # ORGANIZACIÓN
        Tarea("Ordenar espacios comunes", "semanal", 60, 4, "Organización")
    ]

def _get_tareas_extras_generalizadas():
    """Tareas extras generalizadas"""
    return [
        Tarea("Planchar ropa", "semanal", 60, 5, "Lavandería"),
        Tarea("Limpiar refrigerador", "mensual", 90, 6, "Limpieza"),
        Tarea("Comprar productos limpieza", "mensual", 60, 3, "Compras"),
        Tarea("Organizar despensa", "mensual", 60, 4, "Organización")
    ]

# RESTO DE FUNCIONES SIN CAMBIOS MAYORES...
def _configuracion_tareas_personalizada():
    """Configuración personalizada de tareas"""
    st.markdown("#### ✏️ Configuración Personalizada")
    
    tab1, tab2 = st.tabs(["🏪 Catálogo", "➕ Nueva Tarea"])
    
    with tab1:
        _selector_tareas_catalogo()
    
    with tab2:
        _formulario_tarea_nueva()

def _selector_tareas_catalogo():
    """Selector de tareas del catálogo generalizado"""
    todas_las_tareas = _get_tareas_esenciales_generalizadas() + _get_tareas_extras_generalizadas()
    tareas_actuales = {t.nombre for t in st.session_state.tareas}
    
    st.markdown("**Selecciona tareas del catálogo generalizado:**")
    
    # Agrupar por categoría
    tareas_por_categoria = {}
    for tarea in todas_las_tareas:
        if tarea.categoria not in tareas_por_categoria:
            tareas_por_categoria[tarea.categoria] = []
        tareas_por_categoria[tarea.categoria].append(tarea)
    
    for categoria, tareas in tareas_por_categoria.items():
        with st.expander(f"📁 {categoria} ({len(tareas)} tareas)"):
            for tarea in tareas:
                checked = st.checkbox(
                    f"**{tarea.nombre}** - {tarea.tiempo_estimado}min - Dificultad {tarea.dificultad}/10",
                    value=tarea.nombre in tareas_actuales,
                    key=f"tarea_cat_{tarea.nombre}",
                    help=f"Frecuencia: {tarea.frecuencia}"
                )
                
                if checked and tarea.nombre not in tareas_actuales:
                    st.session_state.tareas.append(tarea)
                elif not checked and tarea.nombre in tareas_actuales:
                    st.session_state.tareas = [t for t in st.session_state.tareas if t.nombre != tarea.nombre]

def _formulario_tarea_nueva():
    """Formulario para crear tarea nueva"""
    st.markdown("**Crear nueva tarea:**")
    
    nombre = st.text_input("Nombre de la tarea:", placeholder="Ej: Preparar merienda")
    
    col1, col2 = st.columns(2)
    with col1:
        categoria = st.selectbox("Categoría:", ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización'])
        frecuencia = st.selectbox("Frecuencia:", ['diaria', 'semanal', 'mensual'])
    
    with col2:
        # TIEMPOS EN MÚLTIPLOS DE 30 MINUTOS
        tiempo = st.selectbox("Duración:", [30, 60, 90, 120, 150, 180, 210, 240], format_func=lambda x: f"{x} min")
        dificultad = st.slider("Dificultad:", 1, 10, 5)
    
    if nombre and st.button("➕ Crear Tarea", type="primary"):
        if _validar_nombre_tarea(nombre):
            nueva_tarea = Tarea(
                nombre=nombre.strip(),
                frecuencia=frecuencia,
                tiempo_estimado=tiempo,
                dificultad=dificultad,
                categoria=categoria,
                es_predeterminada=False
            )
            st.session_state.tareas.append(nueva_tarea)
            st.success(f"✅ Tarea '{nombre}' creada")
            st.rerun()

# RESTO DE FUNCIONES EXISTENTES (sin cambios)...
def _mostrar_configuracion_espacio():
    """Configuración completa del espacio con impacto real"""
    st.markdown("### 🏠 Características del Espacio")
    st.markdown("*Estas características afectan directamente los tiempos de tareas y la rotación*")
    
    # Información básica
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📐 Estructura Básica**")
        habitaciones = st.number_input("Habitaciones:", 1, 10, 
                                     getattr(st.session_state.get('espacio'), 'habitaciones', 2))
        banos = st.number_input("Baños:", 1, 5, 
                               getattr(st.session_state.get('espacio'), 'banos', 1))
        metros = st.number_input("Metros cuadrados:", 30, 500, 
                                getattr(st.session_state.get('espacio'), 'metros_cuadrados', 80))
        pisos = st.number_input("Pisos:", 1, 4, 
                               getattr(st.session_state.get('espacio'), 'pisos', 1))
    
    with col2:
        st.markdown("**🏛️ Espacios Adicionales**")
        tiene_jardin = st.checkbox("🌱 Jardín", 
                                  getattr(st.session_state.get('espacio'), 'tiene_jardin', False))
        tiene_balcon = st.checkbox("🏡 Balcón/Terraza", 
                                  getattr(st.session_state.get('espacio'), 'tiene_balcon', False))
        tiene_garage = st.checkbox("🚗 Garage", 
                                  getattr(st.session_state.get('espacio'), 'tiene_garage', False))
        tiene_lavanderia = st.checkbox("👕 Lavandería dedicada", 
                                      getattr(st.session_state.get('espacio'), 'tiene_lavanderia', False))
        tiene_estudio = st.checkbox("📚 Estudio/Oficina", 
                                   getattr(st.session_state.get('espacio'), 'tiene_estudio', False))
    
    # Equipamiento
    st.markdown("**🔧 Equipamiento Disponible**")
    st.caption("Esto afecta directamente los tiempos de ejecución de tareas")
    
    equipamiento_disponible = [
        "Aspiradora", "Robot aspirador", "Lavadora", "Secadora", "Lavavajillas",
        "Microondas", "Procesador alimentos", "Plancha a vapor", "Pulidora",
        "Hidrolavadora", "Cortacésped", "Manguera jardín"
    ]
    
    equipamiento_actual = getattr(st.session_state.get('espacio'), 'equipamiento', ["Aspiradora", "Lavadora"])
    
    equipamiento = st.multiselect(
        "Selecciona equipamiento:",
        equipamiento_disponible,
        default=equipamiento_actual
    )
    
    # Vista previa del impacto
    st.markdown("---")
    st.markdown("### 📊 Impacto en el Sistema")
    
    # Crear espacio temporal para mostrar preview
    espacio_preview = EspacioHogar(
        habitaciones=habitaciones,
        banos=banos,
        metros_cuadrados=metros,
        pisos=pisos,
        tiene_jardin=tiene_jardin,
        tiene_balcon=tiene_balcon,
        tiene_garage=tiene_garage,
        tiene_lavanderia=tiene_lavanderia,
        tiene_estudio=tiene_estudio,
        equipamiento=equipamiento
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        factor_limpieza = espacio_preview.get_factor_tiempo_limpieza()
        color = "🟢" if factor_limpieza <= 1.2 else "🟡" if factor_limpieza <= 1.6 else "🔴"
        st.metric(f"{color} Factor Limpieza", f"{factor_limpieza:.2f}x")
        st.caption("Multiplica tiempo de tareas de limpieza")
    
    with col2:
        factor_rotacion = espacio_preview.get_factor_rotacion_complejidad()
        color = "🟢" if factor_rotacion <= 1.3 else "🟡" if factor_rotacion <= 1.7 else "🔴"
        st.metric(f"{color} Complejidad Rotación", f"{factor_rotacion:.2f}x")
        st.caption("Aumenta frecuencia de rotación")
    
    with col3:
        tareas_extra = len(espacio_preview.generar_tareas_espaciales())
        st.metric("➕ Tareas Adicionales", tareas_extra)
        st.caption("Tareas específicas del espacio")
    
    # Mostrar tareas que se agregarán
    if tareas_extra > 0:
        with st.expander(f"📋 Ver {tareas_extra} tareas adicionales que se generarán"):
            for tarea in espacio_preview.generar_tareas_espaciales():
                emoji_cat = {'Limpieza': '🧹', 'Mantenimiento': '🔧', 'Organización': '📦'}.get(tarea.categoria, '📋')
                st.write(f"{emoji_cat} **{tarea.nombre}** - {tarea.frecuencia} - {tarea.tiempo_estimado}min")
    
    # Mostrar eficiencia de equipamiento
    if equipamiento:
        with st.expander("⚡ Eficiencia por Equipamiento"):
            for categoria in ['Limpieza', 'Cocina', 'Lavandería']:
                factor = espacio_preview.get_factor_equipamiento(categoria)
                if factor < 1.0:
                    reduccion = (1 - factor) * 100
                    st.success(f"🎯 **{categoria}:** {reduccion:.0f}% menos tiempo")
    
    # Botón para guardar
    if st.button("💾 Guardar Configuración del Espacio", type="primary", use_container_width=True):
        st.session_state.espacio = espacio_preview
        st.success("✅ Espacio configurado correctamente")
        
        # Mostrar resumen del impacto
        with st.container():
            st.info(f"""
            📊 **Resumen del Impacto:**
            • Factor limpieza: **{factor_limpieza:.2f}x** (tiempo de limpieza)
            • Complejidad rotación: **{factor_rotacion:.2f}x** (frecuencia de cambios)  
            • Tareas adicionales: **+{tareas_extra}** tareas específicas
            • Eficiencia equipamiento: Hasta **50%** reducción en tiempos
            """)
        
        st.rerun()

def _mostrar_tareas_configuradas():
    """Lista de tareas configuradas"""
    st.markdown("---")
    st.markdown("### 🍳 Tareas Configuradas (Generalizadas)")
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    tareas_cocina = len([t for t in st.session_state.tareas if t.categoria == 'Cocina'])
    tiempo_total_semanal = sum(t.tiempo_estimado for t in st.session_state.tareas if t.frecuencia != 'mensual')
    intervalos_semanales = int(tiempo_total_semanal / 30)  # Intervalos de 30 min
    
    with col1:
        st.metric("Total Tareas", len(st.session_state.tareas))
    with col2:
        st.metric("Tareas Cocina", tareas_cocina)
        if tareas_cocina == 0:
            st.caption("⚠️ Agregar para cumplir requisito diario")
    with col3:
        st.metric("Tiempo/Semana", f"{tiempo_total_semanal//60}h {tiempo_total_semanal%60}min")
    with col4:
        st.metric("Intervalos 30min", intervalos_semanales)
    
    # Lista detallada
    if len(st.session_state.tareas) > 5:
        with st.expander("📋 Ver lista completa de tareas"):
            _lista_tareas_detallada()
    else:
        _lista_tareas_detallada()

def _lista_tareas_detallada():
    """Lista detallada de tareas"""
    for i, tarea in enumerate(st.session_state.tareas):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            categoria_emoji = {
                'Cocina': '🍳', 'Limpieza': '🧹', 'Lavandería': '👕',
                'Compras': '🛒', 'Mantenimiento': '🔧', 'Organización': '📦'
            }
            emoji = categoria_emoji.get(tarea.categoria, '📋')
            
            dificultad_color = "🟢" if tarea.dificultad <= 3 else "🟡" if tarea.dificultad <= 6 else "🔴"
            intervalos = int(tarea.tiempo_estimado / 30)
            
            st.markdown(f"""
            {emoji} **{tarea.nombre}**  
            📊 {tarea.categoria} • ⏱️ {tarea.tiempo_estimado}min ({intervalos} intervalos) • 📅 {tarea.frecuencia} • {dificultad_color} {tarea.dificultad}/10
            """)
        
        with col2:
            if st.button("🗑️", key=f"del_tarea_{i}", help="Eliminar tarea"):
                st.session_state.tareas.pop(i)
                st.rerun()

def _mostrar_demo_rapido():
    """Demo rápido para pruebas"""
    st.markdown("### 🎲 Demo Rápido")
    st.markdown("Carga datos de ejemplo con **intervalos de 30 minutos** y **cocina generalizada**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎓 Demo Estudiantes (30min):**
        - 3 roommates con horarios en intervalos de 30min
        - Tareas de cocina generalizadas
        - Espacio departamento típico
        - Configuración realista
        """)
        
        if st.button("🎓 Cargar Demo Estudiantes", type="primary", use_container_width=True):
            _cargar_demo_estudiantes_30min()
            st.success("✅ Demo estudiantes cargado (30min)")
            st.rerun()
    
    with col2:
        st.markdown("""
        **🏠 Demo Básico (30min):**
        - 2 roommates simples
        - Tareas básicas generalizadas
        - Espacio pequeño
        - Configuración mínima
        """)
        
        if st.button("🏠 Cargar Demo Básico", use_container_width=True):
            _cargar_demo_basico_30min()
            st.success("✅ Demo básico cargado (30min)")
            st.rerun()

def _cargar_demo_estudiantes_30min():
    """Demo con horarios de 30 minutos y cocina generalizada"""
    # Roommates con horarios en intervalos de 30 min
    roommates_demo = [
        Roommate(
            nombre="Ana María",
            horarios_disponibles={
                'Lunes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                'Martes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                'Miércoles': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                'Jueves': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                'Viernes': [RangoTiempo(6.0, 8.0), RangoTiempo(14.0, 21.0)],
                'Sábado': [RangoTiempo(8.0, 22.0)],
                'Domingo': [RangoTiempo(8.0, 22.0)]
            },
            habilidades={'Limpieza': 7, 'Cocina': 8, 'Lavandería': 6, 'Compras': 5, 'Mantenimiento': 4, 'Organización': 7},
            preferencias={'Limpieza': 'prefiere', 'Cocina': 'prefiere', 'Lavandería': 'neutro', 'Compras': 'evita', 'Mantenimiento': 'evita', 'Organización': 'prefiere'},
            tiempo_total_disponible=15,
            restricciones_medicas=[]
        ),
        Roommate(
            nombre="Carlos Mendez",
            horarios_disponibles={
                'Lunes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                'Martes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                'Miércoles': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                'Jueves': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                'Viernes': [RangoTiempo(6.0, 12.0), RangoTiempo(19.0, 22.0)],
                'Sábado': [RangoTiempo(7.0, 22.0)],
                'Domingo': [RangoTiempo(7.0, 22.0)]
            },
            habilidades={'Limpieza': 5, 'Cocina': 6, 'Lavandería': 8, 'Compras': 7, 'Mantenimiento': 6, 'Organización': 5},
            preferencias={'Limpieza': 'neutro', 'Cocina': 'neutro', 'Lavandería': 'prefiere', 'Compras': 'prefiere', 'Mantenimiento': 'neutro', 'Organización': 'evita'},
            tiempo_total_disponible=16,
            restricciones_medicas=[]
        ),
        Roommate(
            nombre="Sofia Rodriguez",
            horarios_disponibles={
                'Lunes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                'Martes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                'Miércoles': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                'Jueves': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                'Viernes': [RangoTiempo(8.0, 12.0), RangoTiempo(16.0, 20.0)],
                'Sábado': [RangoTiempo(9.0, 21.0)],
                'Domingo': [RangoTiempo(9.0, 21.0)]
            },
            habilidades={'Limpieza': 6, 'Cocina': 5, 'Lavandería': 5, 'Compras': 8, 'Mantenimiento': 7, 'Organización': 8},
            preferencias={'Limpieza': 'neutro', 'Cocina': 'evita', 'Lavandería': 'neutro', 'Compras': 'prefiere', 'Mantenimiento': 'prefiere', 'Organización': 'prefiere'},
            tiempo_total_disponible=18,
            restricciones_medicas=["Limpieza"]  # Alergia a productos químicos
        )
    ]
    
    # Espacio típico de estudiantes
    espacio_demo = EspacioHogar(
        habitaciones=3,
        banos=2,
        metros_cuadrados=90,
        pisos=1,
        tiene_jardin=False,
        tiene_balcon=True,
        tiene_garage=False,
        tiene_lavanderia=False,
        tiene_estudio=False,
        equipamiento=["Aspiradora", "Lavadora", "Microondas"]
    )
    
    st.session_state.roommates = roommates_demo
    st.session_state.tareas = _get_tareas_esenciales_generalizadas()
    st.session_state.espacio = espacio_demo

def _cargar_demo_basico_30min():
    """Demo básico con horarios de 30 min"""
    roommates_basico = [
        Roommate(
            nombre="Alex",
            horarios_disponibles={
                'Lunes': [RangoTiempo(8.0, 20.0)],
                'Martes': [RangoTiempo(8.0, 20.0)],
                'Miércoles': [RangoTiempo(8.0, 20.0)],
                'Jueves': [RangoTiempo(8.0, 20.0)],
                'Viernes': [RangoTiempo(8.0, 20.0)],
                'Sábado': [RangoTiempo(9.0, 21.0)],
                'Domingo': [RangoTiempo(9.0, 21.0)]
            },
            habilidades={'Limpieza': 6, 'Cocina': 5, 'Lavandería': 6, 'Compras': 7, 'Mantenimiento': 5, 'Organización': 6},
            preferencias={'Limpieza': 'neutro', 'Cocina': 'neutro', 'Lavandería': 'neutro', 'Compras': 'prefiere', 'Mantenimiento': 'neutro', 'Organización': 'neutro'},
            tiempo_total_disponible=15,
            restricciones_medicas=[]
        ),
        Roommate(
            nombre="Jordan",
            horarios_disponibles={
                'Lunes': [RangoTiempo(7.0, 19.0)],
                'Martes': [RangoTiempo(7.0, 19.0)],
                'Miércoles': [RangoTiempo(7.0, 19.0)],
                'Jueves': [RangoTiempo(7.0, 19.0)],
                'Viernes': [RangoTiempo(7.0, 19.0)],
                'Sábado': [RangoTiempo(8.0, 22.0)],
                'Domingo': [RangoTiempo(8.0, 22.0)]
            },
            habilidades={'Limpieza': 7, 'Cocina': 6, 'Lavandería': 5, 'Compras': 5, 'Mantenimiento': 6, 'Organización': 7},
            preferencias={'Limpieza': 'prefiere', 'Cocina': 'neutro', 'Lavandería': 'evita', 'Compras': 'neutro', 'Mantenimiento': 'neutro', 'Organización': 'prefiere'},
            tiempo_total_disponible=15,
            restricciones_medicas=[]
        )
    ]
    
    # Espacio básico
    espacio_basico = EspacioHogar(
        habitaciones=2,
        banos=1,
        metros_cuadrados=60,
        pisos=1,
        tiene_jardin=False,
        tiene_balcon=False,
        tiene_garage=False,
        tiene_lavanderia=False,
        tiene_estudio=False,
        equipamiento=["Aspiradora"]
    )
    
    tareas_basicas = _get_tareas_esenciales_generalizadas()[:8]  # Solo 8 tareas
    
    st.session_state.roommates = roommates_basico
    st.session_state.tareas = tareas_basicas
    st.session_state.espacio = espacio_basico

# Funciones de utilidad (sin cambios)
def _validar_nombre_roommate(nombre: str) -> bool:
    """Valida que el nombre del roommate sea único"""
    if not nombre or not nombre.strip():
        st.error("❌ El nombre es requerido")
        return False
    
    nombres_existentes = [rm.nombre.lower() for rm in st.session_state.roommates]
    if nombre.lower().strip() in nombres_existentes:
        st.error(f"❌ Ya existe un roommate con el nombre '{nombre.strip()}'")
        return False
    
    return True

def _validar_nombre_tarea(nombre: str) -> bool:
    """Valida que el nombre de la tarea sea única"""
    if not nombre or not nombre.strip():
        st.error("❌ El nombre de la tarea es requerido")
        return False
    
    nombres_existentes = [t.nombre.lower() for t in st.session_state.tareas]
    if nombre.lower().strip() in nombres_existentes:
        st.error(f"❌ Ya existe una tarea con el nombre '{nombre.strip()}'")
        return False
    
    return True