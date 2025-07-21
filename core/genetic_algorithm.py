import random
from typing import List, Dict
from models import Roommate, Tarea, EspacioHogar

class AlgoritmoGenetico:
    def __init__(self, roommates: List[Roommate], tareas: List[Tarea], 
                 tam_poblacion: int = 50, generaciones: int = 30, espacio: EspacioHogar = None):
        
        self.roommates = roommates
        self.tareas = tareas
        self.espacio = espacio or EspacioHogar()  # Espacio por defecto si no se proporciona
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        
        # Ajustar tareas según el espacio (si tiene métodos espaciales)
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            self.tareas_ajustadas = self._ajustar_tareas_por_espacio()
        else:
            self.tareas_ajustadas = self.tareas
        
        # Pesos del algoritmo con consideración espacial
        factor_rotacion = getattr(self.espacio, 'get_factor_rotacion_complejidad', lambda: 1.0)()
        
        self.pesos = {
            'equidad': 25,
            'compatibilidad': 25,
            'habilidades': 20,
            'cocina_diaria': 15,
            'preferencias': 10,
            'rotacion_espacial': int(5 * factor_rotacion)
        }
        
        # Constantes del dominio
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.semanas = [1, 2, 3, 4]
        self.intervalos_30min = self._generar_intervalos_30min()
    
    def _generar_intervalos_30min(self):
        """Genera intervalos de 30 minutos"""
        intervalos = []
        for hora in range(6, 24):
            intervalos.extend([hora, hora + 0.5])
        return intervalos
    
    def _ajustar_tareas_por_espacio(self):
        """Ajusta tareas según características del espacio"""
        tareas_ajustadas = []
        
        # Ajustar tareas existentes
        for tarea in self.tareas:
            tarea_ajustada = Tarea(
                nombre=tarea.nombre,
                frecuencia=tarea.frecuencia,
                tiempo_estimado=self._calcular_tiempo_ajustado(tarea),
                dificultad=tarea.dificultad,
                categoria=tarea.categoria,
                es_predeterminada=tarea.es_predeterminada
            )
            tareas_ajustadas.append(tarea_ajustada)
        
        # Agregar tareas específicas del espacio (si el método existe)
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            tareas_espaciales = self.espacio.generar_tareas_espaciales()
            tareas_ajustadas.extend(tareas_espaciales)
        
        return tareas_ajustadas
    
    def _calcular_tiempo_ajustado(self, tarea: Tarea) -> int:
        """Calcula tiempo ajustado según espacio"""
        tiempo_base = tarea.tiempo_estimado
        
        # Aplicar factor espacial si existe
        if hasattr(self.espacio, 'get_factor_tiempo_limpieza') and tarea.categoria == "Limpieza":
            factor_espacio = self.espacio.get_factor_tiempo_limpieza()
            tiempo_base = int(tiempo_base * factor_espacio)
        
        # Aplicar factor de equipamiento si existe
        if hasattr(self.espacio, 'get_factor_equipamiento'):
            factor_equipamiento = self.espacio.get_factor_equipamiento(tarea.categoria)
            tiempo_base = int(tiempo_base * factor_equipamiento)
        
        # Redondear a intervalos de 30 minutos
        return ((tiempo_base + 29) // 30) * 30
    
    def ejecutar(self):
        """Ejecuta el algoritmo genético"""
        # Inicializar población
        poblacion = [self.generar_individuo() for _ in range(self.tam_poblacion)]
        
        historia_fitness = []
        
        for generacion in range(self.generaciones):
            # Evaluar fitness
            fitness_poblacion = [(individuo, self.calcular_fitness(individuo)) for individuo in poblacion]
            fitness_poblacion.sort(key=lambda x: x[1], reverse=True)
            
            # Registrar estadísticas
            fitness_scores = [f[1] for f in fitness_poblacion]
            historia_fitness.append({
                'generacion': generacion,
                'mejor': max(fitness_scores),
                'promedio': sum(fitness_scores) / len(fitness_scores)
            })
            
            # Crear nueva generación
            nueva_poblacion = []
            
            # Mantener los mejores (elitismo)
            elites = int(self.tam_poblacion * 0.1)
            nueva_poblacion.extend([ind[0] for ind in fitness_poblacion[:elites]])
            
            # Generar resto por crossover y mutación
            while len(nueva_poblacion) < self.tam_poblacion:
                padre1 = self._seleccion_tournament(fitness_poblacion)
                padre2 = self._seleccion_tournament(fitness_poblacion)
                hijo = self._crossover(padre1, padre2)
                hijo = self._mutacion(hijo)
                nueva_poblacion.append(hijo)
            
            poblacion = nueva_poblacion
        
        # Retornar mejor solución
        fitness_final = [(individuo, self.calcular_fitness(individuo)) for individuo in poblacion]
        mejor_individuo = max(fitness_final, key=lambda x: x[1])[0]
        
        return mejor_individuo, historia_fitness
    
    def generar_individuo(self):
        """Genera un individuo aleatorio (cronograma)"""
        asignaciones = {}
        
        # Garantizar cocina diaria
        self._garantizar_cocina_diaria(asignaciones)
        
        # Asignar resto de tareas
        for tarea in self.tareas_ajustadas:
            if tarea.categoria != 'Cocina':
                self._asignar_tarea_mensual(tarea, asignaciones)
        
        return asignaciones
    
    def _garantizar_cocina_diaria(self, asignaciones: Dict):
        """Garantiza al menos una tarea de cocina por día"""
        tareas_cocina = [t for t in self.tareas_ajustadas if t.categoria == 'Cocina']
        
        if not tareas_cocina:
            return
        
        for semana in self.semanas:
            for dia in self.dias_semana:
                tarea_cocina = random.choice(tareas_cocina)
                roommate = self._seleccionar_roommate_optimo(dia, tarea_cocina)
                hora = self._seleccionar_hora_optima(roommate, dia, tarea_cocina)
                
                key = f"cocina_S{semana}_{dia}_{hora}"
                asignaciones[key] = {
                    'tarea': tarea_cocina.nombre,
                    'roommate': roommate.nombre,
                    'dia': dia,
                    'semana': semana,
                    'hora': hora,
                    'duracion': tarea_cocina.tiempo_estimado
                }
    
    def _asignar_tarea_mensual(self, tarea: Tarea, asignaciones: Dict):
        """Asigna tarea según su frecuencia mensual"""
        repeticiones = tarea.get_repeticiones_mensuales() if hasattr(tarea, 'get_repeticiones_mensuales') else 1
        
        for rep in range(repeticiones):
            semana = random.choice(self.semanas)
            dia = random.choice(self.dias_semana)
            roommate = self._seleccionar_roommate_optimo(dia, tarea)
            hora = self._seleccionar_hora_optima(roommate, dia, tarea)
            
            key = f"{tarea.nombre}_S{semana}_{rep}_{random.randint(1000,9999)}"
            asignaciones[key] = {
                'tarea': tarea.nombre,
                'roommate': roommate.nombre,
                'dia': dia,
                'semana': semana,
                'hora': hora,
                'duracion': tarea.tiempo_estimado
            }
    
    def _seleccionar_roommate_optimo(self, dia: str, tarea: Tarea) -> Roommate:
        """Selecciona roommate óptimo considerando restricciones"""
        candidatos = []
        
        for roommate in self.roommates:
            # Verificar restricciones médicas
            if (hasattr(roommate, 'restricciones_medicas') and 
                roommate.restricciones_medicas and 
                tarea.categoria in roommate.restricciones_medicas):
                continue
            
            habilidad = roommate.get_habilidad(tarea.categoria)
            preferencia = roommate.get_preferencia(tarea.categoria)
            
            score = habilidad
            if preferencia == 'prefiere':
                score += 3
            elif preferencia == 'evita':
                score -= 3
            
            candidatos.append((roommate, score))
        
        if not candidatos:
            return random.choice(self.roommates)
        
        candidatos.sort(key=lambda x: x[1], reverse=True)
        top_candidatos = candidatos[:min(3, len(candidatos))]
        return random.choice(top_candidatos)[0]
    
    def _seleccionar_hora_optima(self, roommate: Roommate, dia: str, tarea: Tarea) -> float:
        """Selecciona hora óptima en intervalos de 30 min"""
        if dia not in roommate.horarios_disponibles:
            return 12.0  # Mediodía por defecto
        
        rangos = roommate.horarios_disponibles[dia]
        if not rangos:
            return 12.0
        
        # Buscar horarios disponibles en intervalos de 30 min
        horas_disponibles = []
        for rango in rangos:
            hora_actual = rango.inicio
            while hora_actual < rango.fin:
                # Verificar que sea múltiplo de 0.5 (intervalos de 30 min)
                if hora_actual % 0.5 == 0:
                    horas_disponibles.append(hora_actual)
                hora_actual += 0.5
        
        if horas_disponibles:
            return random.choice(horas_disponibles)
        
        return 12.0
    
    def calcular_fitness(self, individuo: Dict) -> float:
        """Calcula fitness del individuo"""
        if not individuo:
            return 0.0
        
        try:
            fitness_componentes = {
                'equidad': self._fitness_equidad(individuo),
                'compatibilidad': self._fitness_compatibilidad(individuo),
                'habilidades': self._fitness_habilidades(individuo),
                'cocina_diaria': self._fitness_cocina_diaria(individuo),
                'preferencias': self._fitness_preferencias(individuo),
                'rotacion_espacial': self._fitness_rotacion_espacial(individuo)
            }
            
            fitness_total = sum(
                fitness_componentes[componente] * self.pesos[componente]
                for componente in fitness_componentes
            )
            
            return max(0, fitness_total)
            
        except Exception:
            return 0.0
    
    def _fitness_equidad(self, individuo: Dict) -> float:
        """Calcula fitness de equidad"""
        cargas = {rm.nombre: 0 for rm in self.roommates}
        
        for asig in individuo.values():
            cargas[asig['roommate']] += asig['duracion']
        
        if not cargas:
            return 0.0
        
        carga_promedio = sum(cargas.values()) / len(cargas)
        varianza = sum((carga - carga_promedio) ** 2 for carga in cargas.values()) / len(cargas)
        
        return 1.0 / (1.0 + varianza / 1000)
    
    def _fitness_compatibilidad(self, individuo: Dict) -> float:
        """Calcula fitness de compatibilidad horaria"""
        score_total = 0
        asignaciones_validas = 0
        
        for asig in individuo.values():
            roommate = next((rm for rm in self.roommates if rm.nombre == asig['roommate']), None)
            if not roommate:
                continue
            
            dia = asig['dia']
            hora = asig['hora']
            
            if dia in roommate.horarios_disponibles:
                for rango in roommate.horarios_disponibles[dia]:
                    if rango.inicio <= hora < rango.fin:
                        score_total += 1
                        break
            
            asignaciones_validas += 1
        
        return score_total / asignaciones_validas if asignaciones_validas > 0 else 0
    
    def _fitness_habilidades(self, individuo: Dict) -> float:
        """Calcula fitness de habilidades"""
        score_total = 0
        roommates_dict = {rm.nombre: rm for rm in self.roommates}
        
        for asig in individuo.values():
            roommate_obj = roommates_dict.get(asig['roommate'])
            tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
            
            if roommate_obj and tarea_obj:
                habilidad = roommate_obj.get_habilidad(tarea_obj.categoria)
                score_total += habilidad / 10.0
        
        return score_total / len(individuo) if individuo else 0
    
    def _fitness_cocina_diaria(self, individuo: Dict) -> float:
        """Calcula fitness de cocina diaria"""
        dias_con_cocina = set()
        
        for asig in individuo.values():
            tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
            if tarea_obj and tarea_obj.categoria == 'Cocina':
                dias_con_cocina.add(f"S{asig['semana']}_{asig['dia']}")
        
        total_dias_posibles = len(self.semanas) * len(self.dias_semana)
        return len(dias_con_cocina) / total_dias_posibles
    
    def _fitness_preferencias(self, individuo: Dict) -> float:
        """Calcula fitness de preferencias"""
        score_total = 0
        roommates_dict = {rm.nombre: rm for rm in self.roommates}
        
        for asig in individuo.values():
            roommate_obj = roommates_dict.get(asig['roommate'])
            tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
            
            if roommate_obj and tarea_obj:
                preferencia = roommate_obj.get_preferencia(tarea_obj.categoria)
                if preferencia == 'prefiere':
                    score_total += 1.0
                elif preferencia == 'evita':
                    score_total -= 0.5
                else:  # neutro
                    score_total += 0.5
        
        return max(0, score_total) / len(individuo) if individuo else 0
    
    def _fitness_rotacion_espacial(self, individuo: Dict) -> float:
        """Calcula fitness de rotación considerando espacio"""
        factor_complejidad = 1.0
        if hasattr(self.espacio, 'get_factor_rotacion_complejidad'):
            factor_complejidad = self.espacio.get_factor_rotacion_complejidad()
        
        # Calcular diversidad de asignaciones
        diversidad_por_semana = {}
        
        for semana in self.semanas:
            asignaciones_semana = [asig for asig in individuo.values() if asig['semana'] == semana]
            
            categorias_roommates = {}
            for asig in asignaciones_semana:
                tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
                if tarea_obj:
                    categoria = tarea_obj.categoria
                    if categoria not in categorias_roommates:
                        categorias_roommates[categoria] = set()
                    categorias_roommates[categoria].add(asig['roommate'])
            
            diversidad_total = 0
            for categoria, roommates_set in categorias_roommates.items():
                diversidad_categoria = len(roommates_set) / len(self.roommates)
                diversidad_categoria *= factor_complejidad
                diversidad_total += diversidad_categoria
            
            diversidad_por_semana[semana] = diversidad_total
        
        diversidad_promedio = sum(diversidad_por_semana.values()) / len(self.semanas)
        return min(1.0, diversidad_promedio / len(set(t.categoria for t in self.tareas_ajustadas)))
    
    def _seleccion_tournament(self, fitness_poblacion):
        """Selección por tournament"""
        tournament_size = 3
        tournament = random.sample(fitness_poblacion, min(tournament_size, len(fitness_poblacion)))
        return max(tournament, key=lambda x: x[1])[0]
    
    def _crossover(self, padre1, padre2):
        """Crossover entre dos individuos"""
        hijo = {}
        
        for key in padre1:
            if random.random() < 0.5:
                hijo[key] = padre1[key].copy()
            elif key in padre2:
                hijo[key] = padre2[key].copy()
            else:
                hijo[key] = padre1[key].copy()
        
        return hijo
    
    def _mutacion(self, individuo):
        """Mutación de un individuo"""
        if random.random() < 0.1:  # 10% probabilidad de mutación
            keys = list(individuo.keys())
            if keys:
                key_mutar = random.choice(keys)
                asig = individuo[key_mutar]
                
                # Mutar roommate
                if random.random() < 0.5:
                    tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
                    if tarea_obj:
                        nuevo_roommate = self._seleccionar_roommate_optimo(asig['dia'], tarea_obj)
                        asig['roommate'] = nuevo_roommate.nombre
                
                # Mutar hora
                else:
                    roommate_obj = next((rm for rm in self.roommates if rm.nombre == asig['roommate']), None)
                    tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
                    if roommate_obj and tarea_obj:
                        nueva_hora = self._seleccionar_hora_optima(roommate_obj, asig['dia'], tarea_obj)
                        asig['hora'] = nueva_hora
        
        return individuo