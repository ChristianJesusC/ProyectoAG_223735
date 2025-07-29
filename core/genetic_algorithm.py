import random
import time
from typing import List, Dict, Tuple, Callable, Optional
from models import Roommate, Tarea, EspacioHogar

class AlgoritmoGenetico:
    def __init__(self, roommates: List[Roommate], tareas: List[Tarea], 
                 tam_poblacion: int = 50, generaciones: int = 30, espacio: EspacioHogar = None):
        
        self.roommates = roommates
        self.tareas = tareas
        self.espacio = espacio or EspacioHogar()
        self.tam_poblacion = tam_poblacion
        self.generaciones = generaciones
        
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            self.tareas_ajustadas = self._ajustar_tareas_por_espacio()
        else:
            self.tareas_ajustadas = self.tareas
        
        factor_rotacion = getattr(self.espacio, 'get_factor_rotacion_complejidad', lambda: 1.0)()
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
        
        if hasattr(self.espacio, 'generar_tareas_espaciales'):
            tareas_espaciales = self.espacio.generar_tareas_espaciales()
            tareas_ajustadas.extend(tareas_espaciales)
        
        return tareas_ajustadas
    
    def _calcular_tiempo_ajustado(self, tarea: Tarea) -> int:
        """Calcula tiempo ajustado según espacio"""
        tiempo_base = tarea.tiempo_estimado
        
        if hasattr(self.espacio, 'get_factor_tiempo_limpieza') and tarea.categoria == "Limpieza":
            factor_espacio = self.espacio.get_factor_tiempo_limpieza()
            tiempo_base = int(tiempo_base * factor_espacio)
        
        if hasattr(self.espacio, 'get_factor_equipamiento'):
            factor_equipamiento = self.espacio.get_factor_equipamiento(tarea.categoria)
            tiempo_base = int(tiempo_base * factor_equipamiento)
        
        return ((tiempo_base + 29) // 30) * 30
    
    def ejecutar(self, callback_progreso: Optional[Callable] = None):
        """
        Ejecuta el algoritmo genético con barra de progreso
        
        Args:
            callback_progreso: Función que recibe (generacion, metricas) para actualizar UI
        """
        
        # Población inicial
        poblacion = [self.generar_individuo() for _ in range(self.tam_poblacion)]
        historia_fitness = []
        
        if callback_progreso:
            callback_progreso(0, {
                'estado': 'Inicializando población...',
                'sub_estado': f'Creando {self.tam_poblacion} cronogramas aleatorios',
                'generacion': 0,
                'total_generaciones': self.generaciones,
                'progreso': 0,
                'mejor_fitness': 0,
                'promedio_fitness': 0,
                'diversidad': 1.0,
                'tiempo_estimado': self.generaciones * 2
            })
            time.sleep(0.3)
        
        for generacion in range(self.generaciones):
            
            # ✅ PROGRESO: INICIO DE GENERACIÓN
            if callback_progreso:
                callback_progreso(generacion, {
                    'estado': f'Generación {generacion + 1}/{self.generaciones}',
                    'sub_estado': 'Evaluando fitness de población',
                    'generacion': generacion,
                    'total_generaciones': self.generaciones,
                    'progreso': (generacion / self.generaciones) * 100
                })
            
            fitness_poblacion = [(individuo, self.calcular_fitness(individuo)) for individuo in poblacion]
            fitness_poblacion.sort(key=lambda x: x[1], reverse=True)

            if callback_progreso:
                callback_progreso(generacion, {
                    'sub_estado': 'Calculando estadísticas de generación',
                })
            
            # Registrar estadísticas
            fitness_scores = [f[1] for f in fitness_poblacion]
            diversidad = self._calcular_diversidad_poblacion(fitness_poblacion)
            
            estadisticas = {
                'generacion': generacion,
                'mejor': max(fitness_scores),
                'promedio': sum(fitness_scores) / len(fitness_scores),
                'peor': min(fitness_scores),
                'diversidad': diversidad,
                'desviacion': self._calcular_desviacion_estandar(fitness_scores)
            }
            
            historia_fitness.append(estadisticas)
            
            if generacion % 5 == 0:
                top_5_fitness = sorted(fitness_scores, reverse=True)[:5]
                print(f"Gen {generacion}: Top 5 = {[f'{f:.1f}' for f in top_5_fitness]}, Promedio = {estadisticas['promedio']:.1f}")
            
            if callback_progreso:
                progreso_porcentual = ((generacion + 1) / self.generaciones) * 100
                tiempo_restante = (self.generaciones - generacion - 1) * 1.2
                mejora = self._calcular_mejora(historia_fitness) if len(historia_fitness) > 1 else 0
                
                callback_progreso(generacion, {
                    'estado': f'Generación {generacion + 1}/{self.generaciones}',
                    'sub_estado': 'Aplicando selección, cruza y mutación mejorada',
                    'progreso': progreso_porcentual,
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
                        'sub_estado': 'Solución óptima encontrada antes de tiempo',
                        'progreso': 100,
                        'convergencia_temprana': True,
                        'generacion_final': generacion + 1
                    })
                break
            
            if callback_progreso:
                callback_progreso(generacion, {
                    'sub_estado': 'Generando nueva población (selección elitista mejorada)',
                })
            
            poblacion = self._generar_nueva_poblacion_mejorada(fitness_poblacion, generacion)
        
        if callback_progreso:
            callback_progreso(self.generaciones, {
                'estado': '✅ Optimización completada',
                'sub_estado': 'Seleccionando y validating mejor cronograma',
                'progreso': 100,
                'finalizado': True,
                'generaciones_totales': len(historia_fitness)
            })
            time.sleep(0.3)
        
        # Retornar mejor solución final
        fitness_final = [(individuo, self.calcular_fitness(individuo)) for individuo in poblacion]
        mejor_individuo = max(fitness_final, key=lambda x: x[1])[0]
        
        return mejor_individuo, historia_fitness
    
    def _calcular_desviacion_estandar(self, fitness_scores):
        """Calcula desviación estándar de fitness"""
        if not fitness_scores:
            return 0
        promedio = sum(fitness_scores) / len(fitness_scores)
        varianza = sum((f - promedio) ** 2 for f in fitness_scores) / len(fitness_scores)
        return varianza ** 0.5
    
    def _calcular_mejora(self, historia):
        """Calcula mejora porcentual entre últimas dos generaciones"""
        if len(historia) < 2:
            return 0
        anterior = historia[-2]['mejor']
        actual = historia[-1]['mejor']
        return ((actual - anterior) / anterior * 100) if anterior > 0 else 0
    
    def _detectar_convergencia_temprana(self, historia, ventana=7, umbral=0.2):
        """Detecta si el algoritmo ha convergido antes de tiempo"""
        if len(historia) < ventana:
            return False
        
        # Verificar tanto mejor como promedio
        ultimos_mejor = [h['mejor'] for h in historia[-ventana:]]
        ultimos_promedio = [h['promedio'] for h in historia[-ventana:]]
        
        mejora_mejor = abs(ultimos_mejor[-1] - ultimos_mejor[0])
        mejora_promedio = abs(ultimos_promedio[-1] - ultimos_promedio[0])
        
        mejora_mejor_pct = (mejora_mejor / ultimos_mejor[0] * 100) if ultimos_mejor[0] > 0 else 0
        mejora_promedio_pct = (mejora_promedio / ultimos_promedio[0] * 100) if ultimos_promedio[0] > 0 else 0
        
        # Convergencia si ambos mejoran menos del umbral
        return mejora_mejor_pct < umbral and mejora_promedio_pct < umbral
 
    def _emparejamiento_selectivo_mejorado(self, fitness_poblacion) -> List[Tuple]:
        """
        ESTRATEGIA: Favorece más a los buenos individuos
        Los mejores 20% tienen más oportunidades de reproducirse
        """
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
    
    def _crossover_multipunto_aleatorio(self, padre1, padre2):
        """
        ESTRATEGIA: Cantidad aleatoria de puntos de cruza (2-5)
        """
        
        fitness_padre1 = self.calcular_fitness(padre1)
        fitness_padre2 = self.calcular_fitness(padre2)
        
        keys_padre1 = sorted(list(padre1.keys()))
        keys_padre2 = sorted(list(padre2.keys()))
        
        keys_comunes = list(set(keys_padre1) & set(keys_padre2))
        if len(keys_comunes) < 3:
            return self._crossover_uniforme_mejorado(padre1, padre2, fitness_padre1, fitness_padre2)
        
        keys_comunes.sort()
        
        if fitness_padre1 > 100 and fitness_padre2 > 100:
            max_puntos = min(3, len(keys_comunes) - 1)
        else:
            max_puntos = min(5, len(keys_comunes) - 1)
        
        max_puntos = max(2, max_puntos)
        num_puntos = random.randint(2, max_puntos)
        
        posiciones_disponibles = list(range(1, len(keys_comunes)))
        if len(posiciones_disponibles) < num_puntos:
            return self._crossover_uniforme_mejorado(padre1, padre2, fitness_padre1, fitness_padre2)
        
        puntos_cruza = sorted(random.sample(posiciones_disponibles, num_puntos))
        
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
        
        self._agregar_claves_unicas_mejorado(hijo, padre1, padre2, keys_comunes, fitness_padre1, fitness_padre2)
        
        return self._reparar_cronograma_basico(hijo)
    
    def _crossover_uniforme_mejorado(self, padre1, padre2, fitness1, fitness2):
        """Crossover uniforme que favorece al mejor padre"""
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
    
    def _agregar_claves_unicas_mejorado(self, hijo, padre1, padre2, keys_comunes, fitness1, fitness2):
        """Agrega claves únicas favoreciendo al mejor padre"""
        keys_comunes_set = set(keys_comunes)
        
        if fitness1 > fitness2:
            prob_padre1, prob_padre2 = 0.75, 0.25
        elif fitness2 > fitness1:
            prob_padre1, prob_padre2 = 0.25, 0.75
        else:
            prob_padre1, prob_padre2 = 0.6, 0.4
        
        # Claves únicas del padre1
        for key in padre1:
            if key not in keys_comunes_set and random.random() < prob_padre1:
                hijo[key] = padre1[key].copy()
        
        # Claves únicas del padre2
        for key in padre2:
            if key not in keys_comunes_set and key not in hijo and random.random() < prob_padre2:
                hijo[key] = padre2[key].copy()

    def _mutacion_adaptativa_por_calidad(self, individuo, generacion=None):
        """
        ESTRATEGIA: Mutación que protege individuos de alta calidad
        Individuos mejores mutan menos, individuos peores mutan más
        """
        
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
        
        genes_a_mutar = []
        for key in keys:
            if random.random() <= pmg_actual:
                genes_a_mutar.append(key)
        
        if len(genes_a_mutar) < 2:
            return individuo
        
        if tipo_individuo in ["excelente", "bueno"]:
            self._intercambio_suave(individuo, genes_a_mutar)
        else:
            self._intercambiar_genes_aleatorio(individuo, genes_a_mutar)
        
        return self._reparar_cronograma_basico(individuo)
    
    def _intercambio_suave(self, individuo, genes_disponibles):
        """Intercambio más conservador para individuos de alta calidad"""
        if len(genes_disponibles) < 2:
            return
        
        if random.random() < 0.6:
            self._intercambiar_horarios_mismo_dia(individuo, genes_disponibles)
        else:
            self._intercambiar_dias_misma_semana(individuo, genes_disponibles)
    
    def _intercambiar_dias_misma_semana(self, individuo, genes):
        """Intercambia días dentro de la misma semana (más conservador)"""
        if len(genes) < 2:
            return
        
        genes_por_semana = {}
        for gene in genes:
            asig = individuo[gene]
            semana = asig['semana']
            if semana not in genes_por_semana:
                genes_por_semana[semana] = []
            genes_por_semana[semana].append(gene)
        
        for semana, genes_semana in genes_por_semana.items():
            if len(genes_semana) >= 2:
                gene1, gene2 = random.sample(genes_semana, 2)
                dia1 = individuo[gene1]['dia']
                dia2 = individuo[gene2]['dia']
                individuo[gene1]['dia'] = dia2
                individuo[gene2]['dia'] = dia1
    
    def _intercambiar_genes_aleatorio(self, individuo, genes_disponibles):
        """Intercambio original (más agresivo) para individuos regulares/malos"""
        
        if random.random() < 0.6:
            self._intercambiar_roommates_compatibles(individuo, genes_disponibles)
        
        elif random.random() < 0.85:
            self._intercambiar_horarios_mismo_dia(individuo, genes_disponibles)
        
        else:
            self._intercambiar_dias_semanas(individuo, genes_disponibles)
    
    def _intercambiar_roommates_compatibles(self, individuo, genes):
        """Intercambia roommates entre tareas de categorías compatibles"""
        if len(genes) < 2:
            return
        
        genes_por_categoria = {}
        for gene in genes:
            asig = individuo[gene]
            tarea_obj = next((t for t in self.tareas_ajustadas if t.nombre == asig['tarea']), None)
            if tarea_obj:
                categoria = tarea_obj.categoria
                if categoria not in genes_por_categoria:
                    genes_por_categoria[categoria] = []
                genes_por_categoria[categoria].append(gene)
        
        for categoria, genes_categoria in genes_por_categoria.items():
            if len(genes_categoria) >= 2:
                gene1, gene2 = random.sample(genes_categoria, 2)
                roommate1 = individuo[gene1]['roommate']
                roommate2 = individuo[gene2]['roommate']
                individuo[gene1]['roommate'] = roommate2
                individuo[gene2]['roommate'] = roommate1
    
    def _intercambiar_horarios_mismo_dia(self, individuo, genes):
        """Intercambia horarios entre asignaciones del mismo día"""
        if len(genes) < 2:
            return
        
        genes_por_dia = {}
        for gene in genes:
            asig = individuo[gene]
            dia_key = f"S{asig['semana']}_{asig['dia']}"
            if dia_key not in genes_por_dia:
                genes_por_dia[dia_key] = []
            genes_por_dia[dia_key].append(gene)
        
        for dia, genes_dia in genes_por_dia.items():
            if len(genes_dia) >= 2:
                gene1, gene2 = random.sample(genes_dia, 2)
                hora1 = individuo[gene1]['hora']
                hora2 = individuo[gene2]['hora']
                individuo[gene1]['hora'] = hora2
                individuo[gene2]['hora'] = hora1
    
    def _intercambiar_dias_semanas(self, individuo, genes):
        """Intercambia días o semanas entre asignaciones"""
        if len(genes) < 2:
            return
        
        gene1, gene2 = random.sample(genes, 2)
        
        if random.random() < 0.5:
            dia1 = individuo[gene1]['dia']
            dia2 = individuo[gene2]['dia']
            individuo[gene1]['dia'] = dia2
            individuo[gene2]['dia'] = dia1
        else:
            semana1 = individuo[gene1]['semana']
            semana2 = individuo[gene2]['semana']
            individuo[gene1]['semana'] = semana2
            individuo[gene2]['semana'] = semana1
            
    def _poda_elitista_mejorada(self, poblacion_extendida):
        """
        ESTRATEGIA: Más elitismo + selección probabilística
        """
        
        if len(poblacion_extendida) <= self.tam_poblacion:
            return poblacion_extendida
        
        poblacion_con_fitness = [(ind, self.calcular_fitness(ind)) for ind in poblacion_extendida]
        poblacion_con_fitness.sort(key=lambda x: x[1], reverse=True)
        
        num_elites = max(3, int(self.tam_poblacion * 0.15))
        elites = [ind for ind, _ in poblacion_con_fitness[:num_elites]]
        poblacion_podada = elites.copy()
        
        candidatos_top50 = poblacion_con_fitness[num_elites:int(len(poblacion_con_fitness) * 0.5)]
        if candidatos_top50:
            num_diversos = max(2, int(self.tam_poblacion * 0.08))
            diversos = self._seleccionar_diversos([ind for ind, _ in candidatos_top50], num_diversos)
            poblacion_podada.extend(diversos)
            
            candidatos_restantes = []
            for ind, fit in candidatos_top50:
                es_diverso = False
                for div in diversos:
                    if self._cronogramas_iguales(ind, div):
                        es_diverso = True
                        break
                if not es_diverso:
                    candidatos_restantes.append((ind, fit))
        else:
            candidatos_restantes = []
       
        espacios_restantes = self.tam_poblacion - len(poblacion_podada)
        
        if espacios_restantes > 0 and candidatos_restantes: 
            candidatos_bottom = poblacion_con_fitness[int(len(poblacion_con_fitness) * 0.5):]
            todos_candidatos = candidatos_restantes + candidatos_bottom
            
            if todos_candidatos:
                fitness_values = [fit for _, fit in todos_candidatos]
                min_fitness = min(fitness_values)
                max_fitness = max(fitness_values)
             
                pesos_normalizados = []
                for _, fit in todos_candidatos:
                    if max_fitness > min_fitness:
                        peso_normalizado = 0.1 + 0.9 * ((fit - min_fitness) / (max_fitness - min_fitness))
                    else:
                        peso_normalizado = 1.0
                    pesos_normalizados.append(peso_normalizado)
                
                individuos_seleccionados = random.choices(
                    [ind for ind, _ in todos_candidatos],
                    weights=pesos_normalizados,
                    k=min(espacios_restantes, len(todos_candidatos))
                )
                
                poblacion_podada.extend(individuos_seleccionados)
        
        return poblacion_podada[:self.tam_poblacion]
    
    def _cronogramas_iguales(self, cronograma1, cronograma2):
        if len(cronograma1) != len(cronograma2):
            return False
        
        for key in cronograma1:
            if key not in cronograma2:
                return False
            if cronograma1[key] != cronograma2[key]:
                return False
        
        return True
    
    def _seleccionar_diversos(self, candidatos, cantidad):
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
            mejor_candidato = None
            mejor_distancia_minima = -1
            
            for candidato in candidatos_restantes:
                distancia_minima = float('inf')
                for seleccionado in diversos:
                    distancia = self._distancia_hamming_cronograma(candidato, seleccionado)
                    distancia_minima = min(distancia_minima, distancia)
                
                if distancia_minima > mejor_distancia_minima:
                    mejor_distancia_minima = distancia_minima
                    mejor_candidato = candidato
            
            if mejor_candidato:
                diversos.append(mejor_candidato)
                candidatos_restantes.remove(mejor_candidato)
            else:
                break
        
        return diversos
    
    def _distancia_hamming_cronograma(self, cronograma1, cronograma2):
        diferencias = 0
        total_comparaciones = 0
        
        keys_comunes = set(cronograma1.keys()) & set(cronograma2.keys())
        
        for key in keys_comunes:
            asig1 = cronograma1[key]
            asig2 = cronograma2[key]
            
            # Comparar roommate
            if asig1['roommate'] != asig2['roommate']:
                diferencias += 1
            total_comparaciones += 1
            
            # Comparar hora (tolerancia 30 min)
            if abs(asig1['hora'] - asig2['hora']) > 0.5:
                diferencias += 1
            total_comparaciones += 1
            
            # Comparar día
            if asig1['dia'] != asig2['dia']:
                diferencias += 1
            total_comparaciones += 1
        
        return diferencias / total_comparaciones if total_comparaciones > 0 else 0
    
    def _generar_nueva_poblacion_mejorada(self, fitness_poblacion, generacion):
        """✅ Genera nueva población con todas las estrategias mejoradas"""
        
        parejas = self._emparejamiento_selectivo_mejorado(fitness_poblacion)
        
        descendencia = []
        for padre1, padre2 in parejas:
            hijo1 = self._crossover_multipunto_aleatorio(padre1, padre2)
            hijo2 = self._crossover_multipunto_aleatorio(padre2, padre1)
            
            hijo1 = self._mutacion_adaptativa_por_calidad(hijo1, generacion)
            hijo2 = self._mutacion_adaptativa_por_calidad(hijo2, generacion)
            
            descendencia.extend([hijo1, hijo2])
        
        padres = [ind for ind, _ in fitness_poblacion]
        poblacion_extendida = padres + descendencia
        
        return self._poda_elitista_mejorada(poblacion_extendida)

    def _calcular_diversidad_poblacion(self, fitness_poblacion):
        """Calcula diversidad promedio de la población"""
        if len(fitness_poblacion) < 2:
            return 1.0
        
        distancias = []
        individuos = [ind for ind, _ in fitness_poblacion]
        
        if len(individuos) > 20:
            muestra = random.sample(individuos, 20)
        else:
            muestra = individuos
        
        for i in range(len(muestra)):
            for j in range(i + 1, len(muestra)):
                dist = self._distancia_hamming_cronograma(muestra[i], muestra[j])
                distancias.append(dist)
        
        return sum(distancias) / len(distancias) if distancias else 0.0

    def _reparar_cronograma_basico(self, cronograma):
        """Reparación básica para mantener viabilidad"""
        cronograma = self._verificar_cocina_diaria(cronograma)
        return cronograma
    
    def _verificar_cocina_diaria(self, cronograma):
        """Asegura al menos una tarea de cocina por día"""
        tareas_cocina = [t for t in self.tareas_ajustadas if t.categoria == 'Cocina']
        if not tareas_cocina:
            return cronograma
        
        for semana in self.semanas:
            for dia in self.dias_semana:
                tiene_cocina = any(
                    asig['semana'] == semana and 
                    asig['dia'] == dia and
                    any(t.nombre == asig['tarea'] and t.categoria == 'Cocina' 
                        for t in self.tareas_ajustadas)
                    for asig in cronograma.values()
                )
                
                if not tiene_cocina:
                    tarea_cocina = random.choice(tareas_cocina)
                    roommate = self._seleccionar_roommate_optimo(dia, tarea_cocina)
                    hora = self._seleccionar_hora_optima(roommate, dia, tarea_cocina)
                    
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

    def generar_individuo(self):
        """Genera un individuo aleatorio (cronograma)"""
        asignaciones = {}
        self._garantizar_cocina_diaria(asignaciones)
        
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
            return 12.0
        
        rangos = roommate.horarios_disponibles[dia]
        if not rangos:
            return 12.0
        
        horas_disponibles = []
        for rango in rangos:
            hora_actual = rango.inicio
            while hora_actual < rango.fin:
                if hora_actual % 0.5 == 0:
                    horas_disponibles.append(hora_actual)
                hora_actual += 0.5
        
        return random.choice(horas_disponibles) if horas_disponibles else 12.0
    
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
                else:
                    score_total += 0.5
        
        return max(0, score_total) / len(individuo) if individuo else 0
    
    def _fitness_rotacion_espacial(self, individuo: Dict) -> float:
        """Calcula fitness de rotación considerando espacio"""
        factor_complejidad = 1.0
        if hasattr(self.espacio, 'get_factor_rotacion_complejidad'):
            factor_complejidad = self.espacio.get_factor_rotacion_complejidad()
        
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