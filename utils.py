import pandas as pd
import numpy as np
import random
from typing import Dict, List, Tuple
from models import Roommate, Tarea, RangoTiempo, TareasPredeterminadas

class DataUtilsMejorado:
    
    @staticmethod
    def generar_datos_demo_aleatorios():
        """Genera roommates demo con datos completamente aleatorios - SOLO DATOS"""
        num_roommates = random.randint(3, 5)
        
        roommates_demo = []
        nombres_usados = set()
        
        for _ in range(num_roommates):
            intentos = 0
            while intentos < 20:
                roommate = DataUtilsMejorado.generar_roommate_aleatorio()
                if roommate.nombre not in nombres_usados:
                    nombres_usados.add(roommate.nombre)
                    roommates_demo.append(roommate)
                    break
                intentos += 1
        
        if len(roommates_demo) < 2:
            roommates_demo = [
                DataUtilsMejorado.generar_roommate_aleatorio(),
                DataUtilsMejorado.generar_roommate_aleatorio(),
                DataUtilsMejorado.generar_roommate_aleatorio()
            ]
        
        # Seleccionar tareas aleatorias
        todas_las_tareas = TareasPredeterminadas.get_tareas_basicas()
        num_tareas = random.randint(8, min(15, len(todas_las_tareas)))
        tareas_seleccionadas = random.sample(todas_las_tareas, num_tareas)
        
        return roommates_demo, tareas_seleccionadas
    
    @staticmethod
    def generar_roommate_aleatorio():
        """Genera un roommate con datos completamente aleatorios"""
        nombres_masculinos = [
            "Alejandro", "Carlos", "Diego", "Eduardo", "Fernando", "Gabriel", "Hugo", "Iván", 
            "Javier", "Kevin", "Luis", "Mario", "Nicolás", "Oscar", "Pablo", "Ricardo", 
            "Santiago", "Tomás", "Vicente", "Ximeno"
        ]
        
        nombres_femeninos = [
            "Ana", "Beatriz", "Carmen", "Diana", "Elena", "Fernanda", "Gabriela", "Helena",
            "Isabel", "Julia", "Karla", "Laura", "María", "Natalia", "Olivia", "Patricia",
            "Regina", "Sofía", "Teresa", "Valeria"
        ]
        
        genero = random.choice(["M", "F"])
        if genero == "M":
            nombre = random.choice(nombres_masculinos)
        else:
            nombre = random.choice(nombres_femeninos)
        
        horarios = DataUtilsMejorado.generar_horarios_aleatorios()
        habilidades = DataUtilsMejorado.generar_habilidades_aleatorias()
        preferencias = DataUtilsMejorado.generar_preferencias_aleatorias(habilidades)
        tiempo_objetivo = random.randint(10, 25)
        
        return Roommate(nombre, horarios, habilidades, preferencias, tiempo_objetivo)
    
    @staticmethod
    def generar_horarios_aleatorios():
        """Genera horarios realistas para cada día de la semana"""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        horarios = {}
        
        patrones_laborales = ["mañana_temprano", "mañana_tarde", "tarde_noche", "noche", "flexible", "estudiante"]
        patron = random.choice(patrones_laborales)
        
        for dia in dias:
            es_fin_semana = dia in ['Sábado', 'Domingo']
            rangos_dia = []
            
            if patron == "mañana_temprano":
                if es_fin_semana:
                    if random.random() > 0.3:
                        inicio = random.uniform(7, 10)
                        fin = random.uniform(inicio + 3, 20)
                        rangos_dia.append(RangoTiempo(inicio, fin))
                else:
                    if random.random() > 0.1:
                        rangos_dia.append(RangoTiempo(6, random.uniform(11, 13)))
                        if random.random() > 0.5:
                            rangos_dia.append(RangoTiempo(random.uniform(18, 19), random.uniform(21, 23)))
            
            elif patron == "mañana_tarde":
                if es_fin_semana:
                    if random.random() > 0.2:
                        inicio = random.uniform(8, 11)
                        fin = random.uniform(inicio + 4, 22)
                        rangos_dia.append(RangoTiempo(inicio, fin))
                else:
                    if random.random() > 0.1:
                        rangos_dia.append(RangoTiempo(random.uniform(7, 9), random.uniform(15, 17)))
                        if random.random() > 0.6:
                            rangos_dia.append(RangoTiempo(random.uniform(19, 20), random.uniform(22, 23.5)))
            
            elif patron == "tarde_noche":
                if es_fin_semana:
                    if random.random() > 0.2:
                        rangos_dia.append(RangoTiempo(random.uniform(9, 12), random.uniform(18, 23)))
                else:
                    if random.random() > 0.1:
                        if random.random() > 0.4:
                            rangos_dia.append(RangoTiempo(random.uniform(6, 8), random.uniform(9, 11)))
                        rangos_dia.append(RangoTiempo(random.uniform(14, 16), random.uniform(21, 23)))
            
            elif patron == "noche":
                if es_fin_semana:
                    if random.random() > 0.1:
                        rangos_dia.append(RangoTiempo(random.uniform(10, 14), random.uniform(20, 23.5)))
                else:
                    if random.random() > 0.2:
                        rangos_dia.append(RangoTiempo(random.uniform(18, 19), random.uniform(22, 23.5)))
            
            elif patron == "estudiante":
                if es_fin_semana:
                    if random.random() > 0.1:
                        rangos_dia.append(RangoTiempo(random.uniform(9, 12), random.uniform(16, 23)))
                else:
                    if random.random() > 0.2:
                        if random.random() > 0.3:
                            rangos_dia.append(RangoTiempo(random.uniform(6, 8), random.uniform(9, 12)))
                        if random.random() > 0.2:
                            rangos_dia.append(RangoTiempo(random.uniform(18, 19), random.uniform(21, 23)))
            
            elif patron == "flexible":
                num_rangos = random.choice([0, 1, 1, 2, 2, 3])
                for _ in range(num_rangos):
                    inicio = random.uniform(6, 20)
                    duracion = random.uniform(2, 8)
                    fin = min(24, inicio + duracion)
                    if fin > inicio + 1:
                        rangos_dia.append(RangoTiempo(inicio, fin))
            
            # Redondear horarios a medias horas
            rangos_redondeados = []
            for rango in rangos_dia:
                inicio_redondeado = round(rango.inicio * 2) / 2
                fin_redondeado = round(rango.fin * 2) / 2
                if fin_redondeado > inicio_redondeado + 0.5:
                    rangos_redondeados.append(RangoTiempo(inicio_redondeado, fin_redondeado))
            
            if rangos_redondeados:
                horarios[dia] = rangos_redondeados
        
        return horarios
    
    @staticmethod
    def generar_habilidades_aleatorias():
        """Genera habilidades con cierta especialización realista"""
        categorias = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
        habilidades = {}
        
        especialidades = random.sample(categorias, random.randint(1, 2))
        debilidades = random.sample([cat for cat in categorias if cat not in especialidades], 
                                   random.randint(1, min(2, len(categorias) - len(especialidades))))
        
        for categoria in categorias:
            if categoria in especialidades:
                habilidades[categoria] = random.randint(7, 10)
            elif categoria in debilidades:
                habilidades[categoria] = random.randint(1, 4)
            else:
                habilidades[categoria] = random.randint(4, 7)
        
        return habilidades
    
    @staticmethod
    def generar_preferencias_aleatorias(habilidades):
        """Genera preferencias coherentes con las habilidades"""
        categorias = ['Limpieza', 'Cocina', 'Lavandería', 'Compras', 'Mantenimiento', 'Organización']
        preferencias = {}
        
        for categoria in categorias:
            nivel_habilidad = habilidades[categoria]
            
            if nivel_habilidad >= 8:
                preferencias[categoria] = random.choices(['prefiere', 'neutro'], weights=[0.8, 0.2])[0]
            elif nivel_habilidad <= 3:
                preferencias[categoria] = random.choices(['evita', 'neutro'], weights=[0.7, 0.3])[0]
            else:
                preferencias[categoria] = random.choices(['prefiere', 'neutro', 'evita'], weights=[0.3, 0.5, 0.2])[0]
        
        return preferencias
    
    @staticmethod
    def cronograma_a_dataframe(cronograma: Dict) -> pd.DataFrame:
        """Convierte cronograma a DataFrame"""
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
    def analizar_roommates_generados(roommates_demo):
        """Analiza los roommates generados y devuelve estadísticas"""
        analisis = []
        
        for rm in roommates_demo:
            especialidades = [cat for cat, nivel in rm.habilidades.items() if nivel >= 8]
            debilidades = [cat for cat, nivel in rm.habilidades.items() if nivel <= 3]
            horas_totales = rm.total_horas_disponibles()
            
            analisis.append({
                'nombre': rm.nombre,
                'especialidades': especialidades,
                'debilidades': debilidades,
                'horas_totales': horas_totales,
                'tiempo_objetivo': rm.tiempo_total_disponible
            })
        
        return analisis