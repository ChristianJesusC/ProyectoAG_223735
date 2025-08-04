import random
import time
import numpy as np
from typing import List, Dict, Tuple, Callable, Optional, Set
from collections import defaultdict
from functools import lru_cache
from models import Roommate, Tarea, EspacioHogar

class AlgoritmoGenetico:
    def __init__(self, roommates: List[Roommate], tareas: List[Tarea], 
                 tam_poblacion: int = 50, generaciones: int = 30, espacio: EspacioHogar = None):
        
        self.roommates = roommates
        self.tareas = tareas
        self.espacio = espacio or EspacioHogar()
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        
        self._precomputar_datos()
        
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            self.tareas_ajustadas = self._ajustar_tareas_por_espacio()
        else:
            self.tareas_ajustadas = self.tareas
        
        factor_rotacion = self.espacio.get_factor_rotacion_complejidad()
        self.pesos = {
            'equidad': 25,
            'compatibilidad': 25,
            'habilidades': 20,
            'cocina_diaria': 15,
            'preferencias': 10,
            'rotacion_espacial': int(5 * factor_rotacion)
        }
        
        self.pmi_base = 0.12
        self.pmg_base = 0.18
        self.factor_adaptacion = 0.6
        
        self._fitness_cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _precomputar_datos(self):
        self.dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.semanas = [1, 2, 3, 4]
        
        self.intervalos_30min = []
        for hora in range(6, 24):
            self.intervalos_30min.extend([hora, hora + 0.5])
        
        self.roommates_dict = {rm.nombre: rm for rm in self.roommates}
        self.tareas_dict = {t.nombre: t for t in self.tareas}
        
        self._precompute_horarios_validos()
        
        self.tareas_cocina_nombres = set()
        for tarea in self.tareas:
            if tarea.categoria == 'Cocina':
                self.tareas_cocina_nombres.add(tarea.nombre)
    
    def _precompute_horarios_validos(self):
        self.horarios_validos = {}
        
        for roommate in self.roommates:
            self.horarios_validos[roommate.nombre] = {}
            
            for dia in self.dias_semana:
                horas_validas = set()
                if dia in roommate.horarios_disponibles:
                    for rango in roommate.horarios_disponibles[dia]:
                        hora_actual = rango.inicio
                        while hora_actual < rango.fin:
                            if hora_actual % 0.5 == 0:  
                                horas_validas.add(hora_actual)
                            hora_actual += 0.5
                
                self.horarios_validos[roommate.nombre][dia] = horas_validas
    
    def _get_individuo_hash(self, individuo: Dict) -> str:
            items = []
            for key in sorted(individuo.keys()):
                asig = individuo[key]
                items.append(f"{key}:{asig['tarea']}:{asig['roommate']}:{asig['dia']}:{asig['semana']}:{asig['hora']}:{asig['duracion']}")
            return hash(tuple(items))
    
    def _ajustar_tareas_por_espacio(self):
        tareas_ajustadas = []
        
        factor_limpieza = self.espacio.get_factor_tiempo_limpieza()
        factores_equipamiento = {
            categoria: self.espacio.get_factor_equipamiento(categoria)
            for categoria in ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
        }
        
        for tarea in self.tareas:
            tiempo_ajustado = tarea.tiempo_estimado
            
            if tarea.categoria == "Limpieza":
                tiempo_ajustado = int(tiempo_ajustado * factor_limpieza)
            
            factor_equip = factores_equipamiento.get(tarea.categoria, 1.0)
            tiempo_ajustado = int(tiempo_ajustado * factor_equip)
            
            tiempo_ajustado = ((tiempo_ajustado + 29) // 30) * 30
            
            tarea_ajustada = Tarea(
                nombre=tarea.nombre,
                frecuencia=tarea.frecuencia,
                tiempo_estimado=tiempo_ajustado,
                dificultad=tarea.dificultad,
                categoria=tarea.categoria,
                es_predeterminada=tarea.es_predeterminada
            )
            tareas_ajustadas.append(tarea_ajustada)
        
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            tareas_espaciales = self.espacio.generar_tareas_espaciales()
            tareas_ajustadas.extend(tareas_espaciales)
        
        self.tareas_dict.update({t.nombre: t for t in tareas_ajustadas})
        
        return tareas_ajustadas
    
    def ejecutar(self, callback_progreso: Optional[Callable] = None):
        poblacion = self._generar_poblacion_inicial()
        historia_fitness = []
        
        if callback_progreso:
            callback_progreso(0, {
                'estado': 'Inicializando población optimizada...',
                'sub_estado': f'Creando {self.tam_poblacion} cronogramas',
                'generacion': 0,
                'total_generaciones': self.generaciones,
                'progreso': 0,
                'mejor_fitness': 0,
                'promedio_fitness': 0,
                'diversidad': 1.0,
                'tiempo_estimado': self.generaciones * 1.5 
            })
        
        for generacion in range(self.generaciones):
            tiempo_inicio = time.time()
            
            if callback_progreso:
                callback_progreso(generacion, {
                    'estado': f'Generación {generacion + 1}/{self.generaciones}',
                    'sub_estado': 'Evaluando fitness (con cache)',
                    'generacion': generacion,
                    'total_generaciones': self.generaciones,
                    'progreso': (generacion / self.generaciones) * 100
                })
            
            fitness_poblacion = self._evaluar_poblacion_con_cache(poblacion)
            
            fitness_scores = [f[1] for f in fitness_poblacion]
            diversidad = self._calcular_diversidad(fitness_poblacion)
            
            estadisticas = {
                'generacion': generacion,
                'mejor': max(fitness_scores),
                'promedio': np.mean(fitness_scores),
                'peor': min(fitness_scores),
                'diversidad': diversidad,
                'desviacion': np.std(fitness_scores)
            }
            
            historia_fitness.append(estadisticas)
            
            if generacion % 5 == 0:
                cache_ratio = self._cache_hits / max(1, self._cache_hits + self._cache_misses)
                print(f"Gen {generacion}: Top={estadisticas['mejor']:.1f}, "
                      f"Avg={estadisticas['promedio']:.1f}, Cache={cache_ratio:.2%}")
            
            if callback_progreso:
                tiempo_generacion = time.time() - tiempo_inicio
                tiempo_restante = (self.generaciones - generacion - 1) * tiempo_generacion
                mejora = self._calcular_mejora(historia_fitness) if len(historia_fitness) > 1 else 0
                
                callback_progreso(generacion, {
                    'estado': f'Generación {generacion + 1}/{self.generaciones}',
                    'sub_estado': 'Evolucionando población (optimizado)',
                    'progreso': ((generacion + 1) / self.generaciones) * 100,
                    'generacion': generacion + 1,
                    'total_generaciones': self.generaciones,
                    'mejor_fitness': estadisticas['mejor'],
                    'promedio_fitness': estadisticas['promedio'],
                    'peor_fitness': estadisticas['peor'],
                    'diversidad': diversidad,
                    'tiempo_restante': max(0, tiempo_restante),
                    'mejora': mejora,
                    'desviacion': estadisticas['desviacion']
                })
            
            if self._detectar_convergencia_temprana(historia_fitness):
                if callback_progreso:
                    callback_progreso(generacion, {
                        'estado': '🎯 Convergencia alcanzada',
                        'sub_estado': 'Solución óptima encontrada',
                        'progreso': 100,
                        'convergencia_temprana': True,
                        'generacion_final': generacion + 1
                    })
                break
            
            poblacion = self._generar_nueva_poblacion(fitness_poblacion, generacion)
        
        if callback_progreso:
            callback_progreso(self.generaciones, {
                'estado': '✅ Optimización completada',
                'sub_estado': f'Cache efficiency: {self._cache_hits/(self._cache_hits+self._cache_misses):.1%}',
                'progreso': 100,
                'finalizado': True,
                'generaciones_totales': len(historia_fitness)
            })
        
        fitness_final = self._evaluar_poblacion_con_cache(poblacion)
        mejor_individuo = max(fitness_final, key=lambda x: x[1])[0]
        
        return mejor_individuo, historia_fitness
    
    def _generar_poblacion_inicial(self):
        poblacion = []
        
        tareas_cocina = [t for t in self.tareas_ajustadas if t.categoria == 'Cocina']
        tareas_no_cocina = [t for t in self.tareas_ajustadas if t.categoria != 'Cocina']
        
        for _ in range(self.tam_poblacion):
            individuo = {}
            
            self._garantizar_cocina_diaria(individuo, tareas_cocina)
            
            for tarea in tareas_no_cocina:
                self._asignar_tarea_mensual(tarea, individuo)
            
            poblacion.append(individuo)
        
        return poblacion
    
    def _garantizar_cocina_diaria(self, asignaciones: Dict, tareas_cocina: List[Tarea]):
        if not tareas_cocina:
            return
        
        for semana in self.semanas:
            for dia in self.dias_semana:
                tarea_cocina = random.choice(tareas_cocina)
                roommate = self._seleccionar_roommate_optimo(dia, tarea_cocina)
                hora = self._seleccionar_hora_optima(roommate.nombre, dia)
                
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
        repeticiones = self._get_repeticiones_mensuales(tarea)
        
        for rep in range(repeticiones):
            semana = random.choice(self.semanas)
            dia = random.choice(self.dias_semana)
            roommate = self._seleccionar_roommate_optimo(dia, tarea)
            hora = self._seleccionar_hora_optima(roommate.nombre, dia)
            
            key = f"{tarea.nombre}_S{semana}_{rep}_{random.randint(1000,9999)}"
            asignaciones[key] = {
                'tarea': tarea.nombre,
                'roommate': roommate.nombre,
                'dia': dia,
                'semana': semana,
                'hora': hora,
                'duracion': tarea.tiempo_estimado
            }
    
    def _get_repeticiones_mensuales(self, tarea: Tarea) -> int:
        if tarea.frecuencia == 'diaria':
            return 28
        elif tarea.frecuencia == 'semanal':
            return 4
        elif tarea.frecuencia == 'mensual':
            return 1
        return 1
    
    def _seleccionar_roommate_optimo(self, dia: str, tarea: Tarea) -> Roommate:
        mejores_candidatos = []
        
        for roommate in self.roommates:
            if (hasattr(roommate, 'restricciones_medicas') and 
                roommate.restricciones_medicas and 
                tarea.categoria in roommate.restricciones_medicas):
                continue
            
            habilidad = roommate.habilidades.get(tarea.categoria, 5)
            preferencia = roommate.preferencias.get(tarea.categoria, 'neutro')
            
            score = habilidad
            if preferencia == 'prefiere':
                score += 3
            elif preferencia == 'evita':
                score -= 3
            
            mejores_candidatos.append((roommate, score))
        
        if not mejores_candidatos:
            return random.choice(self.roommates)
        
        if len(mejores_candidatos) > 10:
            scores = np.array([score for _, score in mejores_candidatos])
            indices_top = np.argsort(scores)[-3:]
            candidatos_finales = [mejores_candidatos[i] for i in indices_top]
        else:
            mejores_candidatos.sort(key=lambda x: x[1], reverse=True)
            candidatos_finales = mejores_candidatos[:3]
        
        return random.choice(candidatos_finales)[0]
    
    def _seleccionar_hora_optima(self, roommate_nombre: str, dia: str) -> float:
        horas_validas = self.horarios_validos.get(roommate_nombre, {}).get(dia, set())
        
        if not horas_validas:
            return 12.0
        
        return random.choice(list(horas_validas))
    
    def _evaluar_poblacion_con_cache(self, poblacion: List[Dict]) -> List[Tuple[Dict, float]]:
        resultados = []
        
        for individuo in poblacion:
            hash_individuo = self._get_individuo_hash(individuo)
            
            if hash_individuo in self._fitness_cache:
                fitness = self._fitness_cache[hash_individuo]
                self._cache_hits += 1
            else:
                fitness = self.calcular_fitness(individuo)
                self._fitness_cache[hash_individuo] = fitness
                self._cache_misses += 1
            
            resultados.append((individuo, fitness))
        
        if len(resultados) > 50:
            fitness_array = np.array([r[1] for r in resultados])
            indices_ordenados = np.argsort(fitness_array)[::-1]
            return [resultados[i] for i in indices_ordenados]
        else:
            return sorted(resultados, key=lambda x: x[1], reverse=True)
    
    def calcular_fitness(self, individuo: Dict) -> float:
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
        cargas = defaultdict(int)
        
        for asig in individuo.values():
            cargas[asig['roommate']] += asig['duracion']
        
        if not cargas:
            return 0.0
        
        cargas_array = np.array(list(cargas.values()))
        varianza = np.var(cargas_array)
        
        return 1.0 / (1.0 + varianza / 1000)
    
    def _fitness_compatibilidad(self, individuo: Dict) -> float:
        score_total = 0
        asignaciones_validas = 0
        
        for asig in individuo.values():
            roommate_nombre = asig['roommate']
            dia = asig['dia']
            hora = asig['hora']
            
            horas_validas = self.horarios_validos.get(roommate_nombre, {}).get(dia, set())
            
            if hora in horas_validas:
                score_total += 1
            
            asignaciones_validas += 1
        
        return score_total / asignaciones_validas if asignaciones_validas > 0 else 0
    
    def _fitness_habilidades(self, individuo: Dict) -> float:
        score_total = 0
        num_asignaciones = len(individuo)
        
        for asig in individuo.values():
            roommate_obj = self.roommates_dict.get(asig['roommate'])
            tarea_obj = self.tareas_dict.get(asig['tarea'])
            
            if roommate_obj and tarea_obj:
                habilidad = roommate_obj.habilidades.get(tarea_obj.categoria, 5)
                score_total += habilidad / 10.0
        
        return score_total / num_asignaciones if num_asignaciones > 0 else 0
    
    def _fitness_cocina_diaria(self, individuo: Dict) -> float:
        dias_con_cocina = set()
        
        for asig in individuo.values():
            if asig['tarea'] in self.tareas_cocina_nombres:
                dias_con_cocina.add(f"S{asig['semana']}_{asig['dia']}")
        
        total_dias_posibles = len(self.semanas) * len(self.dias_semana)
        return len(dias_con_cocina) / total_dias_posibles
    
    def _fitness_preferencias(self, individuo: Dict) -> float:
        score_total = 0
        
        for asig in individuo.values():
            roommate_obj = self.roommates_dict.get(asig['roommate'])
            tarea_obj = self.tareas_dict.get(asig['tarea'])
            
            if roommate_obj and tarea_obj:
                preferencia = roommate_obj.preferencias.get(tarea_obj.categoria, 'neutro')
                if preferencia == 'prefiere':
                    score_total += 1.0
                elif preferencia == 'evita':
                    score_total -= 0.5
                else:
                    score_total += 0.5
        
        return max(0, score_total) / len(individuo) if individuo else 0
    
    def _fitness_rotacion_espacial(self, individuo: Dict) -> float:
        factor_complejidad = self.espacio.get_factor_rotacion_complejidad()
        
        diversidad_por_semana = defaultdict(lambda: defaultdict(set))
        
        for asig in individuo.values():
            tarea_obj = self.tareas_dict.get(asig['tarea'])
            if tarea_obj:
                semana = asig['semana']
                categoria = tarea_obj.categoria
                roommate = asig['roommate']
                
                diversidad_por_semana[semana][categoria].add(roommate)
        
        total_diversidad = 0
        num_roommates = len(self.roommates)
        
        for semana in self.semanas:
            diversidad_semana = 0
            for categoria, roommates_set in diversidad_por_semana[semana].items():
                diversidad_categoria = len(roommates_set) / num_roommates
                diversidad_categoria *= factor_complejidad
                diversidad_semana += diversidad_categoria
            
            total_diversidad += diversidad_semana
        
        diversidad_promedio = total_diversidad / len(self.semanas)
        num_categorias = len(set(t.categoria for t in self.tareas_ajustadas))
        
        return min(1.0, diversidad_promedio / num_categorias)
    
    def _calcular_diversidad(self, fitness_poblacion: List[Tuple]) -> float:
        if len(fitness_poblacion) < 2:
            return 1.0
        
        individuos = [ind for ind, _ in fitness_poblacion]
        
        if len(individuos) > 30:
            muestra = random.sample(individuos, 30)
        else:
            muestra = individuos
        
        distancias = []
        for i in range(len(muestra)):
            for j in range(i + 1, len(muestra)):
                dist = self._distancia_hamming(muestra[i], muestra[j])
                distancias.append(dist)
        
        return np.mean(distancias) if distancias else 0.0
    
    def _distancia_hamming(self, cronograma1: Dict, cronograma2: Dict) -> float:
        if not cronograma1 or not cronograma2:
            return 1.0
        
        keys_comunes = set(cronograma1.keys()) & set(cronograma2.keys())
        if not keys_comunes:
            return 1.0
        
        diferencias = 0
        total_comparaciones = 0
        
        for key in keys_comunes:
            asig1 = cronograma1[key]
            asig2 = cronograma2[key]
            
            if asig1['roommate'] != asig2['roommate']:
                diferencias += 1
            if abs(asig1['hora'] - asig2['hora']) > 0.5:
                diferencias += 1
            if asig1['dia'] != asig2['dia']:
                diferencias += 1
            
            total_comparaciones += 3
        
        return diferencias / total_comparaciones if total_comparaciones > 0 else 0
    
    def _generar_nueva_poblacion(self, fitness_poblacion: List[Tuple], generacion: int):
        parejas = self._emparejamiento_selectivo_mejorado(fitness_poblacion)
        
        descendencia = []
        for padre1, padre2 in parejas:
            hijo1 = self._cruza_multipunto_aleatorio(padre1, padre2)
            hijo2 = self._cruza_multipunto_aleatorio(padre2, padre1)
            
            hijo1 = self._mutacion_adaptativa(hijo1, generacion)
            hijo2 = self._mutacion_adaptativa(hijo2, generacion)
            
            descendencia.extend([hijo1, hijo2])
        
        padres = [ind for ind, _ in fitness_poblacion]
        poblacion_extendida = padres + descendencia
        
        return self._poda_elitista(poblacion_extendida)
    
    def _cruza_multipunto_aleatorio(self, padre1: Dict, padre2: Dict) -> Dict:
        fitness_padre1 = self._fitness_cache.get(self._get_individuo_hash(padre1))
        fitness_padre2 = self._fitness_cache.get(self._get_individuo_hash(padre2))
        
        if fitness_padre1 is None:
            fitness_padre1 = self.calcular_fitness(padre1)
        if fitness_padre2 is None:
            fitness_padre2 = self.calcular_fitness(padre2)
        
        keys_padre1 = set(padre1.keys())
        keys_padre2 = set(padre2.keys())
        keys_comunes = list(keys_padre1 & keys_padre2)
        
        if len(keys_comunes) < 3:
            return self._crossover_uniforme(padre1, padre2, fitness_padre1, fitness_padre2)
        
        keys_comunes.sort()
        
        max_puntos = min(5 if fitness_padre1 <= 100 or fitness_padre2 <= 100 else 3, 
                        len(keys_comunes) - 1)
        max_puntos = max(2, max_puntos)
        num_puntos = random.randint(2, max_puntos)
        
        if len(keys_comunes) - 1 < num_puntos:
            return self._crossover_uniforme(padre1, padre2, fitness_padre1, fitness_padre2)
        
        puntos_cruza = sorted(random.sample(range(1, len(keys_comunes)), num_puntos))
        
        hijo = {}
        usar_mejor_padre = fitness_padre1 >= fitness_padre2
        inicio = 0
        
        for punto in puntos_cruza + [len(keys_comunes)]:
            padre_actual = padre1 if usar_mejor_padre else padre2
            
            for i in range(inicio, punto):
                key = keys_comunes[i]
                if key in padre_actual:
                    hijo[key] = padre_actual[key].copy()
            
            if random.random() < 0.7:
                usar_mejor_padre = not usar_mejor_padre
            inicio = punto
        
        self._agregar_claves_unicas(hijo, padre1, padre2, 
                                              set(keys_comunes), fitness_padre1, fitness_padre2)
        
        return self._reparar_cronograma_basico(hijo)
    
    def _crossover_uniforme(self, padre1: Dict, padre2: Dict, 
                                     fitness1: float, fitness2: float) -> Dict:
        hijo = {}
        probabilidad_mejor = 0.7 if fitness1 > fitness2 else 0.3
        padre_mejor = padre1 if fitness1 > fitness2 else padre2
        padre_peor = padre2 if fitness1 > fitness2 else padre1
        
        for key in padre_mejor:
            if random.random() < probabilidad_mejor:
                hijo[key] = padre_mejor[key].copy()
            elif key in padre_peor:
                hijo[key] = padre_peor[key].copy()
            else:
                hijo[key] = padre_mejor[key].copy()
        
        return hijo
    
    def _agregar_claves_unicas(self, hijo: Dict, padre1: Dict, padre2: Dict,
                                        keys_comunes_set: Set, fitness1: float, fitness2: float):
        if fitness1 > fitness2:
            prob_padre1, prob_padre2 = 0.75, 0.25
        elif fitness2 > fitness1:
            prob_padre1, prob_padre2 = 0.25, 0.75
        else:
            prob_padre1, prob_padre2 = 0.6, 0.4
        
        keys_unicas_padre1 = set(padre1.keys()) - keys_comunes_set
        keys_unicas_padre2 = set(padre2.keys()) - keys_comunes_set
        
        for key in keys_unicas_padre1:
            if random.random() < prob_padre1:
                hijo[key] = padre1[key].copy()
        
        for key in keys_unicas_padre2:
            if key not in hijo and random.random() < prob_padre2:
                hijo[key] = padre2[key].copy()
    
    def _mutacion_adaptativa(self, individuo: Dict, generacion: Optional[int] = None) -> Dict:
        hash_individuo = self._get_individuo_hash(individuo)
        fitness_individuo = self._fitness_cache.get(hash_individuo)
        
        if fitness_individuo is None:
            fitness_individuo = self.calcular_fitness(individuo)
        
        if fitness_individuo > 120:
            factor_proteccion = 0.2
            tipo_individuo = "excelente"
        elif fitness_individuo > 100:
            factor_proteccion = 0.4 
            tipo_individuo = "bueno"
        elif fitness_individuo > 80:
            factor_proteccion = 0.7
            tipo_individuo = "regular"
        else:
            factor_proteccion = 1.2 
            tipo_individuo = "malo"
        
        if generacion is not None:
            factor_gen = 1.0 - (generacion / self.generaciones) * self.factor_adaptacion
            pmi_actual = self.pmi_base * factor_gen * factor_proteccion
        else:
            pmi_actual = self.pmi_base * factor_proteccion
        
        if random.random() > pmi_actual:
            return individuo
        
        fitness_normalizado = min(1.0, fitness_individuo / 100.0)
        pmg_actual = self.pmg_base * (1.1 - fitness_normalizado) * factor_proteccion
        pmg_actual = max(0.05, min(0.35, pmg_actual))
        
        keys = list(individuo.keys())
        if len(keys) < 2:
            return individuo
        
        num_keys = len(keys)
        probs = np.random.random(num_keys)
        genes_a_mutar = [keys[i] for i in range(num_keys) if probs[i] <= pmg_actual]
        
        if len(genes_a_mutar) < 2:
            return individuo
        
        if tipo_individuo in ["excelente", "bueno"]:
            self._intercambio_suave(individuo, genes_a_mutar)
        else:
            self._intercambiar_genes_aleatorio(individuo, genes_a_mutar)
        
        return self._reparar_cronograma_basico(individuo)
    
    def _intercambio_suave(self, individuo: Dict, genes_disponibles: List[str]):
        if len(genes_disponibles) < 2:
            return
        
        if random.random() < 0.6:
            self._intercambiar_horarios_mismo_dia(individuo, genes_disponibles)
        else:
            self._intercambiar_dias_misma_semana(individuo, genes_disponibles)
    
    def _intercambiar_dias_misma_semana(self, individuo: Dict, genes: List[str]):
        if len(genes) < 2:
            return
        
        genes_por_semana = defaultdict(list)
        for gene in genes:
            semana = individuo[gene]['semana']
            genes_por_semana[semana].append(gene)
        
        for semana, genes_semana in genes_por_semana.items():
            if len(genes_semana) >= 2:
                gene1, gene2 = random.sample(genes_semana, 2)
                individuo[gene1]['dia'], individuo[gene2]['dia'] = \
                    individuo[gene2]['dia'], individuo[gene1]['dia']
    
    def _intercambiar_genes_aleatorio(self, individuo: Dict, genes_disponibles: List[str]):
        rand_val = random.random()
        if rand_val < 0.6:
            self._intercambiar_roommates_compatibles(individuo, genes_disponibles)
        elif rand_val < 0.85:
            self._intercambiar_horarios_mismo_dia(individuo, genes_disponibles)
        else:
            self._intercambiar_dias_semanas(individuo, genes_disponibles)
    
    def _intercambiar_roommates_compatibles(self, individuo: Dict, genes: List[str]):
        if len(genes) < 2:
            return
        
        genes_por_categoria = defaultdict(list)
        for gene in genes:
            tarea_obj = self.tareas_dict.get(individuo[gene]['tarea'])
            if tarea_obj:
                genes_por_categoria[tarea_obj.categoria].append(gene)
        
        for categoria, genes_categoria in genes_por_categoria.items():
            if len(genes_categoria) >= 2:
                gene1, gene2 = random.sample(genes_categoria, 2)
                individuo[gene1]['roommate'], individuo[gene2]['roommate'] = \
                    individuo[gene2]['roommate'], individuo[gene1]['roommate']
    
    def _intercambiar_horarios_mismo_dia(self, individuo: Dict, genes: List[str]):
        if len(genes) < 2:
            return
        
        genes_por_dia = defaultdict(list)
        for gene in genes:
            asig = individuo[gene]
            dia_key = f"S{asig['semana']}_{asig['dia']}"
            genes_por_dia[dia_key].append(gene)
        
        for dia, genes_dia in genes_por_dia.items():
            if len(genes_dia) >= 2:
                gene1, gene2 = random.sample(genes_dia, 2)
                individuo[gene1]['hora'], individuo[gene2]['hora'] = \
                    individuo[gene2]['hora'], individuo[gene1]['hora']
    
    def _intercambiar_dias_semanas(self, individuo: Dict, genes: List[str]):
        if len(genes) < 2:
            return
        
        gene1, gene2 = random.sample(genes, 2)
        
        if random.random() < 0.5:
            individuo[gene1]['dia'], individuo[gene2]['dia'] = \
                individuo[gene2]['dia'], individuo[gene1]['dia']
        else:
            individuo[gene1]['semana'], individuo[gene2]['semana'] = \
                individuo[gene2]['semana'], individuo[gene1]['semana']
    
    def _poda_elitista(self, poblacion_extendida: List[Dict]) -> List[Dict]:
        if len(poblacion_extendida) <= self.tam_poblacion:
            return poblacion_extendida
        
        poblacion_con_fitness = self._evaluar_poblacion_con_cache(poblacion_extendida)
        
        num_elites = max(3, int(self.tam_poblacion * 0.15))
        elites = [ind for ind, _ in poblacion_con_fitness[:num_elites]]
        poblacion_podada = elites.copy()
        
        candidatos_top50 = poblacion_con_fitness[num_elites:int(len(poblacion_con_fitness) * 0.5)]
        if candidatos_top50:
            num_diversos = max(2, int(self.tam_poblacion * 0.08))
            diversos = self._seleccionar_diversos([ind for ind, _ in candidatos_top50], num_diversos)
            poblacion_podada.extend(diversos)
            
            diversos_set = set(id(d) for d in diversos)
            candidatos_restantes = [(ind, fit) for ind, fit in candidatos_top50 
                                  if id(ind) not in diversos_set]
        else:
            candidatos_restantes = []
        
        espacios_restantes = self.tam_poblacion - len(poblacion_podada)
        
        if espacios_restantes > 0 and candidatos_restantes:
            candidatos_bottom = poblacion_con_fitness[int(len(poblacion_con_fitness) * 0.5):]
            todos_candidatos = candidatos_restantes + candidatos_bottom
            
            if todos_candidatos:
                fitness_values = np.array([fit for _, fit in todos_candidatos])
                min_fitness = np.min(fitness_values)
                max_fitness = np.max(fitness_values)
                
                if max_fitness > min_fitness:
                    pesos_normalizados = 0.1 + 0.9 * ((fitness_values - min_fitness) / (max_fitness - min_fitness))
                else:
                    pesos_normalizados = np.ones(len(fitness_values))
                
                indices_seleccionados = np.random.choice(
                    len(todos_candidatos),
                    size=min(espacios_restantes, len(todos_candidatos)),
                    p=pesos_normalizados / np.sum(pesos_normalizados),
                    replace=False
                )
                
                individuos_seleccionados = [todos_candidatos[i][0] for i in indices_seleccionados]
                poblacion_podada.extend(individuos_seleccionados)
        
        return poblacion_podada[:self.tam_poblacion]
    
    def _seleccionar_diversos(self, candidatos: List[Dict], cantidad: int) -> List[Dict]:
        if not candidatos or cantidad <= 0:
            return []
        
        diversos = []
        candidatos_restantes = candidatos.copy()
        
        if candidatos_restantes:
            top_candidates = candidatos_restantes[:max(1, int(len(candidatos_restantes) * 0.3))]
            primer_individuo = random.choice(top_candidates)
            diversos.append(primer_individuo)
            candidatos_restantes.remove(primer_individuo)
        
        while len(diversos) < cantidad and candidatos_restantes:
            if len(candidatos_restantes) > 50:
                muestra_candidatos = random.sample(candidatos_restantes, 50)
            else:
                muestra_candidatos = candidatos_restantes
            
            mejor_candidato = None
            mejor_distancia_minima = -1
            
            for candidato in muestra_candidatos:
                distancias = [self._distancia_hamming(candidato, seleccionado) 
                            for seleccionado in diversos]
                distancia_minima = min(distancias) if distancias else 0
                
                if distancia_minima > mejor_distancia_minima:
                    mejor_distancia_minima = distancia_minima
                    mejor_candidato = candidato
            
            if mejor_candidato:
                diversos.append(mejor_candidato)
                candidatos_restantes.remove(mejor_candidato)
            else:
                break
        
        return diversos
    
    def _reparar_cronograma_basico(self, cronograma: Dict) -> Dict:
        return self._verificar_cocina_diaria(cronograma)
    
    def _verificar_cocina_diaria(self, cronograma: Dict) -> Dict:
        if not self.tareas_cocina_nombres:
            return cronograma
        
        dias_con_cocina = set()
        
        for asig in cronograma.values():
            if asig['tarea'] in self.tareas_cocina_nombres:
                dias_con_cocina.add(f"S{asig['semana']}_{asig['dia']}")
        
        for semana in self.semanas:
            for dia in self.dias_semana:
                dia_key = f"S{semana}_{dia}"
                
                if dia_key not in dias_con_cocina:
                    tarea_cocina_nombre = random.choice(list(self.tareas_cocina_nombres))
                    tarea_cocina = self.tareas_dict[tarea_cocina_nombre]
                    
                    roommate = self._seleccionar_roommate_optimo(dia, tarea_cocina)
                    hora = self._seleccionar_hora_optima(roommate.nombre, dia)
                    
                    key = f"cocina_reparacion_S{semana}_{dia}_{random.randint(1000,9999)}"
                    cronograma[key] = {
                        'tarea': tarea_cocina.nombre,
                        'roommate': roommate.nombre,
                        'dia': dia,
                        'semana': semana,
                        'hora': hora,
                        'duracion': tarea_cocina.tiempo_estimado
                    }
        
        return cronograma
    
    def _emparejamiento_selectivo_mejorado(self, fitness_poblacion: List[Tuple]) -> List[Tuple]:
        poblacion_ordenada = sorted(fitness_poblacion, key=lambda x: x[1], reverse=True)
        parejas = []
        
        top_20_percent = max(2, int(len(poblacion_ordenada) * 0.2))
        mejores = poblacion_ordenada[:top_20_percent]
        resto = poblacion_ordenada[top_20_percent:]
        
        for i in range(0, len(mejores), 2):
            if i + 1 < len(mejores):
                parejas.append((mejores[i][0], mejores[i+1][0]))
            else:
                parejas.append((mejores[i][0], mejores[1][0]))
        
        for i, mejor in enumerate(mejores[:3]):
            if i < len(resto):
                parejas.append((mejor[0], resto[i][0]))
        
        for i in range(0, len(resto)-1, 2):
            parejas.append((resto[i][0], resto[i+1][0]))
        
        if len(poblacion_ordenada) % 2 == 1:
            ultimo = poblacion_ordenada[-1][0]
            mejor = poblacion_ordenada[0][0]
            parejas.append((ultimo, mejor))
        
        return parejas
    
    def _calcular_desviacion_estandar(self, fitness_scores: List[float]) -> float:
        if not fitness_scores:
            return 0
        return np.std(fitness_scores)
    
    def _calcular_mejora(self, historia: List[Dict]) -> float:
        if len(historia) < 2:
            return 0
        anterior = historia[-2]['mejor']
        actual = historia[-1]['mejor']
        return ((actual - anterior) / anterior * 100) if anterior > 0 else 0
    
    def _detectar_convergencia_temprana(self, historia: List[Dict], ventana: int = 7, umbral: float = 0.2) -> bool:
        if len(historia) < ventana:
            return False
        
        ultimos_mejor = [h['mejor'] for h in historia[-ventana:]]
        ultimos_promedio = [h['promedio'] for h in historia[-ventana:]]
        
        mejora_mejor = abs(ultimos_mejor[-1] - ultimos_mejor[0])
        mejora_promedio = abs(ultimos_promedio[-1] - ultimos_promedio[0])
        
        mejora_mejor_pct = (mejora_mejor / ultimos_mejor[0] * 100) if ultimos_mejor[0] > 0 else 0
        mejora_promedio_pct = (mejora_promedio / ultimos_promedio[0] * 100) if ultimos_promedio[0] > 0 else 0
        
        return mejora_mejor_pct < umbral and mejora_promedio_pct < umbral