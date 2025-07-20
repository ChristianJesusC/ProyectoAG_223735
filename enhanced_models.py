from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta 
from models import Roommate, Tarea, RangoTiempo


@dataclass
class RestriccionMedica:
    """Restricciones médicas específicas para roommates"""
    categoria_tarea: str
    tipo_restriccion: str  # "alergia", "limitacion_fisica", "medica", "temporal"
    descripcion: str
    severidad: str  # "prohibido", "limitado", "con_ayuda"
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    productos_prohibidos: List[str] = field(default_factory=list)
    
    def es_activa(self, fecha_actual: date = None) -> bool:
        """Verifica si la restricción está activa en la fecha dada"""
        if fecha_actual is None:
            fecha_actual = date.today()
        
        if self.fecha_inicio and fecha_actual < self.fecha_inicio:
            return False
        if self.fecha_fin and fecha_actual > self.fecha_fin:
            return False
        return True
    
    def permite_tarea(self, tarea: Tarea, fecha: date = None) -> bool:
        """Verifica si permite realizar una tarea específica"""
        if not self.es_activa(fecha):
            return True
        
        if self.categoria_tarea != tarea.categoria:
            return True
        
        if self.severidad == "prohibido":
            return False
        elif self.severidad == "limitado":
            return tarea.dificultad <= 5  # Solo tareas fáciles
        elif self.severidad == "con_ayuda":
            return True  # Permite pero necesita ayuda
        
        return True

@dataclass
class Ausencia:
    """Manejo de ausencias temporales de roommates"""
    roommate: str
    fecha_inicio: date
    fecha_fin: date
    motivo: str
    tipo: str = "vacaciones"  # "vacaciones", "enfermedad", "trabajo", "emergencia"
    es_parcial: bool = False  # True si solo algunas horas del día
    horas_disponibles: Dict[str, List[RangoTiempo]] = field(default_factory=dict)
    
    def esta_ausente(self, fecha: date, hora: float = None) -> bool:
        """Verifica si está ausente en fecha/hora específica"""
        if not (self.fecha_inicio <= fecha <= self.fecha_fin):
            return False
        
        if not self.es_parcial:
            return True
        
        if hora is None:
            return False
        
        dia_semana = fecha.strftime("%A")  # Convertir a nombre del día
        dias_map = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
        }
        dia = dias_map.get(dia_semana, dia_semana)
        
        if dia in self.horas_disponibles:
            return not any(rango.contiene_hora(hora) for rango in self.horas_disponibles[dia])
        
        return True

@dataclass
class RoommateEnhanced(Roommate):
    """Roommate con características extendidas"""
    restricciones_medicas: List[RestriccionMedica] = field(default_factory=list)
    incompatibilidades: List[str] = field(default_factory=list)  # Nombres incompatibles
    ausencias: List[Ausencia] = field(default_factory=list)
    
    def puede_realizar_tarea(self, tarea: Tarea, fecha: date = None) -> tuple[bool, str]:
        """Verifica si puede realizar una tarea con detalles del motivo"""
        if fecha is None:
            fecha = date.today()
        
        # Verificar ausencias
        for ausencia in self.ausencias:
            if ausencia.esta_ausente(fecha):
                return False, f"Ausente por {ausencia.motivo}"
        
        # Verificar restricciones médicas
        for restriccion in self.restricciones_medicas:
            if not restriccion.permite_tarea(tarea, fecha):
                return False, f"Restricción médica: {restriccion.descripcion}"
        
        return True, "Sin restricciones"
    
    def agregar_restriccion_medica(self, categoria: str, tipo: str, descripcion: str, 
                                  severidad: str, productos_prohibidos: List[str] = None):
        """Agregar restricción médica de forma fácil"""
        restriccion = RestriccionMedica(
            categoria_tarea=categoria,
            tipo_restriccion=tipo,
            descripcion=descripcion,
            severidad=severidad,
            productos_prohibidos=productos_prohibidos or []
        )
        self.restricciones_medicas.append(restriccion)
    
    def agregar_ausencia(self, fecha_inicio: date, fecha_fin: date, motivo: str, tipo: str = "vacaciones"):
        """Agregar ausencia de forma fácil"""
        ausencia = Ausencia(
            roommate=self.nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            motivo=motivo,
            tipo=tipo
        )
        self.ausencias.append(ausencia)