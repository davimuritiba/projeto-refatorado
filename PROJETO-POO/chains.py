# --- Chain of Responsibility Pattern Implementation ---
"""
Implementação do padrão Chain of Responsibility para processamento sequencial
de validações, autorizações e transformações de dados no Travel Itinerary Planner.
Permite criar pipelines flexíveis e extensíveis de processamento.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

# === Resultado do Processamento ===

class ProcessingResult:
    """Classe para encapsular o resultado do processamento na chain"""
    
    def __init__(self, success: bool = True, data: Dict[str, Any] = None, 
                 errors: List[str] = None, warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.errors = errors or []
        self.warnings = warnings or []
        self.processed_by = []  # Lista de handlers que processaram
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_error(self, error: str):
        """Adiciona um erro"""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """Adiciona um aviso"""
        self.warnings.append(warning)
    
    def mark_processed_by(self, handler_name: str):
        """Marca qual handler processou"""
        self.processed_by.append(handler_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'success': self.success,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'processed_by': self.processed_by,
            'timestamp': self.timestamp
        }

# === Handler Interface ===

class Handler(ABC):
    """Interface Handler - base para todos os handlers da chain"""
    
    def __init__(self, name: str):
        self.name = name
        self._next_handler: Optional['Handler'] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        """
        Define o próximo handler na chain
        
        Args:
            handler: Próximo handler
            
        Returns:
            O handler passado (para encadeamento fluente)
        """
        self._next_handler = handler
        return handler
    
    def handle(self, request: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Processa a requisição e passa para o próximo handler se necessário
        
        Args:
            request: Dados da requisição
            context: Contexto adicional (opcional)
            
        Returns:
            Resultado do processamento
        """
        result = self._process(request, context or {})
        result.mark_processed_by(self.name)
        
        # Se houver erro crítico, não passa adiante
        if not result.success and not self._should_continue_on_error():
            return result
        
        # Passa para o próximo handler se houver
        if self._next_handler and (result.success or self._should_continue_on_error()):
            next_result = self._next_handler.handle(request, context)
            # Mesclar resultados
            result.errors.extend(next_result.errors)
            result.warnings.extend(next_result.warnings)
            result.processed_by.extend(next_result.processed_by)
            result.data.update(next_result.data)
            # Se próximo falhou, resultado final falha
            if not next_result.success:
                result.success = False
        
        return result
    
    @abstractmethod
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """
        Processa a requisição (deve ser implementado pelas subclasses)
        
        Args:
            request: Dados da requisição
            context: Contexto adicional
            
        Returns:
            Resultado do processamento
        """
        pass
    
    def _should_continue_on_error(self) -> bool:
        """
        Define se deve continuar na chain mesmo após erro
        Por padrão, retorna False (para em caso de erro)
        """
        return False

# === Handlers de Validação ===

class DataSanitizationHandler(Handler):
    """Handler que sanitiza dados de entrada"""
    
    def __init__(self):
        super().__init__("DataSanitizationHandler")
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Sanitiza dados removendo espaços e convertendo tipos"""
        result = ProcessingResult()
        sanitized_data = {}
        
        for key, value in request.items():
            if isinstance(value, str):
                # Remove espaços extras
                sanitized_value = value.strip()
                # Converte strings vazias para None
                if sanitized_value == '':
                    sanitized_value = None
            elif isinstance(value, (int, float)):
                # Valida números
                if value < 0 and key not in ['weight']:  # weight pode ser negativo em alguns contextos
                    result.add_error(f"Valor negativo inválido para {key}")
                else:
                    sanitized_value = value
            else:
                sanitized_value = value
            
            sanitized_data[key] = sanitized_value
        
        result.data = sanitized_data
        return result

class FormatValidationHandler(Handler):
    """Handler que valida formato de dados"""
    
    def __init__(self, required_fields: List[str] = None):
        super().__init__("FormatValidationHandler")
        self.required_fields = required_fields or []
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Valida formato básico dos dados"""
        result = ProcessingResult()
        
        # Verificar campos obrigatórios
        missing_fields = [field for field in self.required_fields if not request.get(field)]
        if missing_fields:
            result.add_error(f"Campos obrigatórios faltando: {', '.join(missing_fields)}")
        
        # Validar formato de datas
        date_fields = ['start_date', 'end_date', 'checkin', 'checkout', 'date', 'departure', 'arrival']
        for field in date_fields:
            if field in request and request[field]:
                if not self._is_valid_date_format(request[field]):
                    result.add_warning(f"Formato de data inválido ou suspeito em {field}")
        
        # Validar formato de email se presente
        if 'email' in request and request['email']:
            if not self._is_valid_email(request['email']):
                result.add_error("Formato de email inválido")
        
        result.data = request.copy()
        return result
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Valida formato básico de data"""
        if not isinstance(date_str, str):
            return False
        # Aceita vários formatos comuns
        date_formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y']
        for fmt in date_formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        return False
    
    def _is_valid_email(self, email: str) -> bool:
        """Validação básica de email"""
        return '@' in email and '.' in email.split('@')[1]

class BusinessLogicValidationHandler(Handler):
    """Handler que valida regras de negócio"""
    
    def __init__(self):
        super().__init__("BusinessLogicValidationHandler")
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Valida regras de negócio específicas"""
        result = ProcessingResult()
        
        # Validar datas de viagem
        if 'start_date' in request and 'end_date' in request:
            try:
                start = datetime.strptime(request['start_date'], '%Y-%m-%d')
                end = datetime.strptime(request['end_date'], '%Y-%m-%d')
                if start > end:
                    result.add_error("Data de início não pode ser posterior à data de fim")
                if start < datetime.now():
                    result.add_warning("Data de início está no passado")
            except (ValueError, TypeError):
                pass
        
        # Validar datas de hotel
        if 'checkin' in request and 'checkout' in request:
            try:
                checkin = datetime.strptime(request['checkin'], '%Y-%m-%d')
                checkout = datetime.strptime(request['checkout'], '%Y-%m-%d')
                if checkin >= checkout:
                    result.add_error("Data de check-in deve ser anterior ao check-out")
            except (ValueError, TypeError):
                pass
        
        # Validar valores monetários
        if 'amount' in request:
            amount = float(request['amount']) if request['amount'] else 0
            if amount <= 0:
                result.add_error("Valor deve ser positivo")
            elif amount > 1000000:
                result.add_warning("Valor muito alto, verifique se está correto")
        
        # Validar orçamento
        if 'budget' in request:
            budget = float(request['budget']) if request['budget'] else 0
            if budget < 0:
                result.add_error("Orçamento não pode ser negativo")
        
        result.data = request.copy()
        return result

# === Handlers de Autorização ===

class PermissionCheckHandler(Handler):
    """Handler que verifica permissões do usuário"""
    
    def __init__(self, data_store):
        super().__init__("PermissionCheckHandler")
        self.data_store = data_store
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Verifica se o usuário tem permissão"""
        result = ProcessingResult()
        
        user_id = request.get('user_id') or context.get('user_id')
        trip_id = request.get('trip_id') or context.get('trip_id')
        
        if not user_id or not trip_id:
            result.add_error("user_id e trip_id são obrigatórios para verificação de permissão")
            return result
        
        # Verificar permissão
        trip = self.data_store.find_trip_by_id(trip_id)
        if not trip:
            result.add_error("Viagem não encontrada")
            return result
        
        is_owner = trip.user_id == user_id
        is_collaborator = user_id in (trip.collaborators or [])
        
        if not (is_owner or is_collaborator):
            result.add_error("Usuário não tem permissão para acessar esta viagem")
            return result
        
        result.data['has_permission'] = True
        result.data['is_owner'] = is_owner
        result.data['is_collaborator'] = is_collaborator
        return result

class LimitCheckHandler(Handler):
    """Handler que verifica limites e quotas"""
    
    def __init__(self, data_store, max_items_per_trip: int = 100):
        super().__init__("LimitCheckHandler")
        self.data_store = data_store
        self.max_items_per_trip = max_items_per_trip
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Verifica limites"""
        result = ProcessingResult()
        
        trip_id = request.get('trip_id') or context.get('trip_id')
        item_type = request.get('item_type') or context.get('item_type', 'item')
        
        if not trip_id:
            return result
        
        # Contar itens existentes
        details = self.data_store.get_details_for_trip(trip_id)
        total_items = (
            len(details.get('flights', [])) +
            len(details.get('hotels', [])) +
            len(details.get('activities', []))
        )
        
        if total_items >= self.max_items_per_trip:
            result.add_warning(f"Viagem está próxima do limite de {self.max_items_per_trip} itens ({total_items})")
        
        result.data['current_items_count'] = total_items
        result.data['max_items'] = self.max_items_per_trip
        return result

class StateCheckHandler(Handler):
    """Handler que verifica estado de objetos"""
    
    def __init__(self, data_store):
        super().__init__("StateCheckHandler")
        self.data_store = data_store
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Verifica estado de objetos (viagem, item, etc.)"""
        result = ProcessingResult()
        
        trip_id = request.get('trip_id') or context.get('trip_id')
        
        if trip_id:
            trip = self.data_store.find_trip_by_id(trip_id)
            if trip:
                # Verificar se viagem não está sugerida (pode ter diferentes regras)
                if trip.is_suggestion:
                    result.add_warning("Esta é uma viagem sugerida, algumas operações podem ser limitadas")
                
                result.data['trip_status'] = 'suggestion' if trip.is_suggestion else 'active'
        
        # Verificar estado de item se item_id estiver presente
        item_id = request.get('item_id') or context.get('item_id')
        item_type = request.get('item_type') or context.get('item_type')
        
        if item_id and item_type:
            collection_name = f"{item_type}s" if item_type != 'expense' else 'expenses'
            items = self.data_store._data.get(collection_name, [])
            item = next((i for i in items if i.get('id') == item_id), None)
            
            if item:
                if item.get('is_done', False):
                    result.add_warning(f"Item {item_type} {item_id} já está marcado como concluído")
                result.data['item_status'] = 'done' if item.get('is_done') else 'pending'
        
        return result

# === Handlers de Processamento de Dados ===

class DataEnrichmentHandler(Handler):
    """Handler que enriquece dados com informações adicionais"""
    
    def __init__(self, data_store):
        super().__init__("DataEnrichmentHandler")
        self.data_store = data_store
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """ Enriquece dados com informações adicionais"""
        result = ProcessingResult()
        enriched_data = request.copy()
        
        # Adicionar timestamps
        if 'created_at' not in enriched_data:
            enriched_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Enriquecer com informações de viagem
        trip_id = enriched_data.get('trip_id')
        if trip_id:
            trip = self.data_store.find_trip_by_id(trip_id)
            if trip:
                enriched_data['trip_destination'] = trip.destination
                enriched_data['trip_name'] = trip.name
        
        # Enriquecer com informações de usuário
        user_id = enriched_data.get('user_id')
        if user_id:
            user = self.data_store.find_user_by_id(user_id)
            if user:
                enriched_data['user_name'] = user.name
        
        result.data = enriched_data
        return result

class DataTransformationHandler(Handler):
    """Handler que transforma dados"""
    
    def __init__(self):
        super().__init__("DataTransformationHandler")
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        """Transforma dados para formato desejado"""
        result = ProcessingResult()
        transformed_data = request.copy()
        
        # Transformar valores monetários para float
        monetary_fields = ['amount', 'budget']
        for field in monetary_fields:
            if field in transformed_data and transformed_data[field]:
                try:
                    transformed_data[field] = float(transformed_data[field])
                except (ValueError, TypeError):
                    pass
        
        # Normalizar strings (capitalizar primeira letra)
        string_fields = ['name', 'destination', 'description', 'title']
        for field in string_fields:
            if field in transformed_data and isinstance(transformed_data[field], str):
                value = transformed_data[field]
                if value:
                    transformed_data[field] = value[0].upper() + value[1:] if len(value) > 1 else value.upper()
        
        # Padronizar códigos (maiúsculas)
        if 'code' in transformed_data and isinstance(transformed_data['code'], str):
            transformed_data['code'] = transformed_data['code'].upper()
        
        result.data = transformed_data
        return result

class ValidationChainBuilder:
    """Builder para construir chains de validação"""
    
    def __init__(self, data_store, required_fields: List[str] = None):
        self.data_store = data_store
        self.required_fields = required_fields or []
        self._chain_start = None
        self._chain_end = None
    
    def add_sanitization(self) -> 'ValidationChainBuilder':
        """Adiciona handler de sanitização"""
        handler = DataSanitizationHandler()
        self._add_handler(handler)
        return self
    
    def add_format_validation(self, required_fields: List[str] = None) -> 'ValidationChainBuilder':
        """Adiciona handler de validação de formato"""
        fields = required_fields or self.required_fields
        handler = FormatValidationHandler(fields)
        self._add_handler(handler)
        return self
    
    def add_business_validation(self) -> 'ValidationChainBuilder':
        """Adiciona handler de validação de negócio"""
        handler = BusinessLogicValidationHandler()
        self._add_handler(handler)
        return self
    
    def add_enrichment(self) -> 'ValidationChainBuilder':
        """Adiciona handler de enriquecimento"""
        handler = DataEnrichmentHandler(self.data_store)
        self._add_handler(handler)
        return self
    
    def add_transformation(self) -> 'ValidationChainBuilder':
        """Adiciona handler de transformação"""
        handler = DataTransformationHandler()
        self._add_handler(handler)
        return self
    
    def _add_handler(self, handler: Handler):
        """Adiciona handler à chain"""
        if not self._chain_start:
            self._chain_start = handler
            self._chain_end = handler
        else:
            self._chain_end.set_next(handler)
            self._chain_end = handler
    
    def build(self) -> Handler:
        """Constrói e retorna a chain"""
        if not self._chain_start:
            raise ValueError("Chain deve ter pelo menos um handler")
        return self._chain_start

class AuthorizationChainBuilder:
    """Builder para construir chains de autorização"""
    
    def __init__(self, data_store):
        self.data_store = data_store
        self._chain_start = None
        self._chain_end = None
    
    def add_permission_check(self) -> 'AuthorizationChainBuilder':
        """Adiciona verificação de permissão"""
        handler = PermissionCheckHandler(self.data_store)
        self._add_handler(handler)
        return self
    
    def add_limit_check(self, max_items: int = 100) -> 'AuthorizationChainBuilder':
        """Adiciona verificação de limites"""
        handler = LimitCheckHandler(self.data_store, max_items)
        self._add_handler(handler)
        return self
    
    def add_state_check(self) -> 'AuthorizationChainBuilder':
        """Adiciona verificação de estado"""
        handler = StateCheckHandler(self.data_store)
        self._add_handler(handler)
        return self
    
    def _add_handler(self, handler: Handler):
        """Adiciona handler à chain"""
        if not self._chain_start:
            self._chain_start = handler
            self._chain_end = handler
        else:
            self._chain_end.set_next(handler)
            self._chain_end = handler
    
    def build(self) -> Handler:
        """Constrói e retorna a chain"""
        if not self._chain_start:
            raise ValueError("Chain deve ter pelo menos um handler")
        return self._chain_start

class ProcessingChainBuilder:
    """Builder para construir chains de processamento completo"""
    
    def __init__(self, data_store, required_fields: List[str] = None):
        self.data_store = data_store
        self.required_fields = required_fields or []
        self._chain_start = None
        self._chain_end = None
    
    def add_all_validation_steps(self) -> 'ProcessingChainBuilder':
        """Adiciona todos os passos de validação"""
        self._add_handler(DataSanitizationHandler())
        self._add_handler(FormatValidationHandler(self.required_fields))
        self._add_handler(BusinessLogicValidationHandler())
        return self
    
    def add_all_authorization_steps(self) -> 'ProcessingChainBuilder':
        """Adiciona todos os passos de autorização"""
        self._add_handler(PermissionCheckHandler(self.data_store))
        self._add_handler(LimitCheckHandler(self.data_store))
        self._add_handler(StateCheckHandler(self.data_store))
        return self
    
    def add_all_processing_steps(self) -> 'ProcessingChainBuilder':
        """Adiciona todos os passos de processamento"""
        self._add_handler(DataEnrichmentHandler(self.data_store))
        self._add_handler(DataTransformationHandler())
        return self
    
    def add_custom_handler(self, handler: Handler) -> 'ProcessingChainBuilder':
        """Adiciona um handler customizado"""
        self._add_handler(handler)
        return self
    
    def _add_handler(self, handler: Handler):
        """Adiciona handler à chain"""
        if not self._chain_start:
            self._chain_start = handler
            self._chain_end = handler
        else:
            self._chain_end.set_next(handler)
            self._chain_end = handler
    
    def build(self) -> Handler:
        """Constrói e retorna a chain completa"""
        if not self._chain_start:
            raise ValueError("Chain deve ter pelo menos um handler")
        return self._chain_start

