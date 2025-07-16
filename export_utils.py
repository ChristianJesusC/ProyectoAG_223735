import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO
import streamlit as st
from datetime import datetime

class ExportadorCalendarios:
    
    def __init__(self, cronograma, roommates, tareas):
        self.cronograma = cronograma
        self.roommates = roommates
        self.tareas = tareas
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.colores_roommates = {
            rm.nombre: f"FF{['3498db', 'e74c3c', '2ecc71', 'f39c12', '9b59b6', '1abc9c', '34495e', 'e67e22'][i % 8]}"
            for i, rm in enumerate(roommates)
        }
    
    def exportar_excel_completo(self) -> BytesIO:
        """Exporta el cronograma completo a Excel con múltiples hojas"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Hoja 1: Resumen General
            self._crear_hoja_resumen(writer)
            
            # Hojas 2-5: Una por cada semana
            for semana in [1, 2, 3, 4]:
                self._crear_hoja_semana(writer, semana)
            
            # Hoja 6: Vista por Roommates
            self._crear_hoja_roommates(writer)
            
            # Hoja 7: Estadísticas
            self._crear_hoja_estadisticas(writer)
            
            # Hoja 8: Lista completa de tareas
            self._crear_hoja_lista_tareas(writer)
        
        # Aplicar formato
        self._aplicar_formato_excel(buffer)
        
        buffer.seek(0)
        return buffer
    
    def _crear_hoja_resumen(self, writer):
        """Crea hoja de resumen con vista general del mes"""
        data = []
        
        for key, asig in self.cronograma.items():
            hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
            data.append({
                'ID': key,
                'Semana': f"S{asig['semana']}",
                'Día': asig['dia'],
                'Hora': hora_str,
                'Tarea': asig['tarea'],
                'Roommate': asig['roommate'],
                'Duración (min)': asig['duracion'],
                'Categoría': self._get_categoria_tarea(asig['tarea']),
                'Área': self._get_area_tarea(asig['tarea'])
            })
        
        df_resumen = pd.DataFrame(data)
        df_resumen = df_resumen.sort_values(['Semana', 'Día', 'Hora'])
        
        df_resumen.to_excel(writer, sheet_name='Resumen General', index=False)
    
    def _crear_hoja_semana(self, writer, semana):
        """Crea hoja calendario para una semana específica"""
        # Crear matriz de horarios (intervalos de 30 min)
        intervalos_30min = []
        for h in range(6, 24):
            intervalos_30min.append(f"{h:02d}:00")
            intervalos_30min.append(f"{h:02d}:30")
        
        # Inicializar matriz vacía
        calendario_matriz = pd.DataFrame(
            index=intervalos_30min,
            columns=self.dias_semana
        )
        
        # Llenar matriz con asignaciones
        for asig in self.cronograma.values():
            if asig['semana'] == semana:
                hora_inicio = asig['hora']
                duracion_horas = asig['duracion'] / 60
                
                # Encontrar índices de inicio y fin
                inicio_idx = self._hora_a_indice_30min(hora_inicio)
                fin_idx = inicio_idx + int(duracion_horas * 2)
                
                # Llenar slots ocupados
                for idx in range(inicio_idx, min(fin_idx, len(intervalos_30min))):
                    if 0 <= idx < len(intervalos_30min):
                        dia = asig['dia']
                        if dia in self.dias_semana:
                            valor_actual = calendario_matriz.loc[intervalos_30min[idx], dia]
                            if pd.isna(valor_actual) or valor_actual == '':
                                calendario_matriz.loc[intervalos_30min[idx], dia] = f"{asig['tarea']} ({asig['roommate']})"
                            else:
                                calendario_matriz.loc[intervalos_30min[idx], dia] += f" | {asig['tarea']} ({asig['roommate']})"
        
        # Llenar celdas vacías
        calendario_matriz = calendario_matriz.fillna('')
        
        # Agregar columna de hora como primera columna
        calendario_matriz.insert(0, 'Hora', intervalos_30min)
        
        calendario_matriz.to_excel(writer, sheet_name=f'Semana {semana}', index=False)
    
    def _crear_hoja_roommates(self, writer):
        """Crea hoja con vista por roommates"""
        data_roommates = []
        
        for roommate in self.roommates:
            asignaciones_rm = [asig for asig in self.cronograma.values() 
                             if asig['roommate'] == roommate.nombre]
            
            for asig in asignaciones_rm:
                hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
                data_roommates.append({
                    'Roommate': asig['roommate'],
                    'Semana': f"S{asig['semana']}",
                    'Día': asig['dia'],
                    'Hora': hora_str,
                    'Tarea': asig['tarea'],
                    'Duración (min)': asig['duracion'],
                    'Categoría': self._get_categoria_tarea(asig['tarea']),
                    'Habilidad (1-10)': roommate.get_habilidad(self._get_categoria_tarea(asig['tarea'])),
                    'Preferencia': roommate.get_preferencia(self._get_categoria_tarea(asig['tarea']))
                })
        
        df_roommates = pd.DataFrame(data_roommates)
        df_roommates = df_roommates.sort_values(['Roommate', 'Semana', 'Día', 'Hora'])
        
        df_roommates.to_excel(writer, sheet_name='Por Roommates', index=False)
    
    def _crear_hoja_estadisticas(self, writer):
        """Crea hoja con estadísticas del cronograma"""
        estadisticas = []
        
        # Estadísticas por semana
        for semana in [1, 2, 3, 4]:
            asig_semana = [asig for asig in self.cronograma.values() if asig['semana'] == semana]
            tiempo_total = sum(asig['duracion'] for asig in asig_semana)
            roommates_activos = len(set(asig['roommate'] for asig in asig_semana))
            tareas_totales = len(asig_semana)
            
            # Verificar cocina diaria
            dias_con_cocina = set()
            for asig in asig_semana:
                tarea_obj = next((t for t in self.tareas if t.nombre == asig['tarea']), None)
                if tarea_obj and tarea_obj.categoria == 'Cocina':
                    dias_con_cocina.add(asig['dia'])
            
            estadisticas.append({
                'Semana': f"S{semana}",
                'Total Tareas': tareas_totales,
                'Tiempo Total (min)': tiempo_total,
                'Tiempo Total (horas)': f"{tiempo_total//60}h {tiempo_total%60}min",
                'Roommates Activos': roommates_activos,
                'Días con Cocina': len(dias_con_cocina),
                'Cumplimiento Cocina': f"{len(dias_con_cocina)}/7 ({len(dias_con_cocina)/7*100:.1f}%)"
            })
        
        # Estadísticas por roommate
        stats_roommates = []
        for roommate in self.roommates:
            asig_rm = [asig for asig in self.cronograma.values() if asig['roommate'] == roommate.nombre]
            tiempo_total = sum(asig['duracion'] for asig in asig_rm)
            categorias = set(self._get_categoria_tarea(asig['tarea']) for asig in asig_rm)
            
            stats_roommates.append({
                'Roommate': roommate.nombre,
                'Total Tareas': len(asig_rm),
                'Tiempo Total (min)': tiempo_total,
                'Tiempo Total (horas)': f"{tiempo_total//60}h {tiempo_total%60}min",
                'Categorías Asignadas': len(categorias),
                'Categorías': ', '.join(categorias),
                'Tiempo Objetivo (h/semana)': roommate.tiempo_total_disponible,
                'Cumplimiento Objetivo': f"{(tiempo_total/4)/(roommate.tiempo_total_disponible*60)*100:.1f}%"
            })
        
        # Crear DataFrames
        df_semanas = pd.DataFrame(estadisticas)
        df_roommates = pd.DataFrame(stats_roommates)
        
        # Escribir ambas tablas en la misma hoja
        df_semanas.to_excel(writer, sheet_name='Estadísticas', index=False, startrow=0)
        df_roommates.to_excel(writer, sheet_name='Estadísticas', index=False, startrow=len(df_semanas) + 3)
    
    def _crear_hoja_lista_tareas(self, writer):
        """Crea hoja con lista completa de tareas disponibles"""
        data_tareas = []
        
        for tarea in self.tareas:
            # Contar cuántas veces aparece en el cronograma
            apariciones = len([asig for asig in self.cronograma.values() if asig['tarea'] == tarea.nombre])
            
            data_tareas.append({
                'Tarea': tarea.nombre,
                'Categoría': tarea.categoria,
                'Frecuencia': tarea.frecuencia,
                'Duración (min)': tarea.tiempo_estimado,
                'Dificultad (1-10)': tarea.dificultad,
                'Área': tarea.area_espacio,
                'Apariciones en Cronograma': apariciones,
                'Hora Preferida': f"{int(tarea.hora_preferida):02d}:{int((tarea.hora_preferida % 1) * 60):02d}" if tarea.hora_preferida else 'Flexible',
                'Días Requeridos': ', '.join(tarea.dias_requeridos) if tarea.dias_requeridos else 'Cualquiera',
                'Predeterminada': 'Sí' if tarea.es_predeterminada else 'No'
            })
        
        df_tareas = pd.DataFrame(data_tareas)
        df_tareas = df_tareas.sort_values(['Categoría', 'Tarea'])
        
        df_tareas.to_excel(writer, sheet_name='Lista de Tareas', index=False)
    
    def _aplicar_formato_excel(self, buffer):
        """Aplica formato profesional al archivo Excel"""
        from openpyxl import load_workbook
        
        # Reabrir el archivo para aplicar formato
        buffer.seek(0)
        wb = load_workbook(buffer)
        
        # Formato para headers
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Aplicar formato a todas las hojas
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Formato para header row
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
            
            # Ajustar ancho de columnas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Formato especial para hojas de calendario de semana
            if "Semana" in sheet_name:
                self._aplicar_formato_calendario(ws)
        
        # Guardar cambios
        new_buffer = BytesIO()
        wb.save(new_buffer)
        new_buffer.seek(0)
        return new_buffer
    
    def _aplicar_formato_calendario(self, ws):
        """Aplica formato especial a las hojas de calendario semanal"""
        # Colores para diferentes franjas horarias
        manana_fill = PatternFill(start_color="E8F5E8", end_color="E8F5E8", fill_type="solid")
        tarde_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        noche_fill = PatternFill(start_color="E1F5FE", end_color="E1F5FE", fill_type="solid")
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2), 2):  # Empezar desde fila 2
            hora_cell = row[0]  # Primera columna es la hora
            
            if hora_cell.value:
                hora_str = str(hora_cell.value)
                if ':' in hora_str:
                    hora_num = int(hora_str.split(':')[0])
                    
                    # Aplicar color de fondo según la hora
                    fill_color = None
                    if 6 <= hora_num <= 11:
                        fill_color = manana_fill
                    elif 12 <= hora_num <= 17:
                        fill_color = tarde_fill
                    elif 18 <= hora_num <= 23:
                        fill_color = noche_fill
                    
                    if fill_color:
                        for cell in row:
                            if not cell.fill.start_color.rgb or cell.fill.start_color.rgb == "00000000":
                                cell.fill = fill_color
    
    def _hora_a_indice_30min(self, hora_decimal):
        """Convierte hora decimal a índice en lista de intervalos de 30 min"""
        return int((hora_decimal - 6) * 2)
    
    def _get_categoria_tarea(self, nombre_tarea):
        """Obtiene la categoría de una tarea"""
        tarea = next((t for t in self.tareas if t.nombre == nombre_tarea), None)
        return tarea.categoria if tarea else 'Desconocida'
    
    def _get_area_tarea(self, nombre_tarea):
        """Obtiene el área de una tarea"""
        tarea = next((t for t in self.tareas if t.nombre == nombre_tarea), None)
        return tarea.area_espacio if tarea else 'General'
    
    def exportar_csv_simple(self) -> str:
        """Exporta cronograma a CSV simple"""
        data = []
        for key, asig in self.cronograma.items():
            hora_str = f"{int(asig['hora']):02d}:{int((asig['hora'] % 1) * 60):02d}"
            data.append({
                'Semana': f"S{asig['semana']}",
                'Día': asig['dia'],
                'Hora': hora_str,
                'Tarea': asig['tarea'],
                'Roommate': asig['roommate'],
                'Duración (min)': asig['duracion']
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values(['Semana', 'Día', 'Hora'])
        return df.to_csv(index=False)