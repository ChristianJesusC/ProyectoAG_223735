import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from models import Roommate, Tarea, RangoTiempo, Asignacion, CronogramaSemanal

class DataUtilsMejorado:
    
    @staticmethod
    def cronograma_a_dataframe(cronograma: Dict) -> pd.DataFrame:
        data = []
        for key, asignacion in cronograma.items():
            hora_fin = asignacion['hora'] + (asignacion['duracion'] / 60)
            data.append({
                'ID': key,
                'Día': asignacion['dia'],
                'Hora Inicio': f"{asignacion['hora']:02d}:00",
                'Hora Fin': f"{int(hora_fin):02d}:{int((hora_fin % 1) * 60):02d}",
                'Tarea': asignacion['tarea'],
                'Roommate': asignacion['roommate'],
                'Duración (min)': asignacion['duracion']
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def calcular_estadisticas_mejoradas(cronograma: Dict, roommates: List[Roommate]) -> Dict:
        cronograma_obj = CronogramaSemanal()
        for key, asig_dict in cronograma.items():
            asignacion = Asignacion(**asig_dict)
            cronograma_obj.agregar_asignacion(key, asignacion)
        
        carga_por_roommate = cronograma_obj.calcular_carga_por_roommate()
        tareas_por_roommate = {rm.nombre: 0 for rm in roommates}
        
        for asignacion in cronograma.values():
            tareas_por_roommate[asignacion['roommate']] += 1
        
        cargas = list(carga_por_roommate.values())
        tiempos_muertos = cronograma_obj.calcular_tiempos_muertos(roommates)
        
        tiempo_muerto_total = sum(tiempos_muertos.values())
        tiempo_trabajo_total = sum(carga_por_roommate.values())
        eficiencia_temporal = tiempo_trabajo_total / (tiempo_trabajo_total + tiempo_muerto_total) * 100 if (tiempo_trabajo_total + tiempo_muerto_total) > 0 else 100
        
        return {
            'carga_por_roommate': carga_por_roommate,
            'tareas_por_roommate': tareas_por_roommate,
            'tiempos_muertos_por_roommate': tiempos_muertos,
            'tiempo_promedio': np.mean(cargas),
            'desviacion_estandar': np.std(cargas),
            'coeficiente_variacion': (np.std(cargas) / np.mean(cargas)) * 100 if np.mean(cargas) > 0 else 0,
            'indice_equidad': max(0, 100 - ((np.std(cargas) / np.mean(cargas)) * 100)) if np.mean(cargas) > 0 else 100,
            'tiempo_muerto_total': tiempo_muerto_total,
            'eficiencia_temporal': eficiencia_temporal
        }
    
    @staticmethod
    def generar_datos_ejemplo_mejorados() -> Tuple[List[Roommate], List[Tarea]]:
        roommate1 = Roommate(
            nombre="Ana",
            horarios_disponibles={
                'Lunes': [RangoTiempo(8, 12), RangoTiempo(18, 22)],
                'Martes': [RangoTiempo(8, 12), RangoTiempo(18, 22)],
                'Miércoles': [RangoTiempo(8, 12), RangoTiempo(18, 22)],
                'Jueves': [RangoTiempo(8, 12), RangoTiempo(18, 22)],
                'Viernes': [RangoTiempo(8, 12), RangoTiempo(18, 22)],
                'Sábado': [RangoTiempo(9, 15), RangoTiempo(19, 23)],
                'Domingo': [RangoTiempo(10, 20)]
            },
            habilidades={'Limpieza': 8, 'Cocina': 6, 'Lavandería': 7, 'Compras': 9, 'Mantenimiento': 4, 'Organización': 8},
            preferencias={'Limpieza': 'prefiere', 'Cocina': 'neutro', 'Lavandería': 'neutro', 'Compras': 'prefiere', 'Mantenimiento': 'evita', 'Organización': 'prefiere'},
            tiempo_total_disponible=20
        )
        
        roommate2 = Roommate(
            nombre="Carlos",
            horarios_disponibles={
                'Lunes': [RangoTiempo(14, 18), RangoTiempo(20, 23)],
                'Martes': [RangoTiempo(14, 18), RangoTiempo(20, 23)],
                'Miércoles': [RangoTiempo(14, 18), RangoTiempo(20, 23)],
                'Jueves': [RangoTiempo(14, 18), RangoTiempo(20, 23)],
                'Viernes': [RangoTiempo(14, 18), RangoTiempo(20, 23)],
                'Sábado': [RangoTiempo(8, 12), RangoTiempo(16, 20)],
                'Domingo': [RangoTiempo(8, 20)]
            },
            habilidades={'Limpieza': 5, 'Cocina': 9, 'Lavandería': 6, 'Compras': 7, 'Mantenimiento': 8, 'Organización': 5},
            preferencias={'Limpieza': 'neutro', 'Cocina': 'prefiere', 'Lavandería': 'neutro', 'Compras': 'neutro', 'Mantenimiento': 'prefiere', 'Organización': 'evita'},
            tiempo_total_disponible=18
        )
        
        roommate3 = Roommate(
            nombre="María",
            horarios_disponibles={
                'Lunes': [RangoTiempo(6, 10), RangoTiempo(16, 19)],
                'Martes': [RangoTiempo(6, 10), RangoTiempo(16, 19)],
                'Miércoles': [RangoTiempo(6, 10), RangoTiempo(16, 19)],
                'Jueves': [RangoTiempo(6, 10), RangoTiempo(16, 19)],
                'Viernes': [RangoTiempo(6, 10), RangoTiempo(16, 19)],
                'Sábado': [RangoTiempo(10, 14), RangoTiempo(18, 22)],
                'Domingo': [RangoTiempo(10, 22)]
            },
            habilidades={'Limpieza': 7, 'Cocina': 8, 'Lavandería': 9, 'Compras': 6, 'Mantenimiento': 6, 'Organización': 9},
            preferencias={'Limpieza': 'neutro', 'Cocina': 'prefiere', 'Lavandería': 'prefiere', 'Compras': 'evita', 'Mantenimiento': 'neutro', 'Organización': 'prefiere'},
            tiempo_total_disponible=22
        )
        
        tareas_ejemplo = [
            Tarea("Lavar platos", "diaria", 30, 3, "Limpieza"),
            Tarea("Cocinar cena", "diaria", 60, 6, "Cocina", hora_preferida=19),
            Tarea("Limpiar baño", "semanal", 90, 7, "Limpieza"),
            Tarea("Aspirar sala", "semanal", 60, 4, "Limpieza"),
            Tarea("Lavar ropa", "semanal", 120, 5, "Lavandería", dias_requeridos=["Sábado", "Domingo"]),
            Tarea("Comprar víveres", "semanal", 120, 6, "Compras", dias_requeridos=["Sábado"]),
            Tarea("Limpiar cocina", "semanal", 60, 5, "Limpieza"),
            Tarea("Organizar espacios", "mensual", 180, 8, "Organización"),
            Tarea("Sacar basura", "diaria", 30, 2, "Limpieza", hora_preferida=20),
            Tarea("Preparar desayuno", "diaria", 30, 4, "Cocina", hora_preferida=7)
        ]
        
        return [roommate1, roommate2, roommate3], tareas_ejemplo