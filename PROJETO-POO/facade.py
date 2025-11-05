# --- Facade Pattern Implementation ---
"""
Implementação do padrão Facade para simplificar a interface complexa do sistema
Travel Itinerary Planner. Fornece uma interface unificada e simplificada para
operações comuns do sistema.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class TravelFacade:
    """
    Facade que simplifica a interface complexa do DataStore
    Fornece métodos de alto nível para operações comuns
    """
    
    def __init__(self, data_store):
        """
        Inicializa o Facade com uma referência ao DataStore
        
        Args:
            data_store: Instância do DataStore (Singleton)
        """
        self._data_store = data_store
    
    # === Métodos Simplificados para Viagens ===
    
    def create_trip_simple(self, user_id: int, destination: str, name: str,
                          start_date: str, end_date: str, budget: float = 0.0) -> Dict[str, Any]:
        """
        Cria uma viagem de forma simplificada
        
        Args:
            user_id: ID do usuário
            destination: Destino da viagem
            name: Nome da viagem
            start_date: Data de início
            end_date: Data de fim
            budget: Orçamento (opcional)
            
        Returns:
            Dicionário com informações da viagem criada
        """
        trip = self._data_store.add_trip(user_id, destination, name, start_date, end_date, "")
        
        if not trip:
            return {'success': False, 'error': 'Falha ao criar viagem'}
        
        # Atualizar orçamento se fornecido
        if budget > 0:
            self._data_store.update_trip_budget(trip.id, budget)
            trip = self._data_store.find_trip_by_id(trip.id)
        
        return {
            'success': True,
            'trip': trip.to_dict(),
            'message': 'Viagem criada com sucesso'
        }
    
    def create_complete_trip(self, user_id: int, destination: str, name: str,
                            start_date: str, end_date: str, budget: float = 0.0,
                            flight_data: Optional[Dict[str, Any]] = None,
                            hotel_data: Optional[Dict[str, Any]] = None,
                            activities: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Cria uma viagem completa com itens básicos em uma única operação
        
        Args:
            user_id: ID do usuário
            destination: Destino da viagem
            name: Nome da viagem
            start_date: Data de início
            end_date: Data de fim
            budget: Orçamento
            flight_data: Dados do voo (opcional)
            hotel_data: Dados do hotel (opcional)
            activities: Lista de atividades (opcional)
            
        Returns:
            Dicionário com a viagem completa e todos os itens criados
        """
        # Criar viagem
        result = self.create_trip_simple(user_id, destination, name, start_date, end_date, budget)
        
        if not result['success']:
            return result
        
        trip_id = result['trip']['id']
        created_items = {
            'flight': None,
            'hotel': None,
            'activities': []
        }
        
        # Adicionar voo se fornecido
        if flight_data:
            try:
                flight_data['trip_id'] = trip_id
                flight = self._data_store.add_flight(trip_id, **flight_data)
                created_items['flight'] = flight.to_dict()
            except Exception as e:
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append(f"Erro ao adicionar voo: {str(e)}")
        
        # Adicionar hotel se fornecido
        if hotel_data:
            try:
                hotel_data['trip_id'] = trip_id
                hotel = self._data_store.add_hotel(trip_id, **hotel_data)
                created_items['hotel'] = hotel.to_dict()
            except Exception as e:
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append(f"Erro ao adicionar hotel: {str(e)}")
        
        # Adicionar atividades se fornecidas
        if activities:
            for activity_data in activities:
                try:
                    activity_data['trip_id'] = trip_id
                    activity = self._data_store.add_activity(trip_id, **activity_data)
                    created_items['activities'].append(activity.to_dict())
                except Exception as e:
                    result['warnings'] = result.get('warnings', [])
                    result['warnings'].append(f"Erro ao adicionar atividade: {str(e)}")
        
        result['created_items'] = created_items
        result['message'] = 'Viagem completa criada com sucesso'
        
        return result
    
    def get_trip_summary(self, trip_id: int, user_id: int) -> Dict[str, Any]:
        """
        Obtém um resumo completo de uma viagem em uma única chamada
        
        Args:
            trip_id: ID da viagem
            user_id: ID do usuário para verificar permissões
            
        Returns:
            Dicionário com resumo completo da viagem
        """
        trip = self._data_store.find_trip_by_id(trip_id)
        
        if not trip:
            return {'success': False, 'error': 'Viagem não encontrada'}
        
        # Verificar permissão
        is_owner = trip.user_id == user_id
        is_collaborator = user_id in (trip.collaborators or [])
        
        if not (is_owner or is_collaborator):
            return {'success': False, 'error': 'Permissão negada'}
        
        # Obter detalhes
        details = self._data_store.get_details_for_trip(trip_id)
        expenses = self._data_store.get_expenses_for_trip(trip_id)
        
        # Calcular estatísticas
        total_expenses = sum(float(e.amount) for e in expenses)
        completed_flights = sum(1 for f in details.get('flights', []) if f.get('is_done', False))
        completed_hotels = sum(1 for h in details.get('hotels', []) if h.get('is_done', False))
        completed_activities = sum(1 for a in details.get('activities', []) if a.get('is_done', False))
        
        return {
            'success': True,
            'trip': trip.to_dict(),
            'details': details,
            'expenses': {
                'total': total_expenses,
                'count': len(expenses),
                'list': [e.to_dict() for e in expenses]
            },
            'statistics': {
                'total_flights': len(details.get('flights', [])),
                'completed_flights': completed_flights,
                'total_hotels': len(details.get('hotels', [])),
                'completed_hotels': completed_hotels,
                'total_activities': len(details.get('activities', [])),
                'completed_activities': completed_activities,
                'total_expenses': total_expenses,
                'budget_remaining': trip.budget - total_expenses if trip.budget > 0 else None,
                'completion_percentage': self._calculate_completion_percentage(details)
            },
            'permissions': {
                'is_owner': is_owner,
                'is_collaborator': is_collaborator,
                'can_edit': is_owner or is_collaborator
            }
        }
    
    def _calculate_completion_percentage(self, details: Dict[str, Any]) -> float:
        """Calcula porcentagem de conclusão dos itens"""
        total_items = (
            len(details.get('flights', [])) +
            len(details.get('hotels', [])) +
            len(details.get('activities', []))
        )
        
        if total_items == 0:
            return 0.0
        
        completed_items = (
            sum(1 for f in details.get('flights', []) if f.get('is_done', False)) +
            sum(1 for h in details.get('hotels', []) if h.get('is_done', False)) +
            sum(1 for a in details.get('activities', []) if a.get('is_done', False))
        )
        
        return round((completed_items / total_items) * 100, 2)
    
    # === Métodos Simplificados para Itens ===
    
    def add_trip_items_batch(self, trip_id: int, user_id: int,
                            flights: Optional[List[Dict[str, Any]]] = None,
                            hotels: Optional[List[Dict[str, Any]]] = None,
                            activities: Optional[List[Dict[str, Any]]] = None,
                            expenses: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Adiciona múltiplos itens à viagem em uma única operação
        
        Args:
            trip_id: ID da viagem
            user_id: ID do usuário
            flights: Lista de voos
            hotels: Lista de hotéis
            activities: Lista de atividades
            expenses: Lista de despesas
            
        Returns:
            Dicionário com todos os itens criados
        """
        # Verificar permissão
        trip = self._data_store.find_trip_by_id(trip_id)
        if not trip:
            return {'success': False, 'error': 'Viagem não encontrada'}
        
        is_owner = trip.user_id == user_id
        is_collaborator = user_id in (trip.collaborators or [])
        
        if not (is_owner or is_collaborator):
            return {'success': False, 'error': 'Permissão negada'}
        
        result = {
            'success': True,
            'created': {
                'flights': [],
                'hotels': [],
                'activities': [],
                'expenses': []
            },
            'errors': []
        }
        
        # Adicionar voos
        if flights:
            for flight_data in flights:
                try:
                    flight_data['trip_id'] = trip_id
                    flight = self._data_store.add_flight(trip_id, **flight_data)
                    result['created']['flights'].append(flight.to_dict())
                except Exception as e:
                    result['errors'].append(f"Erro ao adicionar voo: {str(e)}")
        
        # Adicionar hotéis
        if hotels:
            for hotel_data in hotels:
                try:
                    hotel_data['trip_id'] = trip_id
                    hotel = self._data_store.add_hotel(trip_id, **hotel_data)
                    result['created']['hotels'].append(hotel.to_dict())
                except Exception as e:
                    result['errors'].append(f"Erro ao adicionar hotel: {str(e)}")
        
        # Adicionar atividades
        if activities:
            for activity_data in activities:
                try:
                    activity_data['trip_id'] = trip_id
                    activity = self._data_store.add_activity(trip_id, **activity_data)
                    result['created']['activities'].append(activity.to_dict())
                except Exception as e:
                    result['errors'].append(f"Erro ao adicionar atividade: {str(e)}")
        
        # Adicionar despesas
        if expenses:
            for expense_data in expenses:
                try:
                    expense_data['trip_id'] = trip_id
                    expense = self._data_store.add_expense(trip_id, **expense_data)
                    result['created']['expenses'].append(expense.to_dict())
                except Exception as e:
                    result['errors'].append(f"Erro ao adicionar despesa: {str(e)}")
        
        result['message'] = f"Itens adicionados: {len(result['created']['flights'])} voos, " \
                           f"{len(result['created']['hotels'])} hotéis, " \
                           f"{len(result['created']['activities'])} atividades, " \
                           f"{len(result['created']['expenses'])} despesas"
        
        return result
    
    def get_user_dashboard(self, user_id: int) -> Dict[str, Any]:
        """
        Obtém um dashboard completo do usuário em uma única chamada
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dicionário com todas as informações do dashboard
        """
        trips = self._data_store.get_user_trips(user_id)
        user = self._data_store.find_user_by_id(user_id)
        
        if not user:
            return {'success': False, 'error': 'Usuário não encontrado'}
        
        # Calcular estatísticas agregadas
        total_trips = len(trips)
        total_budget = sum(t.budget for t in trips)
        upcoming_trips = [t for t in trips if t.start_date >= datetime.now().strftime("%Y-%m-%d")]
        past_trips = [t for t in trips if t.start_date < datetime.now().strftime("%Y-%m-%d")]
        
        # Obter recomendações recentes
        recommendations = self._data_store.get_user_recommendations(user_id, limit=5)
        
        # Obter notificações (se disponível)
        notifications = []
        try:
            from observers import EventManager
            event_manager = EventManager.get_instance()
            notification_observer = event_manager.get_notification_observer()
            if notification_observer:
                notifications = notification_observer.get_notifications(user_id, unread_only=True)
        except:
            pass
        
        return {
            'success': True,
            'user': user.to_dict(),
            'trips': {
                'total': total_trips,
                'upcoming': len(upcoming_trips),
                'past': len(past_trips),
                'list': [t.to_dict() for t in trips]
            },
            'statistics': {
                'total_trips': total_trips,
                'total_budget': total_budget,
                'average_budget_per_trip': round(total_budget / total_trips, 2) if total_trips > 0 else 0,
                'upcoming_trips_count': len(upcoming_trips),
                'past_trips_count': len(past_trips)
            },
            'recommendations': {
                'count': len(recommendations),
                'list': [r.to_dict() for r in recommendations]
            },
            'notifications': {
                'unread_count': len(notifications),
                'list': notifications[:5]  # Últimas 5
            }
        }
    
    # === Métodos Simplificados para Operações Compostas ===
    
    def duplicate_trip(self, trip_id: int, user_id: int, new_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Duplica uma viagem existente com todos os seus itens
        
        Args:
            trip_id: ID da viagem a ser duplicada
            user_id: ID do usuário que está duplicando
            new_name: Nome para a nova viagem (opcional)
            
        Returns:
            Dicionário com a nova viagem criada
        """
        original_trip = self._data_store.find_trip_by_id(trip_id)
        
        if not original_trip:
            return {'success': False, 'error': 'Viagem não encontrada'}
        
        # Verificar permissão (pode duplicar se for colaborador)
        is_owner = original_trip.user_id == user_id
        is_collaborator = user_id in (original_trip.collaborators or [])
        
        if not (is_owner or is_collaborator):
            return {'success': False, 'error': 'Permissão negada'}
        
        # Criar nova viagem
        new_name = new_name or f"{original_trip.name} (Cópia)"
        new_trip_result = self.create_trip_simple(
            user_id,
            original_trip.destination,
            new_name,
            original_trip.start_date,
            original_trip.end_date,
            original_trip.budget
        )
        
        if not new_trip_result['success']:
            return new_trip_result
        
        new_trip_id = new_trip_result['trip']['id']
        
        # Obter itens originais
        details = self._data_store.get_details_for_trip(trip_id)
        
        # Duplicar itens
        batch_result = self.add_trip_items_batch(
            new_trip_id,
            user_id,
            flights=[f for f in details.get('flights', []) if 'trip_id' not in f],
            hotels=[h for h in details.get('hotels', []) if 'trip_id' not in h],
            activities=[a for a in details.get('activities', []) if 'trip_id' not in a]
        )
        
        # Duplicar despesas
        expenses = self._data_store.get_expenses_for_trip(trip_id)
        if expenses:
            expense_data = [
                {
                    'description': e.description,
                    'amount': e.amount,
                    'currency': e.currency,
                    'date': e.date,
                    'category': e.category
                } for e in expenses
            ]
            expense_result = self.add_trip_items_batch(new_trip_id, user_id, expenses=expense_data)
            batch_result['created']['expenses'] = expense_result['created']['expenses']
        
        new_trip_result['duplicated_items'] = batch_result['created']
        new_trip_result['message'] = 'Viagem duplicada com sucesso'
        
        return new_trip_result
    
    def share_trip_with_user(self, trip_id: int, owner_id: int, 
                            collaborator_email: str) -> Dict[str, Any]:
        """
        Compartilha uma viagem com um usuário pelo email em uma única operação
        
        Args:
            trip_id: ID da viagem
            owner_id: ID do dono da viagem
            collaborator_email: Email do colaborador
            
        Returns:
            Dicionário com resultado da operação
        """
        trip = self._data_store.find_trip_by_id(trip_id)
        
        if not trip:
            return {'success': False, 'error': 'Viagem não encontrada'}
        
        if trip.user_id != owner_id:
            return {'success': False, 'error': 'Apenas o dono pode compartilhar a viagem'}
        
        # Buscar usuário pelo email
        collaborator = self._data_store.find_user_by_email(collaborator_email)
        
        if not collaborator:
            return {'success': False, 'error': 'Usuário não encontrado'}
        
        if collaborator.id == owner_id:
            return {'success': False, 'error': 'Você já é o dono desta viagem'}
        
        # Adicionar colaborador
        updated_trip = self._data_store.add_collaborator_to_trip(trip_id, collaborator.id)
        
        if not updated_trip:
            return {'success': False, 'error': 'Falha ao adicionar colaborador'}
        
        return {
            'success': True,
            'trip': updated_trip.to_dict(),
            'collaborator': collaborator.to_dict(),
            'message': f'Viagem compartilhada com {collaborator.name}'
        }

