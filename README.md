# 🧭 Travel Itinerary Planner - Refatorado com Padrões de Design

> **Projeto Original:** [edgarvtt/Travel-Itinerary-Planner](https://github.com/edgarvtt/Travel-Itinerary-Planner)  
> **Versão Refatorada:** Expandida com padrões de design, arquitetura modular e funcionalidades avançadas
> 
> **Proximos Passos:** Implementar mais um padrao comportamental (Obsever) e outros estruturais



**✅ REFATORAÇÃO CONCLUÍDA COM PADRÕES DE DESIGN**

Este projeto foi completamente refatorado com implementação de **10 padrões de design**, arquitetura modular e sistema de recomendação inteligente.

## 📋 **Funcionalidades Implementadas**

### ✅ **Totalmente Implementadas**

1. **✅ Criação e personalização de itinerários**
   - Sistema completo de criação de viagens
   - Adição de voos, hotéis, atividades e despesas
   - Interface web responsiva

2. **✅ Ferramentas de Planejamento Colaborativo**
   - Sistema de códigos de compartilhamento
   - Convite de colaboradores em tempo real
   - Planejamento conjunto de itinerários

3. **✅ Acompanhamento de despesas e gerenciamento de orçamento**
   - Controle detalhado de gastos por categoria
   - Cálculo automático de orçamento
   - Interface visual do orçamento

4. **✅ Sistema de Usuários e Autenticação**
   - Cadastro e login de usuários
   - Dashboard personalizado
   - Gerenciamento de sessões

5. **✅ Guias e recursos de viagem**
   - Guias culturais, gastronômicos e de transporte
   - Recursos úteis (hospitais, embaixadas, aeroportos)
   - Sistema de categorização e tags
   - API completa para gerenciamento

6. **✅ Avaliações de usuários e contribuições da comunidade**
   - Sistema de reviews e ratings
   - Contribuições da comunidade (dicas, destinos)
   - Reações (likes/dislikes) em conteúdo
   - API para gerenciamento de conteúdo colaborativo

7. **✅ Sistema de Recomendação Inteligente** *(NOVO - Strategy Pattern)*
   - Múltiplas estratégias de recomendação (clima, orçamento, interesses, híbrida)
   - Algoritmos personalizáveis por usuário
   - Comparação de estratégias em tempo real
   - API para testar e comparar algoritmos

8. **✅ Cálculo de Orçamento Adaptativo** *(NOVO - Strategy Pattern)*
   - Estratégias de cálculo (diário, por categoria, flexível)
   - Adaptação ao perfil do usuário
   - Cálculos baseados em destino e preferências
   - API para diferentes métodos de cálculo

### 🔄 **Parcialmente Implementadas - Partes que possuem dependências externas não foram feitas**

9. **🔄 Acesso móvel e funcionalidade offline**
   - Interface responsiva implementada
   - **Pendente:** Funcionalidade offline

### ❌ **Não Implementadas - Funcionalidades que possuem dependências externas**

10. **❌ Integração de reservas**
    - **Motivo:** Depende de APIs pagas externas
    - **Impacto:** Não pode ser implementado sem custos adicionais

11. **❌ Integração de mapas e planejamento de rotas**
    - **Motivo:** Depende de APIs de mapas (Google Maps, OpenStreetMap)
    - **Impacto:** Requer chaves de API e configuração externa

## 🎯 **Padrões de Design Implementados**

### **1. Singleton Pattern** ✅
```python
class DataStore:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Garante uma única instância em toda a aplicação
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```
**Benefícios:** Gerenciamento centralizado de dados, thread-safety, consistência de estado.

### **2. Factory Method Pattern** ✅
```python
class ItineraryItemFactory(ABC):
    @abstractmethod
    def create_item(self, item_id, trip_id, **kwargs):
        pass

class FlightFactory(ItineraryItemFactory):
    def create_item(self, item_id, trip_id, **kwargs):
        return Flight(item_id, trip_id, **kwargs)
```
**Benefícios:** Criação flexível de objetos, extensibilidade, desacoplamento.

### **3. Builder Pattern** ✅
```python
class TripBuilder:
    def set_destination(self, destination):
        self._trip_data['destination'] = destination
        return self
    
    def set_dates(self, start_date, end_date):
        self._trip_data['start_date'] = start_date
        self._trip_data['end_date'] = end_date
        return self
    
    def build(self):
        return Trip(**self._trip_data)
```
**Benefícios:** Construção fluente, validação integrada, flexibilidade na criação.

### **4. Strategy Pattern** ✅
```python
class RecommendationStrategy(ABC):
    @abstractmethod
    def calculate_score(self, user_preferences, user_profile, target_item):
        pass

class ClimateBasedRecommendation(RecommendationStrategy):
    def calculate_score(self, user_preferences, user_profile, target_item):
        # Algoritmo baseado em clima
        return score

class BudgetBasedRecommendation(RecommendationStrategy):
    def calculate_score(self, user_preferences, user_profile, target_item):
        # Algoritmo baseado em orçamento
        return score
```
**Benefícios:** Algoritmos intercambiáveis, extensibilidade, personalização.

## 🛡️ **Tratamento de Exceções**

O projeto implementa tratamento robusto de exceções em todo o código, com **89 blocos try/except** distribuídos pelos módulos principais. O tratamento de exceções garante que erros sejam capturados e tratados adequadamente, melhorando a robustez e experiência do usuário.

### **Tipos de Tratamento Implementados**

#### **1. Tratamento Específico por Tipo de Exceção**
Captura exceções específicas como `ValueError` para validações e `Exception` genérica para erros inesperados:

```python
# Exemplo de routes.py
try:
    processed_flight = db.process_item('flight', data, trip_id, user_id)
    return jsonify({
        'message': 'Voo processado com sucesso',
        'flight': processed_flight.to_dict()
    }), Config.HTTP_STATUS['CREATED']
except ValueError as e:
    return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
except Exception as e:
    return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']
```

#### **2. Tratamento em Padrão Command**
Os comandos encapsulam exceções durante a execução, mantendo o estado do comando:

```python
# Exemplo de commands.py
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
        return self._result
    else:
        self._status = CommandStatus.FAILED
        self._error = "Falha ao criar viagem: código de compartilhamento já existe"
        return None
        
except Exception as e:
    self._status = CommandStatus.FAILED
    self._error = str(e)
    return None
```

#### **3. Tratamento em Padrão Facade**
O Facade trata exceções silenciosamente para operações opcionais, permitindo que operações principais continuem mesmo se operações secundárias falharem:

```python
# Exemplo de facade.py
try:
    from observers import EventManager
    event_manager = EventManager.get_instance()
    notification_observer = event_manager.get_notification_observer()
    if notification_observer:
        notifications = notification_observer.get_notifications(user_id, unread_only=True)
except:
    pass  # Notificações são opcionais, não devem interromper o fluxo principal
```

#### **4. Validação com Try/Except**
Uso de try/except para validação de formatos e conversão de tipos:

```python
# Exemplo de chains.py
def _is_valid_date_format(self, date_str: str) -> bool:
    """Valida se a data está em um formato válido"""
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False
```

#### **5. Levantamento de Exceções Personalizadas**
O código também levanta exceções específicas para validações de negócio:

```python
# Exemplo de app.py
if not item_data:
    raise ValueError("Dados do item não podem ser vazios")

if not item_data.get('trip_id'):
    raise ValueError("ID da viagem é obrigatório")

if start_date > end_date:
    raise ValueError("Data de início não pode ser posterior à data de fim")
```

### **Estatísticas de Tratamento de Exceções**

| Arquivo | Blocos Try | Exceções Tratadas |
|---------|-----------|-------------------|
| `routes.py` | ~28 | ValueError, Exception |
| `sample_data.py` | ~50 | Exception |
| `commands.py` | ~14 | Exception |
| `facade.py` | ~7 | Exception |
| `chains.py` | ~4 | ValueError, Exception |
| `observers.py` | ~1 | Exception |
| `travel.py` | ~5 | ValueError, IndexError |

**Total:** 89 blocos try/except implementados no projeto.

## 🎯 **Padrões de Design Implementados (Completos)**

### **📦 Padrões Criacionais**

#### **1. Singleton Pattern** ✅
```python
class DataStore:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Garante uma única instância em toda a aplicação
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```
**Benefícios:** Gerenciamento centralizado de dados, thread-safety, consistência de estado.

#### **2. Factory Method Pattern** ✅
```python
class ItineraryItemFactory(ABC):
    @abstractmethod
    def create_item(self, item_id, trip_id, **kwargs):
        pass

class FlightFactory(ItineraryItemFactory):
    def create_item(self, item_id, trip_id, **kwargs):
        return Flight(item_id, trip_id, **kwargs)
```
**Benefícios:** Criação flexível de objetos, extensibilidade, desacoplamento.

#### **3. Builder Pattern** ✅
```python
class TripBuilder:
    def set_destination(self, destination):
        self._trip_data['destination'] = destination
        return self
    
    def set_dates(self, start_date, end_date):
        self._trip_data['start_date'] = start_date
        self._trip_data['end_date'] = end_date
        return self
    
    def build(self):
        return Trip(**self._trip_data)
```
**Benefícios:** Construção fluente, validação integrada, flexibilidade na criação.

### **🏗️ Padrões Estruturais**

#### **4. Facade Pattern** ✅
```python
class TravelFacade:
    """
    Facade que simplifica a interface complexa do DataStore
    Fornece métodos de alto nível para operações comuns
    """
    
    def __init__(self, data_store):
        self._data_store = data_store
    
    def create_trip_simple(self, user_id: int, destination: str, name: str,
                          start_date: str, end_date: str, budget: float = 0.0):
        """Cria uma viagem de forma simplificada"""
        trip = self._data_store.add_trip(user_id, destination, name, start_date, end_date, "")
        
        if not trip:
            return {'success': False, 'error': 'Falha ao criar viagem'}
        
        # Atualizar orçamento se fornecido
        if budget > 0:
            self._data_store.update_trip_budget(trip.id, budget)
        
        return {'success': True, 'trip': trip.to_dict()}
```
**Benefícios:** Interface simplificada, oculta complexidade, facilita uso do sistema.

#### **5. Adapter Pattern** ✅
```python
class ItineraryItemAdapter(ABC):
    """Interface Target - define o formato padrão interno do sistema"""
    
    @abstractmethod
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class ExternalFlightAPIAdapter(ItineraryItemAdapter):
    """Adaptador para API externa de voos"""
    
    def adapt(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'company': external_data.get('airline', 'Unknown'),
            'code': external_data.get('flight_number', 'N/A'),
            'departure': self._format_datetime(external_data.get('departure_time')),
            'arrival': self._format_datetime(external_data.get('arrival_time'))
        }

class AdapterManager:
    """Gerenciador de adaptadores"""
    
    def adapt_data(self, item_type: str, external_data: Dict[str, Any]):
        adapter = self._adapters[item_type]
        return adapter.adapt(external_data)
```
**Benefícios:** Integração com APIs externas, desacoplamento, flexibilidade de formatos.

#### **6. Decorator Pattern** ✅
```python
class ItineraryItemDecorator(ABC):
    """Decorator base - mantém referência ao componente decorado"""
    
    def __init__(self, component: ItineraryItemComponent):
        self._component = component

class CachedItemDecorator(ItineraryItemDecorator):
    """Decorator que adiciona funcionalidade de cache"""
    
    def get_data(self) -> Dict[str, Any]:
        # Verifica cache antes de buscar dados
        if cache_key in self._cache:
            return self._cache[cache_key]
        data = self._component.get_data()
        self._cache[cache_key] = data
        return data

class LoggedItemDecorator(ItineraryItemDecorator):
    """Decorator que adiciona funcionalidade de logging"""
    
    def get_data(self) -> Dict[str, Any]:
        data = self._component.get_data()
        self._log(f"GET_DATA - Acessado em {datetime.now()}")
        return data

class ValidatedItemDecorator(ItineraryItemDecorator):
    """Decorator que adiciona validação adicional"""
    
    def get_data(self) -> Dict[str, Any]:
        data = self._component.get_data()
        self._validate(data)
        return data
```
**Benefícios:** Adiciona funcionalidades dinamicamente, composição flexível, extensibilidade sem modificar classes base.

### **⚙️ Padrões Comportamentais**

#### **7. Strategy Pattern** ✅
```python
class RecommendationStrategy(ABC):
    @abstractmethod
    def calculate_score(self, user_preferences, user_profile, target_item):
        pass

class ClimateBasedRecommendation(RecommendationStrategy):
    def calculate_score(self, user_preferences, user_profile, target_item):
        # Algoritmo baseado em clima
        return score

class BudgetBasedRecommendation(RecommendationStrategy):
    def calculate_score(self, user_preferences, user_profile, target_item):
        # Algoritmo baseado em orçamento
        return score
```
**Benefícios:** Algoritmos intercambiáveis, extensibilidade, personalização.

#### **8. Observer Pattern** ✅
```python
class Observer(ABC):
    @abstractmethod
    def update(self, event_type: EventType, data: Dict[str, Any]):
        pass

class NotificationObserver(Observer):
    """Observer que armazena notificações para os usuários"""
    
    def __init__(self):
        self._notifications = []
    
    def update(self, event_type: EventType, data: Dict[str, Any]):
        notification = {
            'event_type': event_type.value,
            'data': data,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._notifications.append(notification)

class EventManager:
    """Singleton que gerencia eventos e observers"""
    _instance = None
    
    def notify(self, event_type: EventType, data: Dict[str, Any]):
        """Notifica todos os observers sobre um evento"""
        for observer in self._observers:
            observer.update(event_type, data)
```
**Benefícios:** Desacoplamento entre objetos, sistema de notificações flexível, extensibilidade.

#### **9. Command Pattern** ✅
```python
class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        pass

class CreateTripCommand(Command):
    def __init__(self, receiver, data: Dict[str, Any]):
        self._receiver = receiver
        self._data = data
        self._status = CommandStatus.PENDING
        self._result = None
    
    def execute(self):
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
                self._result = trip.to_dict()
                self._status = CommandStatus.EXECUTED
                return self._result
        except Exception as e:
            self._status = CommandStatus.FAILED
            self._error = str(e)
            return None
    
    def undo(self):
        if self._status == CommandStatus.EXECUTED:
            self._receiver.delete_trip(self._trip_id)
            self._status = CommandStatus.UNDONE
```
**Benefícios:** Encapsulamento de operações, suporte a undo/redo, logging e auditoria, execução em fila.

#### **10. Chain of Responsibility Pattern** ✅
```python
class Handler(ABC):
    def __init__(self, name: str):
        self._name = name
        self._next_handler: Optional['Handler'] = None
    
    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next_handler = handler
        return handler
    
    def handle(self, request: Dict[str, Any], context: Dict[str, Any] = None) -> ProcessingResult:
        result = self._process(request, context)
        result.mark_processed_by(self._name)
        
        if result.success and self._next_handler:
            return self._next_handler.handle(request, context)
        
        return result
    
    @abstractmethod
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        pass

class DataValidationHandler(Handler):
    """Handler que valida dados de entrada"""
    
    def _process(self, request: Dict[str, Any], context: Dict[str, Any]) -> ProcessingResult:
        result = ProcessingResult()
        
        # Validações de dados
        if 'start_date' in request:
            if not self._is_valid_date_format(request['start_date']):
                result.add_error("Formato de data inválido")
        
        return result
```
**Benefícios:** Processamento sequencial flexível, extensibilidade, desacoplamento de handlers.

### **📊 Resumo dos Padrões Implementados**

| Categoria | Padrão | Arquivo | Status |
|-----------|--------|---------|--------|
| **Criacional** | Singleton | `app.py` | ✅ |
| **Criacional** | Factory Method | `app.py` | ✅ |
| **Criacional** | Builder | `app.py` | ✅ |
| **Estrutural** | Facade | `facade.py` | ✅ |
| **Estrutural** | Adapter | `adapters.py` | ✅ |
| **Estrutural** | Decorator | `decorators.py` | ✅ |
| **Comportamental** | Strategy | `strategies.py` | ✅ |
| **Comportamental** | Observer | `observers.py` | ✅ |
| **Comportamental** | Command | `commands.py` | ✅ |
| **Comportamental** | Chain of Responsibility | `chains.py` | ✅ |

**Total:** 10 padrões de design implementados (3 Criacionais, 3 Estruturais, 4 Comportamentais)


