import random
import numpy as np
from typing import List, Dict, Tuple
from models import Roommate, Tarea

class AlgoritmoGeneticoOptimizado:
    
    def __init__(self, roommates: List[Roommate], tareas: List[Tarea], 
                 tam_poblacion: int = 100, generaciones: int = 50,
                 tasa_mutacion: float = 0.1, tasa_cruzamiento: float = 0.8):
        
        self.roommates = roommates
        self.tareas = tareas
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        self.tasa_mutacion = tasa_mutacion
        self.tasa_cruzamiento = tasa_cruzamiento
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        self.pesos = {
            'equidad': 25,
            'compatibilidad': 25,
            'habilidades': 20,
            'preferencias': 10,
            'rotacion': 10,
            'tiempos_muertos': 10
        }
    
    def generar_individuo(self) -> Dict:
        asignaciones = {}
        
        for tarea in self.tareas:
            repeticiones = self._calcular_repeticiones(tarea)
            
            for rep in range(repeticiones):
                roommate = random.choice(self.roommates)
                dia = self._seleccionar_dia(tarea)
                hora = self._seleccionar_hora(roommate, dia, tarea)
                
                key = f"{tarea.nombre}_{rep}_{dia}_{hora}"
                asignaciones[key] = {
                    'tarea': tarea.nombre,
                    'roommate': roommate.nombre,
                    'dia': dia,
                    'hora': int(hora),
                    'duracion': tarea.tiempo_estimado
                }
        
        return asignaciones
    
    def _seleccionar_hora(self, roommate: Roommate, dia: str, tarea: Tarea) -> float:
        if tarea.hora_preferida is not None:
            if roommate.esta_disponible(dia, tarea.hora_preferida):
                return tarea.hora_preferida
        
        if dia in roommate.horarios_disponibles:
            rangos_validos = roommate.horarios_disponibles[dia]
            if rangos_validos:
                rango = random.choice(rangos_validos)
                opciones_hora = []
                hora_actual = rango.inicio
                while hora_actual < rango.fin:
                    opciones_hora.append(hora_actual)
                    hora_actual += 0.5
                if opciones_hora:
                    return random.choice(opciones_hora)
        
        return random.randint(6, 22)
    
    def _calcular_repeticiones(self, tarea: Tarea) -> int:
        if tarea.frecuencia == 'diaria':
            return 7
        elif tarea.frecuencia == 'semanal':
            return 1
        elif tarea.frecuencia == 'mensual':
            return 1 if random.random() < 0.25 else 0
        return 1
    
    def _seleccionar_dia(self, tarea: Tarea) -> str:
        if tarea.dias_requeridos:
            return random.choice(tarea.dias_requeridos)
        return random.choice(self.dias_semana)
    
    def calcular_fitness(self, individuo: Dict) -> float:
        if not individuo:
            return 0.0
        
        fitness_total = 0
        
        try:
            fitness_total += self._calcular_fitness_equidad(individuo) * self.pesos['equidad']
            fitness_total += self._calcular_fitness_compatibilidad(individuo) * self.pesos['compatibilidad']
            fitness_total += self._calcular_fitness_habilidades(individuo) * self.pesos['habilidades']
            fitness_total += self._calcular_fitness_preferencias(individuo) * self.pesos['preferencias']
        except Exception:
            return 0.0
        
        return max(0, fitness_total)
    
    def _calcular_fitness_equidad(self, individuo: Dict) -> float:
        carga_por_roommate = {}
        
        for asignacion in individuo.values():
            roommate = asignacion['roommate']
            if roommate not in carga_por_roommate:
                carga_por_roommate[roommate] = 0
            carga_por_roommate[roommate] += asignacion['duracion']
        
        for roommate in self.roommates:
            if roommate.nombre not in carga_por_roommate:
                carga_por_roommate[roommate.nombre] = 0
        
        cargas = list(carga_por_roommate.values())
        if len(cargas) <= 1 or np.mean(cargas) == 0:
            return 1.0
        
        coef_variacion = np.std(cargas) / np.mean(cargas)
        return max(0, 1.0 - coef_variacion)
    
    def _calcular_fitness_compatibilidad(self, individuo: Dict) -> float:
        compatibilidad = 0
        total_asignaciones = len(individuo)
        
        if total_asignaciones == 0:
            return 1.0
        
        roommates_dict = {rm.nombre: rm for rm in self.roommates}
        
        for asignacion in individuo.values():
            roommate_obj = roommates_dict.get(asignacion['roommate'])
            if roommate_obj and roommate_obj.esta_disponible(asignacion['dia'], asignacion['hora']):
                compatibilidad += 1
        
        return compatibilidad / total_asignaciones
    
    def _calcular_fitness_habilidades(self, individuo: Dict) -> float:
        if not individuo:
            return 1.0
        
        habilidades_score = 0
        tareas_dict = {tarea.nombre: tarea for tarea in self.tareas}
        roommates_dict = {rm.nombre: rm for rm in self.roommates}
        
        for asignacion in individuo.values():
            roommate_obj = roommates_dict.get(asignacion['roommate'])
            tarea_obj = tareas_dict.get(asignacion['tarea'])
            
            if roommate_obj and tarea_obj:
                nivel_habilidad = roommate_obj.get_habilidad(tarea_obj.categoria)
                habilidades_score += nivel_habilidad / 10.0
        
        return habilidades_score / len(individuo)
    
    def _calcular_fitness_preferencias(self, individuo: Dict) -> float:
        if not individuo:
            return 1.0
        
        preferencias_score = 0
        tareas_dict = {tarea.nombre: tarea for tarea in self.tareas}
        roommates_dict = {rm.nombre: rm for rm in self.roommates}
        
        for asignacion in individuo.values():
            roommate_obj = roommates_dict.get(asignacion['roommate'])
            tarea_obj = tareas_dict.get(asignacion['tarea'])
            
            if roommate_obj and tarea_obj:
                preferencia = roommate_obj.get_preferencia(tarea_obj.categoria)
                if preferencia == 'prefiere':
                    preferencias_score += 1.0
                elif preferencia == 'neutro':
                    preferencias_score += 0.5
        
        return preferencias_score / len(individuo)
    
    def seleccion_torneo(self, poblacion: List[Tuple[Dict, float]], tam_torneo: int = 3) -> Dict:
        torneo = random.sample(poblacion, min(tam_torneo, len(poblacion)))
        return max(torneo, key=lambda x: x[1])[0]
    
    def cruzamiento(self, padre1: Dict, padre2: Dict) -> Dict:
        if random.random() > self.tasa_cruzamiento:
            return {k: v.copy() for k, v in padre1.items()}
        
        hijo = {}
        keys = list(padre1.keys())
        
        if len(keys) == 0:
            return {k: v.copy() for k, v in padre1.items()}
        
        punto_corte = random.randint(1, len(keys) - 1)
        
        for i, key in enumerate(keys):
            if i < punto_corte:
                hijo[key] = padre1[key].copy()
            else:
                if key in padre2:
                    hijo[key] = padre2[key].copy()
                else:
                    hijo[key] = padre1[key].copy()
        
        return hijo
    
    def mutacion(self, individuo: Dict) -> Dict:
        individuo_mutado = {}
        
        for key, asignacion in individuo.items():
            if random.random() < self.tasa_mutacion:
                asignacion_mutada = asignacion.copy()
                
                tipo_mutacion = random.choice(['roommate', 'horario', 'dia'])
                
                if tipo_mutacion == 'roommate':
                    asignacion_mutada['roommate'] = random.choice(self.roommates).nombre
                elif tipo_mutacion == 'horario':
                    asignacion_mutada['hora'] = random.randint(6, 22)
                elif tipo_mutacion == 'dia':
                    asignacion_mutada['dia'] = random.choice(self.dias_semana)
                
                individuo_mutado[key] = asignacion_mutada
            else:
                individuo_mutado[key] = asignacion.copy()
        
        return individuo_mutado
    
    def ejecutar(self) -> Tuple[Dict, List[Dict]]:
        try:
            poblacion = []
            for _ in range(self.tam_poblacion):
                individuo = self.generar_individuo()
                if individuo:
                    poblacion.append(individuo)
            
            if not poblacion:
                raise Exception("No se pudo generar población inicial válida")
            
            fitness_historia = []
            
            for generacion in range(self.generaciones):
                fitness_scores = []
                for ind in poblacion:
                    try:
                        fitness = self.calcular_fitness(ind)
                        fitness_scores.append((ind, fitness))
                    except Exception:
                        fitness_scores.append((ind, 0.0))
                
                fitness_scores.sort(key=lambda x: x[1], reverse=True)
                
                mejor_fitness = fitness_scores[0][1]
                fitness_promedio = np.mean([score for _, score in fitness_scores])
                fitness_historia.append({
                    'generacion': generacion,
                    'mejor': mejor_fitness,
                    'promedio': fitness_promedio
                })
                
                elite_size = max(1, self.tam_poblacion // 10)
                elite = [ind for ind, _ in fitness_scores[:elite_size]]
                
                nueva_poblacion = [ind.copy() for ind in elite]
                
                while len(nueva_poblacion) < self.tam_poblacion:
                    try:
                        padre1 = self.seleccion_torneo(fitness_scores)
                        padre2 = self.seleccion_torneo(fitness_scores)
                        
                        hijo = self.cruzamiento(padre1, padre2)
                        hijo = self.mutacion(hijo)
                        
                        nueva_poblacion.append(hijo)
                    except Exception:
                        if elite:
                            nueva_poblacion.append(elite[0].copy())
                
                poblacion = nueva_poblacion
            
            fitness_final = []
            for ind in poblacion:
                try:
                    fitness = self.calcular_fitness(ind)
                    fitness_final.append((ind, fitness))
                except Exception:
                    fitness_final.append((ind, 0.0))
            
            fitness_final.sort(key=lambda x: x[1], reverse=True)
            
            return fitness_final[0][0], fitness_historia
            
        except Exception:
            solucion_basica = self.generar_individuo()
            return solucion_basica, [{'generacion': 0, 'mejor': 0.0, 'promedio': 0.0}]
    
    def ajustar_pesos(self, **nuevos_pesos):
        for categoria, peso in nuevos_pesos.items():
            if categoria in self.pesos:
                self.pesos[categoria] = peso