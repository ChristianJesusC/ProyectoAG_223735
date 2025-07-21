from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np

@dataclass
class RangoTiempo:
    """Rango de tiempo con intervalos de 30 minutos"""
    inicio: float
    fin: float
    
    def __post_init__(self):
        if self.inicio >= self.fin:
            raise ValueError("Hora de inicio debe ser menor que fin")
        # Redondear a intervalos de 30 minutos
        self.inicio = round(self.inicio * 2) / 2
        self.fin = round(self.fin * 2) / 2
    
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
    """Roommate con horarios, habilidades y restricciones básicas"""
    nombre: str
    horarios_disponibles: Dict[str, List[RangoTiempo]]
    habilidades: Dict[str, int]  # 1-10 por categoría
    preferencias: Dict[str, str]  # 'prefiere', 'neutro', 'evita'
    tiempo_total_disponible: int  # horas/semana objetivo
    restricciones_medicas: List[str] = field(default_factory=list)
    ausencias_activas: List[str] = field(default_factory=list)
    
    def esta_disponible(self, dia: str, hora: float) -> bool:
        """Verifica disponibilidad considerando horarios y restricciones"""
        # Verificar ausencias activas
        if self.ausencias_activas:
            return False
        
        if dia not in self.horarios_disponibles:
            return False
        return any(rango.contiene_hora(hora) for rango in self.horarios_disponibles[dia])
    
    def get_habilidad(self, categoria: str) -> int:
        return self.habilidades.get(categoria, 5)
    
    def get_preferencia(self, categoria: str) -> str:
        return self.preferencias.get(categoria, 'neutro')
    
    def tiene_restriccion_para(self, categoria: str) -> bool:
        """Verifica si tiene restricción médica para una categoría"""
        return any(categoria.lower() in restriccion.lower() 
                  for restriccion in self.restricciones_medicas)
    
    def total_horas_disponibles(self) -> float:
        total = 0
        for rangos in self.horarios_disponibles.values():
            for rango in rangos:
                total += rango.duracion_horas()
        return total

@dataclass
class Tarea:
    """Tarea doméstica con tiempo en intervalos de 30 minutos"""
    nombre: str
    frecuencia: str  # 'diaria', 'semanal', 'mensual'
    tiempo_estimado: int  # minutos
    dificultad: int  # 1-10
    categoria: str
    dias_requeridos: List[str] = field(default_factory=list)
    hora_preferida: Optional[float] = None
    es_predeterminada: bool = False
    
    def __post_init__(self):
        # Redondear tiempo a intervalos de 30 minutos
        if self.tiempo_estimado % 30 != 0:
            self.tiempo_estimado = ((self.tiempo_estimado + 29) // 30) * 30
        
        # Redondear hora preferida a intervalos de 30 minutos
        if self.hora_preferida is not None:
            self.hora_preferida = round(self.hora_preferida * 2) / 2
    
    def get_repeticiones_mensuales(self) -> int:
        """Repeticiones para cronograma mensual (4 semanas)"""
        if self.frecuencia == 'diaria':
            return 28  # 7 días × 4 semanas
        elif self.frecuencia == 'semanal':
            return 4   # Una vez por semana × 4 semanas
        elif self.frecuencia == 'mensual':
            return 1   # Una vez al mes
        return 1

class TareasPredeterminadas:
    @staticmethod
    def get_tareas_esenciales():
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
    
    @staticmethod
    def get_tareas_extras():
        """Tareas extras generalizadas"""
        return [
            Tarea("Planchar ropa", "semanal", 60, 5, "Lavandería"),
            Tarea("Limpiar refrigerador", "mensual", 90, 6, "Limpieza"),
            Tarea("Comprar productos limpieza", "mensual", 60, 3, "Compras"),
            Tarea("Organizar despensa", "mensual", 60, 4, "Organización")
        ]

@dataclass
class EspacioHogar:
    """Características del espacio que impactan la distribución de tareas"""
    habitaciones: int = 2
    banos: int = 1
    metros_cuadrados: int = 80
    pisos: int = 1
    tiene_jardin: bool = False
    tiene_balcon: bool = False
    tiene_garage: bool = False
    tiene_lavanderia: bool = False
    tiene_estudio: bool = False
    equipamiento: List[str] = field(default_factory=lambda: ["Aspiradora", "Lavadora"])
    
    def get_factor_tiempo_limpieza(self) -> float:
        """Factor que multiplica el tiempo de tareas de limpieza"""
        factor = 1.0
        
        # Habitaciones adicionales aumentan tiempo significativamente
        factor += (self.habitaciones - 1) * 0.25
        
        # Baños adicionales requieren mucho tiempo extra
        factor += (self.banos - 1) * 0.35
        
        # Metros cuadrados impactan linealmente
        factor += (self.metros_cuadrados - 50) / 150
        
        # Pisos adicionales aumentan complejidad
        factor += (self.pisos - 1) * 0.20
        
        # Espacios especiales
        if self.tiene_balcon:
            factor += 0.15
        if self.tiene_garage:
            factor += 0.20
        if self.tiene_estudio:
            factor += 0.10
        
        return max(0.5, min(2.5, factor))
    
    def get_factor_equipamiento(self, categoria_tarea: str) -> float:
        """Factor de eficiencia según equipamiento disponible"""
        factor = 1.0
        
        if categoria_tarea == "Limpieza":
            if "Robot aspirador" in self.equipamiento:
                factor *= 0.6  # 40% menos tiempo
            elif "Aspiradora" in self.equipamiento:
                factor *= 0.8  # 20% menos tiempo
            
            if "Pulidora" in self.equipamiento:
                factor *= 0.7  # Para pisos
                
        elif categoria_tarea == "Lavandería":
            if "Lavadora" in self.equipamiento:
                factor *= 0.7
            if "Secadora" in self.equipamiento:
                factor *= 0.6
            if "Plancha a vapor" in self.equipamiento:
                factor *= 0.8
                
        elif categoria_tarea == "Cocina":
            if "Lavavajillas" in self.equipamiento:
                factor *= 0.5  # Mucho menos tiempo lavando platos
            if "Microondas" in self.equipamiento:
                factor *= 0.9
            if "Procesador alimentos" in self.equipamiento:
                factor *= 0.8
        
        return max(0.3, factor)
    
    def generar_tareas_espaciales(self) -> List[Tarea]:
        """Genera tareas específicas según características del espacio"""
        tareas_extras = []
        
        # Tareas por habitaciones adicionales
        if self.habitaciones > 2:
            for i in range(self.habitaciones - 2):
                tareas_extras.append(
                    Tarea(f"Limpiar habitación {i+3}", "semanal", 
                         int(45 * self.get_factor_tiempo_limpieza()), 4, "Limpieza")
                )
        
        # Tareas por baños adicionales
        if self.banos > 1:
            for i in range(self.banos - 1):
                tareas_extras.append(
                    Tarea(f"Limpiar baño {i+2}", "semanal", 
                         int(60 * self.get_factor_tiempo_limpieza()), 6, "Limpieza")
                )
        
        # Tareas de jardín
        if self.tiene_jardin:
            tareas_extras.extend([
                Tarea("Regar jardín", "diaria", 30, 2, "Mantenimiento"),
                Tarea("Podar plantas", "semanal", 90, 5, "Mantenimiento"),
                Tarea("Limpiar jardín", "semanal", 120, 4, "Limpieza"),
                Tarea("Mantener césped", "semanal", 60, 4, "Mantenimiento")
            ])
        
        # Tareas de balcón
        if self.tiene_balcon:
            tareas_extras.extend([
                Tarea("Limpiar balcón", "semanal", 45, 3, "Limpieza"),
                Tarea("Regar plantas balcón", "diaria", 15, 1, "Mantenimiento")
            ])
        
        # Tareas de garage
        if self.tiene_garage:
            tareas_extras.extend([
                Tarea("Organizar garage", "mensual", 180, 5, "Organización"),
                Tarea("Limpiar garage", "mensual", 120, 4, "Limpieza")
            ])
        
        # Tareas de lavandería dedicada
        if self.tiene_lavanderia:
            tareas_extras.extend([
                Tarea("Organizar lavandería", "semanal", 30, 3, "Organización"),
                Tarea("Limpiar lavandería", "semanal", 45, 4, "Limpieza")
            ])
        
        # Tareas de estudio
        if self.tiene_estudio:
            tareas_extras.extend([
                Tarea("Organizar estudio", "semanal", 60, 4, "Organización"),
                Tarea("Limpiar estudio", "semanal", 45, 3, "Limpieza")
            ])
        
        # Tareas por pisos adicionales
        if self.pisos > 1:
            tareas_extras.append(
                Tarea("Limpiar escaleras", "semanal", 
                     int(30 * (self.pisos - 1)), 5, "Limpieza")
            )
        
        return tareas_extras
    
    def get_factor_rotacion_complejidad(self) -> float:
        """Factor que afecta la frecuencia de rotación según complejidad"""
        # Espacios más complejos necesitan rotación más frecuente
        complejidad = 0
        complejidad += self.habitaciones * 0.3
        complejidad += self.banos * 0.4
        complejidad += (self.metros_cuadrados / 100) * 0.2
        complejidad += self.pisos * 0.3
        
        if self.tiene_jardin:
            complejidad += 0.5
        if self.tiene_garage:
            complejidad += 0.3
        if self.tiene_balcon:
            complejidad += 0.2
        
        # Factor de 1.0 a 2.0 (más complejo = más rotación)
        return min(2.0, max(1.0, 1.0 + complejidad * 0.2))
    
    def get_prioridades_espaciales(self) -> Dict[str, float]:
        """Obtiene prioridades de categorías según el espacio"""
        prioridades = {
            'Limpieza': 1.0,
            'Cocina': 1.0,
            'Lavandería': 1.0,
            'Compras': 1.0,
            'Mantenimiento': 1.0,
            'Organización': 1.0
        }
        
        # Espacios grandes priorizan limpieza y organización
        if self.metros_cuadrados > 120:
            prioridades['Limpieza'] *= 1.3
            prioridades['Organización'] *= 1.2
        
        # Jardín prioriza mantenimiento
        if self.tiene_jardin:
            prioridades['Mantenimiento'] *= 1.5
        
        # Muchas habitaciones priorizan organización
        if self.habitaciones > 3:
            prioridades['Organización'] *= 1.4
        
        # Pocos equipos priorizan mantenimiento
        if len(self.equipamiento) < 3:
            prioridades['Mantenimiento'] *= 1.2
        
        return prioridades


    """Catálogo de tareas optimizadas para estudiantes"""
    
    @staticmethod
    def get_tareas_esenciales():
        """Tareas esenciales para funcionamiento básico del hogar"""
        return [
            # 🍳 COCINA - Critical para cumplir requisito diario
            Tarea("Desayuno", "diaria", 30, 3, "Cocina", hora_preferida=7.0, es_predeterminada=True),
            Tarea("Almuerzo", "diaria", 60, 4, "Cocina", hora_preferida=13.0, es_predeterminada=True),
            Tarea("Cena", "diaria", 60, 5, "Cocina", hora_preferida=19.0, es_predeterminada=True),
            Tarea("Lavar platos", "diaria", 30, 2, "Cocina", es_predeterminada=True),
            
            # 🧹 LIMPIEZA
            Tarea("Aspirar sala", "semanal", 60, 4, "Limpieza", es_predeterminada=True),
            Tarea("Limpiar baño", "semanal", 90, 6, "Limpieza", es_predeterminada=True),
            Tarea("Trapear", "semanal", 60, 4, "Limpieza", es_predeterminada=True),
            Tarea("Sacar basura", "diaria", 30, 1, "Limpieza", hora_preferida=20.0, es_predeterminada=True),
            
            # 👕 LAVANDERÍA
            Tarea("Lavar ropa", "semanal", 120, 3, "Lavandería", 
                  dias_requeridos=["Sábado", "Domingo"], es_predeterminada=True),
            Tarea("Doblar ropa", "semanal", 60, 2, "Lavandería", es_predeterminada=True),
            
            # 🛒 COMPRAS & MANTENIMIENTO
            Tarea("Comprar víveres", "semanal", 120, 4, "Compras", 
                  dias_requeridos=["Sábado"], es_predeterminada=True),
            Tarea("Organizar espacios", "mensual", 120, 6, "Organización", es_predeterminada=True),
        ]
    
    @staticmethod
    def get_tareas_extras():
        """Tareas adicionales para hogares más complejos"""
        return [
            Tarea("Limpiar ventanas", "mensual", 90, 5, "Limpieza", es_predeterminada=True),
            Tarea("Aspirar habitaciones", "semanal", 90, 4, "Limpieza", es_predeterminada=True),
            Tarea("Planchar", "semanal", 90, 4, "Lavandería", es_predeterminada=True),
            Tarea("Lavar nevera", "mensual", 60, 5, "Limpieza", es_predeterminada=True),
        ]