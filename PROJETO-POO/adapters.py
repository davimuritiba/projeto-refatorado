# --- Adapter Pattern Implementation ---
"""
Implementação do padrão Adapter para adaptar diferentes formatos de dados de APIs externas
para o formato interno do Travel Itinerary Planner.
Permite integração com diferentes serviços externos sem modificar o código existente.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

# === Interface Target (Formato Interno) ===

class ItineraryItemAdapter(ABC):
    """Interface Target - define o formato padrão interno do sistema"""
    
    @abstractmethod
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapta dados de formato externo para formato interno
        
        Args:
            external_data: Dados no formato da API externa
            
        Returns:
            Dados no formato interno do sistema
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Retorna o nome da fonte de dados externa"""
        pass

# === Adaptadores Concretos ===

class ExternalFlightAPIAdapter(ItineraryItemAdapter):
    """
    Adaptador para API externa de voos
    Adapta formato: {flight_number, airline, departure_time, arrival_time, ...}
    Para formato: {company, code, departure, arrival, ...}
    """
    
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta dados de voo de API externa para formato interno"""
        try:
            # Exemplo de formato externo: {"flight_number": "AA123", "airline": "American Airlines", ...}
            return {
                'company': external_data.get('airline', external_data.get('company', 'Unknown')),
                'code': external_data.get('flight_number', external_data.get('code', 'N/A')),
                'departure': self._format_datetime(external_data.get('departure_time', external_data.get('departure'))),
                'arrival': self._format_datetime(external_data.get('arrival_time', external_data.get('arrival'))),
                'origin': external_data.get('origin', external_data.get('from', '')),
                'destination': external_data.get('destination', external_data.get('to', '')),
                'price': external_data.get('price', external_data.get('cost', 0.0)),
                'external_id': external_data.get('id', external_data.get('flight_id', None))
            }
        except Exception as e:
            raise ValueError(f"Erro ao adaptar dados de voo: {str(e)}")
    
    def _format_datetime(self, dt_str: Optional[str]) -> str:
        """Formata datetime para formato interno"""
        if not dt_str:
            return ""
        
        # Tenta diferentes formatos de data
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        return dt_str
    
    def get_source_name(self) -> str:
        return "External Flight API"

class ExternalHotelAPIAdapter(ItineraryItemAdapter):
    """
    Adaptador para API externa de hotéis
    Adapta formato: {hotel_name, check_in_date, check_out_date, ...}
    Para formato: {name, checkin, checkout, ...}
    """
    
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta dados de hotel de API externa para formato interno"""
        try:
            return {
                'name': external_data.get('hotel_name', external_data.get('name', 'Unknown Hotel')),
                'checkin': self._format_date(external_data.get('check_in_date', external_data.get('checkin'))),
                'checkout': self._format_date(external_data.get('check_out_date', external_data.get('checkout'))),
                'address': external_data.get('address', external_data.get('location', '')),
                'rating': external_data.get('rating', external_data.get('stars', 0)),
                'price_per_night': external_data.get('price_per_night', external_data.get('price', 0.0)),
                'external_id': external_data.get('id', external_data.get('hotel_id', None))
            }
        except Exception as e:
            raise ValueError(f"Erro ao adaptar dados de hotel: {str(e)}")
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Formata data para formato interno"""
        if not date_str:
            return ""
        
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str
    
    def get_source_name(self) -> str:
        return "External Hotel API"

class ExternalActivityAPIAdapter(ItineraryItemAdapter):
    """
    Adaptador para API externa de atividades
    Adapta formato: {activity_name, scheduled_date, description_text, ...}
    Para formato: {description, date, ...}
    """
    
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapta dados de atividade de API externa para formato interno"""
        try:
            return {
                'description': external_data.get('activity_name', external_data.get('description', 'Activity')),
                'date': self._format_date(external_data.get('scheduled_date', external_data.get('date'))),
                'time': external_data.get('time', external_data.get('start_time', '')),
                'location': external_data.get('location', external_data.get('venue', '')),
                'duration': external_data.get('duration', external_data.get('duration_hours', 0)),
                'price': external_data.get('price', external_data.get('cost', 0.0)),
                'category': external_data.get('category', external_data.get('type', 'general')),
                'external_id': external_data.get('id', external_data.get('activity_id', None))
            }
        except Exception as e:
            raise ValueError(f"Erro ao adaptar dados de atividade: {str(e)}")
    
    def _format_date(self, date_str: Optional[str]) -> str:
        """Formata data para formato interno"""
        if not date_str:
            return ""
        
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str
    
    def get_source_name(self) -> str:
        return "External Activity API"

# === Adapter Manager ===

class AdapterManager:
    """Gerenciador de adaptadores - facilita o uso dos adaptadores"""
    
    def __init__(self):
        self._adapters: Dict[str, ItineraryItemAdapter] = {}
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Registra os adaptadores padrão"""
        self.register_adapter('flight', ExternalFlightAPIAdapter())
        self.register_adapter('hotel', ExternalHotelAPIAdapter())
        self.register_adapter('activity', ExternalActivityAPIAdapter())
    
    def register_adapter(self, item_type: str, adapter: ItineraryItemAdapter):
        """Registra um novo adaptador"""
        self._adapters[item_type] = adapter
    
    def adapt_data(self, item_type: str, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapta dados externos para formato interno
        
        Args:
            item_type: Tipo do item (flight, hotel, activity)
            external_data: Dados no formato externo
            
        Returns:
            Dados adaptados no formato interno
        """
        if item_type not in self._adapters:
            raise ValueError(f"Adaptador não encontrado para tipo: {item_type}")
        
        adapter = self._adapters[item_type]
        return adapter.adapt(external_data)
    
    def get_available_adapters(self) -> List[str]:
        """Retorna lista de adaptadores disponíveis"""
        return list(self._adapters.keys())
    
    def get_adapter_source(self, item_type: str) -> str:
        """Retorna o nome da fonte de dados do adaptador"""
        if item_type not in self._adapters:
            raise ValueError(f"Adaptador não encontrado para tipo: {item_type}")
        
        return self._adapters[item_type].get_source_name()

