# --- Observer Pattern Implementation ---
"""
Implementação do padrão Observer para notificações e eventos no Travel Itinerary Planner.
Permite que objetos sejam notificados sobre mudanças em outros objetos sem acoplamento direto.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import threading

# === Tipos de Eventos ===

class EventType(Enum):
    """Enum com tipos de eventos que podem ser observados"""
    TRIP_CREATED = "trip_created"
    TRIP_UPDATED = "trip_updated"
    TRIP_BUDGET_CHANGED = "trip_budget_changed"
    COLLABORATOR_ADDED = "collaborator_added"
    COLLABORATOR_REMOVED = "collaborator_removed"
    FLIGHT_ADDED = "flight_added"
    HOTEL_ADDED = "hotel_added"
    ACTIVITY_ADDED = "activity_added"
    EXPENSE_ADDED = "expense_added"
    ITEM_STATUS_CHANGED = "item_status_changed"
    CONTRIBUTION_APPROVED = "contribution_approved"
    CONTRIBUTION_REJECTED = "contribution_rejected"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    USER_PREFERENCE_UPDATED = "user_preference_updated"

# === Observer Interface ===

class Observer(ABC):
    """Interface Observer - define o contrato para objetos que observam mudanças"""
    
    @abstractmethod
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """
        Método chamado quando um evento ocorre
        
        Args:
            event_type: Tipo do evento que ocorreu
            data: Dados relacionados ao evento
        """
        pass
    
    @abstractmethod
    def get_observer_name(self):
        """Retorna o nome do observer para identificação"""
        pass

# === Subject (Observable) Base Class ===

class Subject(ABC):
    """Classe base para objetos observáveis"""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._observers_lock = None  # Será inicializado se necessário (thread-safety)
    
    def attach(self, observer: Observer):
        """Adiciona um observer à lista de observadores"""
        if observer not in self._observers:
            self._observers.append(observer)
            print(f"Observer {observer.get_observer_name()} anexado com sucesso")
    
    def detach(self, observer: Observer):
        """Remove um observer da lista de observadores"""
        if observer in self._observers:
            self._observers.remove(observer)
            print(f"Observer {observer.get_observer_name()} removido com sucesso")
    
    def notify(self, event_type: EventType, data: Dict[str, Any]):
        """
        Notifica todos os observers registrados sobre um evento
        
        Args:
            event_type: Tipo do evento
            data: Dados do evento
        """
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                print(f"Erro ao notificar observer {observer.get_observer_name()}: {e}")
    
    def get_observers_count(self):
        """Retorna o número de observers registrados"""
        return len(self._observers)
    
    def clear_observers(self):
        """Remove todos os observers"""
        self._observers.clear()

# === Observers Concretos ===

class NotificationObserver(Observer):
    """Observer que armazena notificações para os usuários"""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Armazena a notificação"""
        notification = {
            'event_type': event_type.value,
            'data': data,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'read': False
        }
        self.notifications.append(notification)
        print(f"📬 Notificação criada: {event_type.value}")
    
    def get_notifications(self, user_id: Optional[int] = None, unread_only: bool = False):
        """Retorna notificações, opcionalmente filtradas por usuário e status de leitura"""
        filtered = self.notifications
        
        if user_id:
            filtered = [n for n in filtered if n['data'].get('user_id') == user_id]
        
        if unread_only:
            filtered = [n for n in filtered if not n['read']]
        
        return filtered
    
    def mark_as_read(self, notification_index: int):
        """Marca uma notificação como lida"""
        if 0 <= notification_index < len(self.notifications):
            self.notifications[notification_index]['read'] = True
    
    def mark_all_as_read(self, user_id: Optional[int] = None):
        """Marca todas as notificações como lidas"""
        for notification in self.notifications:
            if user_id is None or notification['data'].get('user_id') == user_id:
                notification['read'] = True
    
    def clear_notifications(self, user_id: Optional[int] = None):
        """Remove notificações"""
        if user_id:
            self.notifications = [n for n in self.notifications if n['data'].get('user_id') != user_id]
        else:
            self.notifications.clear()
    
    def get_observer_name(self):
        return "NotificationObserver"

class TripObserver(Observer):
    """Observer específico para eventos relacionados a viagens"""
    
    def __init__(self):
        self.trip_events: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Processa eventos relacionados a viagens"""
        if event_type.value.startswith('trip') or event_type == EventType.COLLABORATOR_ADDED:
            event_record = {
                'event_type': event_type.value,
                'trip_id': data.get('trip_id'),
                'user_id': data.get('user_id'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': data
            }
            self.trip_events.append(event_record)
            
            # Log específico baseado no tipo de evento
            if event_type == EventType.TRIP_CREATED:
                print(f"✈️ Nova viagem criada: {data.get('trip_name')} (ID: {data.get('trip_id')})")
            elif event_type == EventType.COLLABORATOR_ADDED:
                print(f"👥 Colaborador adicionado à viagem {data.get('trip_id')}")
            elif event_type == EventType.TRIP_BUDGET_CHANGED:
                print(f"💰 Orçamento da viagem {data.get('trip_id')} atualizado para ${data.get('budget', 0):.2f}")
    
    def get_trip_history(self, trip_id: int):
        """Retorna histórico de eventos de uma viagem específica"""
        return [event for event in self.trip_events if event['trip_id'] == trip_id]
    
    def get_observer_name(self):
        return "TripObserver"

class BudgetObserver(Observer):
    """Observer específico para eventos relacionados a orçamento"""
    
    def __init__(self):
        self.budget_changes: List[Dict[str, Any]] = []
        self.budget_threshold = 1000.0  # Threshold para alertas
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Monitora mudanças de orçamento"""
        if event_type == EventType.TRIP_BUDGET_CHANGED:
            budget = data.get('budget', 0)
            trip_id = data.get('trip_id')
            
            change_record = {
                'trip_id': trip_id,
                'old_budget': data.get('old_budget'),
                'new_budget': budget,
                'change_amount': budget - (data.get('old_budget', 0)),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'user_id': data.get('user_id')
            }
            self.budget_changes.append(change_record)
            
            # Alerta se o orçamento exceder o threshold
            if budget > self.budget_threshold:
                print(f"⚠️ ALERTA: Orçamento da viagem {trip_id} excede ${self.budget_threshold:.2f}: ${budget:.2f}")
            else:
                print(f"💰 Orçamento atualizado: ${budget:.2f}")
    
    def get_budget_history(self, trip_id: int):
        """Retorna histórico de mudanças de orçamento"""
        return [change for change in self.budget_changes if change['trip_id'] == trip_id]
    
    def set_threshold(self, threshold: float):
        """Define o threshold de alerta de orçamento"""
        self.budget_threshold = threshold
    
    def get_observer_name(self):
        return "BudgetObserver"

class CollaboratorObserver(Observer):
    """Observer para eventos relacionados a colaboradores"""
    
    def __init__(self):
        self.collaborator_events: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Processa eventos de colaboradores"""
        if event_type in [EventType.COLLABORATOR_ADDED, EventType.COLLABORATOR_REMOVED]:
            event_record = {
                'event_type': event_type.value,
                'trip_id': data.get('trip_id'),
                'collaborator_id': data.get('collaborator_id'),
                'added_by': data.get('added_by'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.collaborator_events.append(event_record)
            
            if event_type == EventType.COLLABORATOR_ADDED:
                print(f"👥 Novo colaborador {data.get('collaborator_id')} adicionado à viagem {data.get('trip_id')}")
            elif event_type == EventType.COLLABORATOR_REMOVED:
                print(f"👋 Colaborador {data.get('collaborator_id')} removido da viagem {data.get('trip_id')}")
    
    def get_collaborator_events(self, trip_id: Optional[int] = None):
        """Retorna eventos de colaboradores, opcionalmente filtrados por viagem"""
        if trip_id:
            return [event for event in self.collaborator_events if event['trip_id'] == trip_id]
        return self.collaborator_events
    
    def get_observer_name(self):
        return "CollaboratorObserver"

class ItineraryObserver(Observer):
    """Observer para eventos relacionados a itens do itinerário"""
    
    def __init__(self):
        self.itinerary_events: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Processa eventos de itens do itinerário"""
        if event_type in [EventType.FLIGHT_ADDED, EventType.HOTEL_ADDED, 
                         EventType.ACTIVITY_ADDED, EventType.EXPENSE_ADDED,
                         EventType.ITEM_STATUS_CHANGED]:
            event_record = {
                'event_type': event_type.value,
                'trip_id': data.get('trip_id'),
                'item_type': data.get('item_type'),
                'item_id': data.get('item_id'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'user_id': data.get('user_id')
            }
            self.itinerary_events.append(event_record)
            
            # Mensagens específicas por tipo
            item_messages = {
                EventType.FLIGHT_ADDED: "✈️ Novo voo adicionado",
                EventType.HOTEL_ADDED: "🏨 Novo hotel adicionado",
                EventType.ACTIVITY_ADDED: "🎯 Nova atividade adicionada",
                EventType.EXPENSE_ADDED: "💵 Nova despesa registrada",
                EventType.ITEM_STATUS_CHANGED: "✅ Status de item atualizado"
            }
            
            message = item_messages.get(event_type, "Item atualizado")
            print(f"{message} na viagem {data.get('trip_id')}")
    
    def get_itinerary_events(self, trip_id: Optional[int] = None, item_type: Optional[str] = None):
        """Retorna eventos do itinerário com filtros opcionais"""
        filtered = self.itinerary_events
        
        if trip_id:
            filtered = [e for e in filtered if e['trip_id'] == trip_id]
        
        if item_type:
            filtered = [e for e in filtered if e.get('item_type') == item_type]
        
        return filtered
    
    def get_observer_name(self):
        return "ItineraryObserver"

class ContributionObserver(Observer):
    """Observer para eventos relacionados a contribuições de usuários"""
    
    def __init__(self):
        self.contribution_events: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Processa eventos de contribuições"""
        if event_type in [EventType.CONTRIBUTION_APPROVED, EventType.CONTRIBUTION_REJECTED]:
            event_record = {
                'event_type': event_type.value,
                'contribution_id': data.get('contribution_id'),
                'user_id': data.get('user_id'),
                'trip_id': data.get('trip_id'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'details': data
            }
            self.contribution_events.append(event_record)
            
            if event_type == EventType.CONTRIBUTION_APPROVED:
                print(f"✅ Contribuição {data.get('contribution_id')} aprovada!")
            elif event_type == EventType.CONTRIBUTION_REJECTED:
                print(f"❌ Contribuição {data.get('contribution_id')} rejeitada")
    
    def get_contribution_events(self, user_id: Optional[int] = None):
        """Retorna eventos de contribuições, opcionalmente filtrados por usuário"""
        if user_id:
            return [e for e in self.contribution_events if e['user_id'] == user_id]
        return self.contribution_events
    
    def get_observer_name(self):
        return "ContributionObserver"

class RecommendationObserver(Observer):
    """Observer para eventos relacionados a recomendações"""
    
    def __init__(self):
        self.recommendation_events: List[Dict[str, Any]] = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        """Processa eventos de recomendações"""
        if event_type == EventType.RECOMMENDATION_GENERATED:
            event_record = {
                'event_type': event_type.value,
                'user_id': data.get('user_id'),
                'recommendation_type': data.get('recommendation_type'),
                'count': data.get('count', 0),
                'strategy_used': data.get('strategy_used'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.recommendation_events.append(event_record)
            
            print(f"🎯 {data.get('count', 0)} recomendações geradas para usuário {data.get('user_id')} "
                  f"usando estratégia {data.get('strategy_used', 'unknown')}")
    
    def get_recommendation_statistics(self, user_id: Optional[int] = None):
        """Retorna estatísticas de recomendações"""
        events = self.recommendation_events
        if user_id:
            events = [e for e in events if e['user_id'] == user_id]
        
        if not events:
            return {'total': 0, 'by_type': {}, 'by_strategy': {}}
        
        stats = {
            'total': len(events),
            'by_type': {},
            'by_strategy': {}
        }
        
        for event in events:
            rec_type = event.get('recommendation_type', 'unknown')
            strategy = event.get('strategy_used', 'unknown')
            
            stats['by_type'][rec_type] = stats['by_type'].get(rec_type, 0) + 1
            stats['by_strategy'][strategy] = stats['by_strategy'].get(strategy, 0) + 1
        
        return stats
    
    def get_observer_name(self):
        return "RecommendationObserver"

# === Event Manager (Singleton para gerenciar observers globalmente) ===

class EventManager(Subject):
    """
    Gerenciador global de eventos usando Singleton Pattern
    Coordena todos os observers da aplicação
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        super().__init__()
        
        # Observers padrão que serão anexados automaticamente
        self._default_observers = []
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        """Retorna a instância única do EventManager"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def setup_default_observers(self):
        """Configura observers padrão para o sistema"""
        if not self._default_observers:
            self._default_observers = [
                NotificationObserver(),
                TripObserver(),
                BudgetObserver(),
                CollaboratorObserver(),
                ItineraryObserver(),
                ContributionObserver(),
                RecommendationObserver()
            ]
            
            for observer in self._default_observers:
                self.attach(observer)
            
            print(f"✅ {len(self._default_observers)} observers padrão configurados")
    
    def emit_event(self, event_type: EventType, data: Dict[str, Any]):
        """
        Método helper para emitir eventos de forma mais conveniente
        
        Args:
            event_type: Tipo do evento
            data: Dados do evento
        """
        self.notify(event_type, data)
    
    def get_notification_observer(self) -> Optional[NotificationObserver]:
        """Retorna o NotificationObserver se estiver anexado"""
        for observer in self._observers:
            if isinstance(observer, NotificationObserver):
                return observer
        return None
    
    def get_trip_observer(self) -> Optional[TripObserver]:
        """Retorna o TripObserver se estiver anexado"""
        for observer in self._observers:
            if isinstance(observer, TripObserver):
                return observer
        return None
    
    def get_budget_observer(self) -> Optional[BudgetObserver]:
        """Retorna o BudgetObserver se estiver anexado"""
        for observer in self._observers:
            if isinstance(observer, BudgetObserver):
                return observer
        return None

