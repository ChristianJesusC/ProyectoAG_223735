import streamlit as st
from datetime import date, timedelta
from typing import List, Dict

class ManagerEmergencias:
    
    def __init__(self, cronograma: Dict, roommates: List):
        self.cronograma = cronograma
        self.roommates = roommates
    
    def mostrar_gestion_emergencias(self):
        """Interfaz básica de emergencias"""
        st.subheader("🚨 Gestión de Emergencias")
        st.info("🚧 **Funcionalidad en desarrollo**")
        
        if st.button("➕ Reportar Emergencia"):
            st.success("Función próximamente disponible")
        
        if st.button("📋 Ver Emergencias"):
            st.info("No hay emergencias registradas")