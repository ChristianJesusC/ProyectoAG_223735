import random
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import date, timedelta
from models import Roommate, Tarea
from enhanced_models import RoommateEnhanced, RestriccionMedica
from genetic_algorithm import AlgoritmoGeneticoOptimizado

class AlgoritmoGeneticoMejorado(AlgoritmoGeneticoOptimizado):
    
    def __init__(self, roommates: List[RoommateEnhanced], tareas: List[Tarea], 
                 tam_poblacion: int = 100, generaciones: int = 50,
                 tasa_mutacion: float = 0.1, tasa_cruzamiento: float = 0.8,
                 ajustes_aprendizaje: Dict = None, fecha_planificacion: date = None):
        
        super().__init__(roommates, tareas, tam_poblacion, generaciones, 
                        tasa_mutacion, tasa_cruzamiento)
        
        self.roommates_enhanced = roommates
        self.ajustes_aprendizaje = ajustes_aprendizaje or {}
        self.fecha_planificacion = fecha_planificacion or date.today()
        
        # Nuevos pesos para características mejoradas
        self.pesos.update({
            'restricciones_medicas': 30,  # Peso alto para restricciones
            'ausencias': 25,              # Peso alto para ausencias
            'aprendizaje_historico': 15,  # Aprendizaje de experiencias
            'incompatibilidades': 20      # Incompatibilidades entre roommates
        })
    
    def calcular_fitness(self, individuo: Dict) -> float:
        """Fitness mejorado con nuevas características"""
        if not individuo:
            return 0.0
        
        fitness_total = 0
        
        try:
            # Fitness originales
            fitness_total += self._calcular_fitness_equidad(individuo) * self.pesos['equidad']
            fitness_total += self._calcular_fitness_compatibilidad(individuo) * self.pesos['compatibilidad']
            fitness_total += self._calcular_fitness_habilidades(individuo) * self.pesos['habilidades']
            fitness_total += self._calcular_fitness_preferencias(individuo) * self.pesos['preferencias']
            fitness_total += self._calcular_fitness_rotacion(individuo) * self.pesos['rotacion']
            fitness_total += self._calcular_fitness_cocina_diaria(individuo) * self.pesos['cocina_diaria']
            
            # Nuevos fitness
            fitness_total += self._calcular_fitness_restricciones_medicas(individuo) * self.pesos['restricciones_medicas']
            fitness_total += self._calcular_fitness_ausencias(individuo) * self.pesos['ausencias']
            fitness_total += self._calcular_fitness_aprendizaje_historico(individuo) * self.pesos['aprendizaje_historico']
            fitness_total += self._calcular_fitness_incompatibilidades(individuo) * self.pesos['incompatibilidades']
        
        except Exception:
            return 0.0
        
        return max(0, fitness_total)
    
    def _calcular_fitness_restricciones_medicas(self, individuo: Dict) -> float:
        """Penaliza asignaciones que violan restricciones médicas"""
        violaciones = 0
        total_asignaciones = len(individuo)
        
        if total_asignaciones == 0:
            return 1.0
        
        roommates_dict = {rm.nombre: rm for rm in self.roommates_enhanced}
        tareas_dict = {tarea.nombre: tarea for tarea in self.tareas}
        
        for asignacion in individuo.values():
            roommate_obj = roommates_dict.get(asignacion['roommate'])
            tarea_obj = tareas_dict.get(asignacion['tarea'])
            
            if roommate_obj and tarea_obj:
                # Verificar si puede realizar la tarea
                puede_realizar, motivo = roommate_obj.puede_realizar_tarea(
                    tarea_obj, self.fecha_planificacion
                )
                
                if not puede_realizar:
                    # Penalización severa por violación de restricción médica
                    if "Restricción médica" in motivo:
                        violaciones += 1
        
        # Retorna 1.0 si no hay violaciones, 0.0 si todas son violaciones
        return max(0.0, 1.0 - (violaciones / total_asignaciones))
    
    def _calcular_fitness_ausencias(self, individuo: Dict) -> float:
        """Penaliza asignaciones durante períodos de ausencia"""
        violaciones = 0
        total_asignaciones = len(individuo)
        
        if total_asignaciones == 0:
            return 1.0
        
        roommates_dict = {rm.nombre: rm for rm in self.roommates_enhanced}
        
        for asignacion in individuo.values():
            roommate_obj = roommates_dict.get(asignacion['roommate'])
            
            if roommate_obj:
                # Calcular fecha aproximada de la tarea
                dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                dia_indice = dias_semana.index(asignacion['dia'])
                semana_offset = (asignacion['semana'] - 1) * 7
                fecha_tarea = self.fecha_planificacion + timedelta(days=dia_indice + semana_offset)
                
                # Verificar ausencias
                for ausencia in roommate_obj.ausencias:
                    if ausencia.esta_ausente(fecha_tarea, asignacion['hora']):
                        violaciones += 1
                        break
        
        return max(0.0, 1.0 - (violaciones / total_asignaciones))
    
    def _calcular_fitness_aprendizaje_historico(self, individuo: Dict) -> float:
        """Bonifica/penaliza basado en experiencias históricas"""
        if not self.ajustes_aprendizaje:
            return 0.5  # Neutral si no hay datos históricos
        
        score_total = 0
        num_asignaciones = 0
        
        factores_tiempo = self.ajustes_aprendizaje.get('factores_tiempo', {})
        penalizaciones_calidad = self.ajustes_aprendizaje.get('penalizaciones_calidad', {})
        
        for asignacion in individuo.values():
            roommate = asignacion['roommate']
            tarea = asignacion['tarea']
            
            score_asignacion = 0.5  # Base neutral
            
            # Ajustar por eficiencia temporal histórica
            if roommate in factores_tiempo and tarea in factores_tiempo[roommate]:
                factor = factores_tiempo[roommate][tarea]
                if factor < 1.0:  # Más eficiente
                    score_asignacion += 0.3
                elif factor > 1.5:  # Mucho menos eficiente
                    score_asignacion -= 0.3
            
            # Penalizar por baja calidad histórica
            if (roommate in penalizaciones_calidad and 
                tarea in penalizaciones_calidad[roommate]):
                score_asignacion -= 0.4
            
            score_total += max(0.0, min(1.0, score_asignacion))
            num_asignaciones += 1
        
        return score_total / num_asignaciones if num_asignaciones > 0 else 0.5
    
    def _calcular_fitness_incompatibilidades(self, individuo: Dict) -> float:
        """Penaliza asignaciones simultáneas de roommates incompatibles"""
        penalizaciones = 0
        total_comparaciones = 0
        
        roommates_dict = {rm.nombre: rm for rm in self.roommates_enhanced}
        
        # Agrupar asignaciones por día/hora/semana
        asignaciones_por_slot = {}
        for asignacion in individuo.values():
            slot_key = (asignacion['semana'], asignacion['dia'], asignacion['hora'])
            if slot_key not in asignaciones_por_slot:
                asignaciones_por_slot[slot_key] = []
            asignaciones_por_slot[slot_key].append(asignacion['roommate'])
        
        # Verificar incompatibilidades en slots simultáneos
        for roommates_en_slot in asignaciones_por_slot.values():
            if len(roommates_en_slot) > 1:
                for i, rm1 in enumerate(roommates_en_slot):
                    for rm2 in roommates_en_slot[i+1:]:
                        total_comparaciones += 1
                        
                        rm1_obj = roommates_dict.get(rm1)
                        if rm1_obj and rm2 in rm1_obj.incompatibilidades:
                            penalizaciones += 1
        
        if total_comparaciones == 0:
            return 1.0
        
        return max(0.0, 1.0 - (penalizaciones / total_comparaciones))
    
    def generar_individuo(self) -> Dict:
        """Generación mejorada que respeta restricciones"""
        max_intentos = 100
        
        for intento in range(max_intentos):
            try:
                asignaciones = {}
                
                # Primero asegurar cocina diaria
                self._asegurar_cocina_diaria_mejorada(asignaciones)
                
                # Luego agregar el resto de tareas
                for tarea in self.tareas:
                    if tarea.categoria != 'Cocina':
                        self._asignar_tarea_mensual_mejorada(tarea, asignaciones)
                
                # Verificar que el individuo cumple restricciones básicas
                if self._validar_individuo(asignaciones):
                    return asignaciones
            
            except Exception:
                continue
        
        # Si no se puede generar individuo válido, generar uno básico
        return super().generar_individuo()
    
    def _asegurar_cocina_diaria_mejorada(self, asignaciones: Dict):
        """Asegurar cocina diaria respetando restricciones"""
        tareas_cocina = [t for t in self.tareas if t.categoria == 'Cocina']
        
        if not tareas_cocina:
            return
        
        for semana in self.semanas:
            for dia in self.dias_semana:
                # Buscar roommate disponible para cocina
                roommate_asignado = self._encontrar_roommate_disponible_cocina(
                    dia, semana, tareas_cocina
                )
                
                if roommate_asignado:
                    tarea_cocina = random.choice(tareas_cocina)
                    hora = self._seleccionar_hora_30min_mejorada(
                        roommate_asignado, dia, tarea_cocina, semana
                    )
                    
                    key = f"cocina_obligatoria_S{semana}_{dia}_{hora}"
                    asignaciones[key] = {
                        'tarea': tarea_cocina.nombre,
                        'roommate': roommate_asignado.nombre,
                        'dia': dia,
                        'semana': semana,
                        'hora': hora,
                        'duracion': tarea_cocina.tiempo_estimado
                    }
    
    def _encontrar_roommate_disponible_cocina(self, dia: str, semana: int, 
                                            tareas_cocina: List[Tarea]) -> Optional[RoommateEnhanced]:
        """Encuentra roommate disponible para tareas de cocina"""
        roommates_validos = []
        
        for roommate in self.roommates_enhanced:
            # Verificar restricciones médicas para cocina
            puede_cocinar = True
            for restriccion in roommate.restricciones_medicas:
                if (restriccion.categoria_tarea == 'Cocina' and 
                    restriccion.severidad == 'prohibido' and
                    restriccion.es_activa(self.fecha_planificacion)):
                    puede_cocinar = False
                    break
            
            if puede_cocinar:
                # Verificar ausencias
                fecha_tarea = self._calcular_fecha_tarea(dia, semana)
                ausente = any(ausencia.esta_ausente(fecha_tarea) 
                            for ausencia in roommate.ausencias)
                
                if not ausente:
                    roommates_validos.append(roommate)
        
        return random.choice(roommates_validos) if roommates_validos else None
    
    def _calcular_fecha_tarea(self, dia: str, semana: int) -> date:
        """Calcula fecha aproximada de una tarea"""
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dia_indice = dias_semana.index(dia)
        semana_offset = (semana - 1) * 7
        return self.fecha_planificacion + timedelta(days=dia_indice + semana_offset)
    
    def _seleccionar_hora_30min_mejorada(self, roommate: RoommateEnhanced, 
                                       dia: str, tarea: Tarea, semana: int) -> float:
        """Selección de hora considerando restricciones y ausencias"""
        fecha_tarea = self._calcular_fecha_tarea(dia, semana)
        
        # Verificar ausencias parciales
        for ausencia in roommate.ausencias:
            if (ausencia.es_parcial and ausencia.esta_ausente(fecha_tarea) and
                dia in ausencia.horas_disponibles):
                # Usar solo las horas disponibles durante la ausencia
                opciones_limitadas = []
                for rango in ausencia.horas_disponibles[dia]:
                    opciones_limitadas.extend(rango.get_intervalos_30min())
                
                if opciones_limitadas:
                    return random.choice(opciones_limitadas)
        
        # Usar lógica original si no hay ausencias parciales
        return super()._seleccionar_hora_30min(roommate, dia, tarea)
    
    def _validar_individuo(self, asignaciones: Dict) -> bool:
        """Valida que un individuo cumple restricciones básicas"""
        try:
            roommates_dict = {rm.nombre: rm for rm in self.roommates_enhanced}
            tareas_dict = {tarea.nombre: tarea for tarea in self.tareas}
            
            for asignacion in asignaciones.values():
                roommate_obj = roommates_dict.get(asignacion['roommate'])
                tarea_obj = tareas_dict.get(asignacion['tarea'])
                
                if roommate_obj and tarea_obj:
                    # Verificar restricciones médicas críticas
                    puede_realizar, motivo = roommate_obj.puede_realizar_tarea(
                        tarea_obj, self.fecha_planificacion
                    )
                    
                    if not puede_realizar and "Restricción médica" in motivo:
                        return False
            
            return True
        
        except Exception:
            return False
    
    def ajustar_pesos_dinamicos(self, emergencias_activas: List = None):
        """Ajusta pesos dinámicamente según el contexto"""
        if emergencias_activas:
            # Aumentar peso de ausencias y restricciones durante emergencias
            self.pesos['ausencias'] = 35
            self.pesos['restricciones_medicas'] = 35
            self.pesos['equidad'] = 15  # Reducir temporalmente
        
        # Normalizar pesos para que sumen 100
        total_pesos = sum(self.pesos.values())
        factor_normalizacion = 100 / total_pesos
        
        for categoria in self.pesos:
            self.pesos[categoria] *= factor_normalizacion