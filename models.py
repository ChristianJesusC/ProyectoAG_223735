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
    
    def duracion_horas(self) -> float:
        return self.fin - self.inicio
    
    def contiene_hora(self, hora: float) -> bool:
        return self.inicio <= hora < self.fin
    
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
    
    def __post_init__(self):
        frecuencias_validas = ['diaria', 'semanal', 'mensual']
        if self.frecuencia not in frecuencias_validas:
            raise ValueError(f"Frecuencia debe ser una de: {frecuencias_validas}")
        
        if not 1 <= self.dificultad <= 10:
            raise ValueError("La dificultad debe estar entre 1 y 10")
        
        if self.tiempo_estimado <= 0:
            raise ValueError("El tiempo estimado debe ser mayor a 0")
        
        if self.tiempo_estimado % 30 != 0:
            self.tiempo_estimado = ((self.tiempo_estimado + 29) // 30) * 30
    
    def duracion_intervalos(self) -> int:
        return self.tiempo_estimado // 30
    
    def get_repeticiones_semanales(self) -> int:
        if self.frecuencia == 'diaria':
            return 7
        elif self.frecuencia == 'semanal':
            return 1
        elif self.frecuencia == 'mensual':
            return 1
        return 1

class TareasPredeterminadas:
    @staticmethod
    def get_tareas_basicas():
        return [
            Tarea("Lavar platos", "diaria", 30, 3, "Limpieza", es_predeterminada=True),
            Tarea("Aspirar sala", "semanal", 60, 4, "Limpieza", es_predeterminada=True),
            Tarea("Limpiar baño", "semanal", 90, 7, "Limpieza", es_predeterminada=True),
            Tarea("Trapear pisos", "semanal", 60, 5, "Limpieza", es_predeterminada=True),
            Tarea("Sacar basura", "diaria", 30, 2, "Limpieza", hora_preferida=20, es_predeterminada=True),
            Tarea("Cocinar", "diaria", 60, 6, "Cocina", hora_preferida=12, es_predeterminada=True),
            Tarea("Lavar ropa", "semanal", 120, 3, "Lavandería", dias_requeridos=["Sábado", "Domingo"], es_predeterminada=True),
            Tarea("Doblar ropa", "semanal", 60, 2, "Lavandería", es_predeterminada=True),
            Tarea("Comprar víveres", "semanal", 120, 4, "Compras", dias_requeridos=["Sábado"], es_predeterminada=True),
            Tarea("Regar plantas", "semanal", 30, 2, "Mantenimiento", es_predeterminada=True),
            Tarea("Organizar espacios", "mensual", 180, 8, "Organización", es_predeterminada=True),
            Tarea("Limpiar cocina profunda", "semanal", 60, 5, "Limpieza", es_predeterminada=True),
            Tarea("Lavar ventanas", "mensual", 90, 6, "Limpieza", es_predeterminada=True)
        ]
    
    @staticmethod
    def get_por_categoria(categoria):
        todas = TareasPredeterminadas.get_tareas_basicas()
        return [t for t in todas if t.categoria == categoria]