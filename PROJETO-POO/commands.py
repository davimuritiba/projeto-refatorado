# --- Command Pattern Implementation ---
"""
Implementação do padrão Command para encapsular operações como objetos no Travel Itinerary Planner.
Permite desfazer/refazer operações, logging, auditoria e execução em fila.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import copy

# === Status dos Comandos ===

class CommandStatus(Enum):
    """Enum com status possíveis de um comando"""
    PENDING = "pending"
    EXECUTED = "executed"
    UNDONE = "undone"
    FAILED = "failed"

# === Interface Command ===

class Command(ABC):
    """Interface Command - define o contrato para operações encapsuladas"""
    
    def __init__(self, receiver, data: Dict[str, Any]):
        """
        Inicializa o comando
        
        Args:
            receiver: Objeto que executa a operação (geralmente DataStore)
            data: Dados necessários para executar o comando
        """
        self._receiver = receiver
        self._data = data.copy()
        self._status = CommandStatus.PENDING
        self._executed_at = None
        self._undone_at = None
        self._result = None
        self._error = None
    
    @abstractmethod
    def execute(self) -> Any:
        """
        Executa o comando
        
        Returns:
            Resultado da execução
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        Desfaz o comando
        
        Returns:
            True se desfeito com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_command_name(self) -> str:
        """Retorna o nome do comando para identificação"""
        pass
    
    def can_undo(self) -> bool:
        """Verifica se o comando pode ser desfeito"""
        return self._status == CommandStatus.EXECUTED
    
    def get_status(self) -> CommandStatus:
        """Retorna o status atual do comando"""
        return self._status
    
    def get_result(self) -> Any:
        """Retorna o resultado da execução"""
        return self._result
    
    def get_error(self) -> Optional[str]:
        """Retorna erro se houver"""
        return self._error
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o comando para dicionário"""
        return {
            'command_name': self.get_command_name(),
            'status': self._status.value,
            'executed_at': self._executed_at,
            'undone_at': self._undone_at,
            'data': self._data,
            'error': self._error
        }

# === Comandos Concretos ===

class CreateTripCommand(Command):
    """Comando para criar uma nova viagem"""
    
    def __init__(self, receiver, user_id: int, destination: str, name: str, 
                 start_date: str, end_date: str, share_code: str = ""):
        data = {
            'user_id': user_id,
            'destination': destination,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            'share_code': share_code
        }
        super().__init__(receiver, data)
        self._trip_id = None
    
    def execute(self) -> Any:
        """Executa a criação da viagem"""
        try:
            trip = self._receiver.add_trip(
                self._data['user_id'],
                self._data['destination'],
                self._data['name'],
                self._data['start_date'],
                self._data['end_date'],
                self._data['share_code']
            )
            
            if trip:
                self._trip_id = trip.id
                self._result = trip.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao criar viagem: código de compartilhamento já existe"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a criação da viagem (remove ela)"""
        if not self.can_undo() or not self._trip_id:
            return False
        
        try:
            # Remover a viagem do banco de dados
            trips = self._receiver._data.get('trips', [])
            self._receiver._data['trips'] = [
                t for t in trips if t.get('id') != self._trip_id
            ]
            self._receiver._save_data()
            
            self._status = CommandStatus.UNDONE
            self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
            
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "CreateTripCommand"

class UpdateTripBudgetCommand(Command):
    """Comando para atualizar o orçamento de uma viagem"""
    
    def __init__(self, receiver, trip_id: int, new_budget: float):
        data = {
            'trip_id': trip_id,
            'new_budget': new_budget
        }
        super().__init__(receiver, data)
        self._old_budget = None
    
    def execute(self) -> Any:
        """Executa a atualização do orçamento"""
        try:
            # Buscar orçamento atual
            trip = self._receiver.find_trip_by_id(self._data['trip_id'])
            if not trip:
                self._status = CommandStatus.FAILED
                self._error = "Viagem não encontrada"
                return None
            
            self._old_budget = trip.budget
            
            # Atualizar orçamento
            updated_trip = self._receiver.update_trip_budget(
                self._data['trip_id'],
                self._data['new_budget']
            )
            
            if updated_trip:
                self._result = updated_trip.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao atualizar orçamento"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a atualização (restaura orçamento anterior)"""
        if not self.can_undo() or self._old_budget is None:
            return False
        
        try:
            updated_trip = self._receiver.update_trip_budget(
                self._data['trip_id'],
                self._old_budget
            )
            
            if updated_trip:
                self._status = CommandStatus.UNDONE
                self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
            else:
                return False
                
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "UpdateTripBudgetCommand"

class AddCollaboratorCommand(Command):
    """Comando para adicionar um colaborador a uma viagem"""
    
    def __init__(self, receiver, trip_id: int, user_id: int):
        data = {
            'trip_id': trip_id,
            'user_id': user_id
        }
        super().__init__(receiver, data)
        self._was_collaborator = False
    
    def execute(self) -> Any:
        """Executa a adição do colaborador"""
        try:
            trip = self._receiver.find_trip_by_id(self._data['trip_id'])
            if not trip:
                self._status = CommandStatus.FAILED
                self._error = "Viagem não encontrada"
                return None
            
            # Verificar se já era colaborador
            self._was_collaborator = self._data['user_id'] in (trip.collaborators or [])
            
            if self._was_collaborator:
                self._status = CommandStatus.FAILED
                self._error = "Usuário já é colaborador desta viagem"
                return None
            
            # Adicionar colaborador
            updated_trip = self._receiver.add_collaborator_to_trip(
                self._data['trip_id'],
                self._data['user_id']
            )
            
            if updated_trip:
                self._result = updated_trip.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao adicionar colaborador"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a adição (remove o colaborador)"""
        if not self.can_undo():
            return False
        
        try:
            trip = self._receiver.find_trip_by_id(self._data['trip_id'])
            if not trip:
                return False
            
            # Remover colaborador
            collaborators = trip.collaborators or []
            if self._data['user_id'] in collaborators:
                collaborators.remove(self._data['user_id'])
                
                # Atualizar no banco
                for t in self._receiver._data.get('trips', []):
                    if t.get('id') == self._data['trip_id']:
                        t['collaborators'] = collaborators
                        self._receiver._save_data()
                        break
                
                self._status = CommandStatus.UNDONE
                self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
            
            return False
                
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "AddCollaboratorCommand"

class AddFlightCommand(Command):
    """Comando para adicionar um voo a uma viagem"""
    
    def __init__(self, receiver, trip_id: int, company: str, code: str, 
                 departure: str, arrival: str, **kwargs):
        data = {
            'trip_id': trip_id,
            'company': company,
            'code': code,
            'departure': departure,
            'arrival': arrival,
            **kwargs
        }
        super().__init__(receiver, data)
        self._flight_id = None
    
    def execute(self) -> Any:
        """Executa a adição do voo"""
        try:
            flight = self._receiver.add_flight(
                self._data['trip_id'],
                company=self._data['company'],
                code=self._data['code'],
                departure=self._data['departure'],
                arrival=self._data['arrival'],
                **{k: v for k, v in self._data.items() 
                   if k not in ['trip_id', 'company', 'code', 'departure', 'arrival']}
            )
            
            if flight:
                self._flight_id = flight.id
                self._result = flight.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao adicionar voo"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a adição (remove o voo)"""
        if not self.can_undo() or not self._flight_id:
            return False
        
        try:
            flights = self._receiver._data.get('flights', [])
            self._receiver._data['flights'] = [
                f for f in flights if f.get('id') != self._flight_id
            ]
            self._receiver._save_data()
            
            self._status = CommandStatus.UNDONE
            self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
            
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "AddFlightCommand"

class AddHotelCommand(Command):
    """Comando para adicionar um hotel a uma viagem"""
    
    def __init__(self, receiver, trip_id: int, name: str, checkin: str, checkout: str, **kwargs):
        data = {
            'trip_id': trip_id,
            'name': name,
            'checkin': checkin,
            'checkout': checkout,
            **kwargs
        }
        super().__init__(receiver, data)
        self._hotel_id = None
    
    def execute(self) -> Any:
        """Executa a adição do hotel"""
        try:
            hotel = self._receiver.add_hotel(
                self._data['trip_id'],
                name=self._data['name'],
                checkin=self._data['checkin'],
                checkout=self._data['checkout'],
                **{k: v for k, v in self._data.items() 
                   if k not in ['trip_id', 'name', 'checkin', 'checkout']}
            )
            
            if hotel:
                self._hotel_id = hotel.id
                self._result = hotel.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao adicionar hotel"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a adição (remove o hotel)"""
        if not self.can_undo() or not self._hotel_id:
            return False
        
        try:
            hotels = self._receiver._data.get('hotels', [])
            self._receiver._data['hotels'] = [
                h for h in hotels if h.get('id') != self._hotel_id
            ]
            self._receiver._save_data()
            
            self._status = CommandStatus.UNDONE
            self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
            
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "AddHotelCommand"

class AddActivityCommand(Command):
    """Comando para adicionar uma atividade a uma viagem"""
    
    def __init__(self, receiver, trip_id: int, description: str, date: str, **kwargs):
        data = {
            'trip_id': trip_id,
            'description': description,
            'date': date,
            **kwargs
        }
        super().__init__(receiver, data)
        self._activity_id = None
    
    def execute(self) -> Any:
        """Executa a adição da atividade"""
        try:
            activity = self._receiver.add_activity(
                self._data['trip_id'],
                description=self._data['description'],
                date=self._data['date'],
                **{k: v for k, v in self._data.items() 
                   if k not in ['trip_id', 'description', 'date']}
            )
            
            if activity:
                self._activity_id = activity.id
                self._result = activity.to_dict()
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao adicionar atividade"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a adição (remove a atividade)"""
        if not self.can_undo() or not self._activity_id:
            return False
        
        try:
            activities = self._receiver._data.get('activities', [])
            self._receiver._data['activities'] = [
                a for a in activities if a.get('id') != self._activity_id
            ]
            self._receiver._save_data()
            
            self._status = CommandStatus.UNDONE
            self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
            
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "AddActivityCommand"

class UpdateItemStatusCommand(Command):
    """Comando para atualizar o status de um item do itinerário"""
    
    def __init__(self, receiver, item_type: str, item_id: int, is_done: bool):
        data = {
            'item_type': item_type,
            'item_id': item_id,
            'is_done': is_done
        }
        super().__init__(receiver, data)
        self._previous_status = None
    
    def execute(self) -> Any:
        """Executa a atualização do status"""
        try:
            collection_name = f"{self._data['item_type']}s" if self._data['item_type'] != 'expense' else 'expenses'
            
            # Buscar status atual
            items = self._receiver._data.get(collection_name, [])
            item = next((i for i in items if i.get('id') == self._data['item_id']), None)
            
            if not item:
                self._status = CommandStatus.FAILED
                self._error = f"{self._data['item_type']} não encontrado"
                return None
            
            self._previous_status = item.get('is_done', False)
            
            # Atualizar status
            updated_item = self._receiver._update_item_status(
                collection_name,
                self._data['item_id'],
                self._data['is_done']
            )
            
            if updated_item:
                self._result = updated_item
                self._status = CommandStatus.EXECUTED
                self._executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return self._result
            else:
                self._status = CommandStatus.FAILED
                self._error = "Falha ao atualizar status"
                return None
                
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self) -> bool:
        """Desfaz a atualização (restaura status anterior)"""
        if not self.can_undo() or self._previous_status is None:
            return False
        
        try:
            collection_name = f"{self._data['item_type']}s" if self._data['item_type'] != 'expense' else 'expenses'
            updated_item = self._receiver._update_item_status(
                collection_name,
                self._data['item_id'],
                self._previous_status
            )
            
            if updated_item:
                self._status = CommandStatus.UNDONE
                self._undone_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return True
            else:
                return False
                
        except Exception as e:
            self._error = f"Erro ao desfazer: {str(e)}"
            return False
    
    def get_command_name(self) -> str:
        return "UpdateItemStatusCommand"

# === Command Invoker (gerenciador de comandos) ===

class CommandInvoker:
    """
    Gerenciador de comandos que mantém histórico para desfazer/refazer
    Implementa o Command Pattern com suporte a histórico
    """
    
    def __init__(self):
        self._history: List[Command] = []
        self._current_index = -1  # Índice do comando atual no histórico
        self._max_history_size = 100  # Limite de histórico
    
    def execute_command(self, command: Command) -> Any:
        """
        Executa um comando e adiciona ao histórico
        
        Args:
            command: Comando a ser executado
            
        Returns:
            Resultado da execução do comando
        """
        # Remover comandos após o índice atual (ao executar novo comando após desfazer)
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        # Executar comando
        result = command.execute()
        
        # Adicionar ao histórico se executado com sucesso
        if command.get_status() == CommandStatus.EXECUTED:
            self._history.append(command)
            self._current_index = len(self._history) - 1
            
            # Limitar tamanho do histórico
            if len(self._history) > self._max_history_size:
                self._history.pop(0)
                self._current_index -= 1
        
        return result
    
    def undo(self) -> bool:
        """
        Desfaz o último comando executado
        
        Returns:
            True se desfeito com sucesso, False caso contrário
        """
        if not self.can_undo():
            return False
        
        command = self._history[self._current_index]
        
        if command.can_undo():
            success = command.undo()
            if success:
                self._current_index -= 1
            return success
        
        return False
    
    def redo(self) -> bool:
        """
        Refaz o último comando desfeito
        
        Returns:
            True se refeito com sucesso, False caso contrário
        """
        if not self.can_redo():
            return False
        
        self._current_index += 1
        command = self._history[self._current_index]
        
        # Refazer executando novamente
        return command.execute() is not None
    
    def can_undo(self) -> bool:
        """Verifica se é possível desfazer"""
        return self._current_index >= 0
    
    def can_redo(self) -> bool:
        """Verifica se é possível refazer"""
        return self._current_index < len(self._history) - 1
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Retorna o histórico de comandos"""
        return [cmd.to_dict() for cmd in self._history]
    
    def get_history_range(self, start: int = 0, end: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna um range do histórico"""
        if end is None:
            end = len(self._history)
        return [cmd.to_dict() for cmd in self._history[start:end]]
    
    def clear_history(self):
        """Limpa o histórico"""
        self._history.clear()
        self._current_index = -1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do histórico"""
        if not self._history:
            return {
                'total_commands': 0,
                'executed': 0,
                'undone': 0,
                'failed': 0
            }
        
        stats = {
            'total_commands': len(self._history),
            'executed': 0,
            'undone': 0,
            'failed': 0,
            'by_command_type': {}
        }
        
        for cmd in self._history:
            status = cmd.get_status()
            if status == CommandStatus.EXECUTED:
                stats['executed'] += 1
            elif status == CommandStatus.UNDONE:
                stats['undone'] += 1
            elif status == CommandStatus.FAILED:
                stats['failed'] += 1
            
            cmd_name = cmd.get_command_name()
            stats['by_command_type'][cmd_name] = stats['by_command_type'].get(cmd_name, 0) + 1
        
        return stats

# === Command Factory ===

class CommandFactory:
    """Factory para criar comandos de forma conveniente"""
    
    @staticmethod
    def create_trip_command(receiver, user_id: int, destination: str, name: str,
                           start_date: str, end_date: str, share_code: str = "") -> CreateTripCommand:
        """Cria um comando para criar viagem"""
        return CreateTripCommand(receiver, user_id, destination, name, start_date, end_date, share_code)
    
    @staticmethod
    def create_update_budget_command(receiver, trip_id: int, new_budget: float) -> UpdateTripBudgetCommand:
        """Cria um comando para atualizar orçamento"""
        return UpdateTripBudgetCommand(receiver, trip_id, new_budget)
    
    @staticmethod
    def create_add_collaborator_command(receiver, trip_id: int, user_id: int) -> AddCollaboratorCommand:
        """Cria um comando para adicionar colaborador"""
        return AddCollaboratorCommand(receiver, trip_id, user_id)
    
    @staticmethod
    def create_add_flight_command(receiver, trip_id: int, company: str, code: str,
                                  departure: str, arrival: str, **kwargs) -> AddFlightCommand:
        """Cria um comando para adicionar voo"""
        return AddFlightCommand(receiver, trip_id, company, code, departure, arrival, **kwargs)
    
    @staticmethod
    def create_add_hotel_command(receiver, trip_id: int, name: str, checkin: str,
                                 checkout: str, **kwargs) -> AddHotelCommand:
        """Cria um comando para adicionar hotel"""
        return AddHotelCommand(receiver, trip_id, name, checkin, checkout, **kwargs)
    
    @staticmethod
    def create_add_activity_command(receiver, trip_id: int, description: str,
                                   date: str, **kwargs) -> AddActivityCommand:
        """Cria um comando para adicionar atividade"""
        return AddActivityCommand(receiver, trip_id, description, date, **kwargs)
    
    @staticmethod
    def create_update_item_status_command(receiver, item_type: str, item_id: int,
                                        is_done: bool) -> UpdateItemStatusCommand:
        """Cria um comando para atualizar status de item"""
        return UpdateItemStatusCommand(receiver, item_type, item_id, is_done)

