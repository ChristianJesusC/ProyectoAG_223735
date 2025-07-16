from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import numpy as np

@dataclass
class RangoTiempo:
    inicio: float
    fin: float
    
    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("La hora de inicio debe ser menor que la de fin")
        if not (0 <= self.inicio <= 24) or not (0 <= self.fin <= 24):
            raise ValueError("Las horas deben estar entre 0 y 24")
        
        # Redondear a intervalos de 30 minutos
        self.inicio = round(self.inicio * 2) / 2
        self.fin = round(self.fin * 2) / 2
    
    def duracion_horas(self) -> float:
        return self.fin - self.inicio
    
    def contiene_hora(self, hora: float) -> bool:
        return self.inicio <= hora < self.fin
    
    def get_intervalos_30min(self) -> List[float]:
        """Devuelve lista de intervalos de 30 minutos en este rango"""
        intervalos = []
        hora_actual = self.inicio
        while hora_actual < self.fin:
            intervalos.append(hora_actual)
            hora_actual += 0.5
        return intervalos
    
    def __str__(self):
        def format_hora(h):
            horas = int(h)
            minutos = int((h % 1) * 60)
            return f"{horas:02d}:{minutos:02d}"
        return f"{format_hora(self.inicio)} - {format_hora(self.fin)}"

@dataclass
class Roommate:
    nombre: str
    horarios_disponibles: Dict[str, List[RangoTiempo]]
    habilidades: Dict[str, int]
    preferencias: Dict[str, str]
    tiempo_total_disponible: int
    
    def __post_init__(self):
        if self.tiempo_total_disponible <= 0:
            raise ValueError("El tiempo total disponible debe ser mayor a 0")
        
        for habilidad, nivel in self.habilidades.items():
            if not 1 <= nivel <= 10:
                raise ValueError(f"El nivel de habilidad para {habilidad} debe estar entre 1 y 10")
    
    def esta_disponible(self, dia: str, hora: float) -> bool:
        if dia not in self.horarios_disponibles:
            return False
        return any(rango.contiene_hora(hora) for rango in self.horarios_disponibles[dia])
    
    def get_intervalos_disponibles_30min(self, dia: str) -> List[float]:
        """Obtiene todos los intervalos de 30 minutos disponibles para un día"""
        if dia not in self.horarios_disponibles:
            return []
        
        intervalos = []
        for rango in self.horarios_disponibles[dia]:
            intervalos.extend(rango.get_intervalos_30min())
        
        return sorted(list(set(intervalos)))  # Eliminar duplicados y ordenar
    
    def get_habilidad(self, tarea: str) -> int:
        return self.habilidades.get(tarea, 5)
    
    def get_preferencia(self, tarea: str) -> str:
        return self.preferencias.get(tarea, 'neutro')
    
    def total_horas_disponibles(self) -> float:
        total = 0
        for dia, rangos in self.horarios_disponibles.items():
            for rango in rangos:
                total += rango.duracion_horas()
        return total

@dataclass
class Tarea:
    nombre: str
    frecuencia: str
    tiempo_estimado: int
    dificultad: int
    categoria: str
    dias_requeridos: List[str] = field(default_factory=list)
    hora_preferida: float = None
    es_predeterminada: bool = False
    area_espacio: str = "General"
    
    def __post_init__(self):
        frecuencias_validas = ['diaria', 'semanal', 'mensual']
        if self.frecuencia not in frecuencias_validas:
            raise ValueError(f"Frecuencia debe ser una de: {frecuencias_validas}")
        
        if not 1 <= self.dificultad <= 10:
            raise ValueError("La dificultad debe estar entre 1 y 10")
        
        if self.tiempo_estimado <= 0:
            raise ValueError("El tiempo estimado debe ser mayor a 0")
        
        # Redondear tiempo a intervalos de 30 minutos
        if self.tiempo_estimado % 30 != 0:
            self.tiempo_estimado = ((self.tiempo_estimado + 29) // 30) * 30
        
        # Redondear hora preferida a intervalos de 30 minutos
        if self.hora_preferida is not None:
            self.hora_preferida = round(self.hora_preferida * 2) / 2
    
    def duracion_intervalos_30min(self) -> int:
        """Duración en intervalos de 30 minutos"""
        return self.tiempo_estimado // 30
    
    def get_repeticiones_semanales(self) -> int:
        if self.frecuencia == 'diaria':
            return 7
        elif self.frecuencia == 'semanal':
            return 1
        elif self.frecuencia == 'mensual':
            return 1
        return 1
    
    def get_repeticiones_mensuales(self) -> int:
        """Repeticiones para todo el mes (4 semanas)"""
        if self.frecuencia == 'diaria':
            return 28  # 7 días × 4 semanas
        elif self.frecuencia == 'semanal':
            return 4   # Una vez por semana × 4 semanas
        elif self.frecuencia == 'mensual':
            return 1   # Una vez al mes
        return 4

@dataclass
class EspacioHogar:
    """Características del espacio del hogar"""
    habitaciones: int = 3
    banos: int = 2
    areas_comunes: List[str] = field(default_factory=lambda: ["Sala", "Cocina", "Comedor"])
    equipamiento: List[str] = field(default_factory=lambda: ["Aspiradora", "Lavadora", "Lavavajillas"])
    metros_cuadrados: int = 100
    tiene_jardin: bool = False
    tiene_balcon: bool = False
    tiene_garage: bool = False
    
    def get_factor_complejidad(self) -> float:
        """Calcula factor de complejidad del espacio"""
        factor_base = 1.0
        factor_base += (self.habitaciones - 2) * 0.1
        factor_base += (self.banos - 1) * 0.15
        factor_base += len(self.areas_comunes) * 0.05
        factor_base += (self.metros_cuadrados - 80) / 200
        if self.tiene_jardin:
            factor_base += 0.2
        if self.tiene_balcon:
            factor_base += 0.1
        if self.tiene_garage:
            factor_base += 0.1
        return max(0.5, min(2.0, factor_base))

class TareasPredeterminadas:
    @staticmethod
    def get_tareas_basicas():
        """Tareas básicas optimizadas para intervalos de 30 minutos"""
        return [
            # Tareas de cocina (críticas para cumplir el requisito diario)
            Tarea("Cocinar", "diaria", 30, 4, "Cocina", hora_preferida=7.0, area_espacio="Cocina", es_predeterminada=True),
            Tarea("Preparar snacks", "diaria", 30, 3, "Cocina", hora_preferida=16.0, area_espacio="Cocina", es_predeterminada=True),
            
            # Tareas de limpieza
            Tarea("Lavar platos", "diaria", 30, 3, "Limpieza", area_espacio="Cocina", es_predeterminada=True),
            Tarea("Aspirar sala", "semanal", 60, 4, "Limpieza", area_espacio="Sala", es_predeterminada=True),
            Tarea("Limpiar baño", "semanal", 90, 7, "Limpieza", area_espacio="Baño", es_predeterminada=True),
            Tarea("Trapear pisos", "semanal", 60, 5, "Limpieza", area_espacio="General", es_predeterminada=True),
            Tarea("Sacar basura", "diaria", 30, 2, "Limpieza", hora_preferida=20.0, area_espacio="Cocina", es_predeterminada=True),
            Tarea("Limpiar cocina profunda", "semanal", 90, 6, "Limpieza", area_espacio="Cocina", es_predeterminada=True),
            
            # Lavandería
            Tarea("Lavar ropa", "semanal", 120, 3, "Lavandería", dias_requeridos=["Sábado", "Domingo"], area_espacio="Lavandería", es_predeterminada=True),
            Tarea("Doblar ropa", "semanal", 60, 2, "Lavandería", area_espacio="Habitación", es_predeterminada=True),
            Tarea("Planchar", "semanal", 90, 5, "Lavandería", area_espacio="Lavandería", es_predeterminada=True),
            
            # Compras y mantenimiento
            Tarea("Comprar víveres", "semanal", 120, 4, "Compras", dias_requeridos=["Sábado"], area_espacio="Exterior", es_predeterminada=True),
            Tarea("Regar plantas", "semanal", 30, 2, "Mantenimiento", area_espacio="Jardín", es_predeterminada=True),
            Tarea("Organizar espacios", "mensual", 180, 8, "Organización", area_espacio="General", es_predeterminada=True),
            Tarea("Lavar ventanas", "mensual", 120, 6, "Limpieza", area_espacio="General", es_predeterminada=True),
            
            # Tareas adicionales de mantenimiento
            Tarea("Aspirar habitaciones", "semanal", 90, 4, "Limpieza", area_espacio="Habitación", es_predeterminada=True),
            Tarea("Limpiar nevera", "mensual", 60, 5, "Limpieza", area_espacio="Cocina", es_predeterminada=True),
            Tarea("Organizar despensa", "mensual", 90, 4, "Organización", area_espacio="Cocina", es_predeterminada=True)
        ]
    
    @staticmethod
    def get_por_categoria(categoria):
        todas = TareasPredeterminadas.get_tareas_basicas()
        return [t for t in todas if t.categoria == categoria]
    
    @staticmethod
    def get_tareas_cocina():
        """Obtiene específicamente las tareas de cocina"""
        return [t for t in TareasPredeterminadas.get_tareas_basicas() if t.categoria == "Cocina"]