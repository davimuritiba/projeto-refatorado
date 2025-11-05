# --- Decorator Pattern Implementation ---
"""
Implementação do padrão Decorator para adicionar funcionalidades decorativas
aos itens de itinerário sem modificar sua estrutura base.
Permite adicionar cache, logging, validação, formatação e outras funcionalidades dinamicamente.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import json

# === Componente Base ===

class ItineraryItemComponent(ABC):
    """Interface Component - define a interface base para itens de itinerário"""
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Retorna os dados do item"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Converte o item para dicionário"""
        pass

# === Decorator Base ===

class ItineraryItemDecorator(ItineraryItemComponent):
    """Decorator base - mantém referência ao componente decorado"""
    
    def __init__(self, component: ItineraryItemComponent):
        self._component = component
    
    def get_data(self) -> Dict[str, Any]:
        """Delega para o componente decorado"""
        return self._component.get_data()
    
    def to_dict(self) -> Dict[str, Any]:
        """Delega para o componente decorado"""
        return self._component.to_dict()

# === Decoradores Concretos ===

class CachedItemDecorator(ItineraryItemDecorator):
    """
    Decorator que adiciona funcionalidade de cache
    Armazena dados em cache para evitar processamento repetido
    """
    
    def __init__(self, component: ItineraryItemComponent, cache_ttl: int = 3600):
        super().__init__(component)
        self._cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = cache_ttl  # Time to live em segundos
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna dados do cache se válidos, senão busca do componente"""
        cache_key = id(self._component)
        
        # Verifica se existe cache válido
        if cache_key in self._cache:
            timestamp = self._cache_timestamp.get(cache_key, 0)
            elapsed = (datetime.now() - timestamp).total_seconds()
            
            if elapsed < self._cache_ttl:
                return self._cache[cache_key]
        
        # Busca dados do componente e armazena em cache
        data = self._component.get_data()
        self._cache[cache_key] = data
        self._cache_timestamp[cache_key] = datetime.now()
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna dicionário com informações de cache"""
        data = super().to_dict()
        data['_cached'] = True
        data['_cache_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return data
    
    def clear_cache(self):
        """Limpa o cache"""
        cache_key = id(self._component)
        if cache_key in self._cache:
            del self._cache[cache_key]
        if cache_key in self._cache_timestamp:
            del self._cache_timestamp[cache_key]

class LoggedItemDecorator(ItineraryItemDecorator):
    """
    Decorator que adiciona funcionalidade de logging
    Registra todas as operações realizadas no item
    """
    
    def __init__(self, component: ItineraryItemComponent, log_file: Optional[str] = None):
        super().__init__(component)
        self._log_file = log_file
        self._logs = []
    
    def get_data(self) -> Dict[str, Any]:
        """Registra acesso aos dados"""
        data = self._component.get_data()
        self._log(f"GET_DATA - Acessado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Registra conversão para dicionário"""
        data = self._component.to_dict()
        self._log(f"TO_DICT - Convertido em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return data
    
    def _log(self, message: str):
        """Registra mensagem no log"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': message,
            'item_id': self._component.get_data().get('id', 'unknown')
        }
        self._logs.append(log_entry)
        
        if self._log_file:
            try:
                with open(self._log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception as e:
                print(f"Erro ao escrever log: {e}")
    
    def get_logs(self) -> list:
        """Retorna histórico de logs"""
        return self._logs.copy()

class ValidatedItemDecorator(ItineraryItemDecorator):
    """
    Decorator que adiciona validação adicional
    Valida dados antes de retornar
    """
    
    def __init__(self, component: ItineraryItemComponent, validation_rules: Optional[Dict[str, Any]] = None):
        super().__init__(component)
        self._validation_rules = validation_rules or {}
    
    def get_data(self) -> Dict[str, Any]:
        """Valida dados antes de retornar"""
        data = self._component.get_data()
        self._validate(data)
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """Valida dados antes de converter"""
        data = self._component.to_dict()
        self._validate(data)
        return data
    
    def _validate(self, data: Dict[str, Any]):
        """Executa validações configuradas"""
        errors = []
        
        # Validação de campos obrigatórios
        required_fields = self._validation_rules.get('required', [])
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validação de tipos
        type_rules = self._validation_rules.get('types', {})
        for field, expected_type in type_rules.items():
            if field in data and not isinstance(data[field], expected_type):
                errors.append(f"Campo {field} deve ser do tipo {expected_type.__name__}")
        
        # Validação de valores
        value_rules = self._validation_rules.get('values', {})
        for field, validator_func in value_rules.items():
            if field in data:
                try:
                    if not validator_func(data[field]):
                        errors.append(f"Validação falhou para campo {field}")
                except Exception as e:
                    errors.append(f"Erro na validação de {field}: {str(e)}")
        
        if errors:
            raise ValueError(f"Erros de validação: {'; '.join(errors)}")

class FormattedItemDecorator(ItineraryItemDecorator):
    """
    Decorator que adiciona formatação de dados
    Formata valores para exibição (datas, moedas, etc.)
    """
    
    def __init__(self, component: ItineraryItemComponent, format_options: Optional[Dict[str, Any]] = None):
        super().__init__(component)
        self._format_options = format_options or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna dicionário com dados formatados"""
        data = self._component.to_dict()
        formatted_data = {}
        
        for key, value in data.items():
            if key in self._format_options:
                formatter = self._format_options[key]
                formatted_data[key] = formatter(value)
            else:
                formatted_data[key] = value
        
        return formatted_data
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna dados formatados"""
        return self.to_dict()

# === Wrapper para ItineraryItem ===

class ItineraryItemWrapper(ItineraryItemComponent):
    """Wrapper que adapta ItineraryItem para o padrão Decorator"""
    
    def __init__(self, item):
        """Inicializa wrapper com um ItineraryItem"""
        self._item = item
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna dados do item"""
        return self._item.to_dict()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte item para dicionário"""
        return self._item.to_dict()
    
    def get_item(self):
        """Retorna o item original"""
        return self._item

