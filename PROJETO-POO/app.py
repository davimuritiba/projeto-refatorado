# --- Importações ---
"""
Arquivo principal da aplicação Travel Itinerary Planner.
Agora organizado de forma modular usando os padrões de design implementados.
"""

import json
import os
import random
import string
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Importações dos módulos separados
from config import create_app, Config
from routes import register_routes
from sample_data import initialize_sample_data
from strategies import RecommendationContext, BudgetContext, StrategyFactory

#Classes 

# Factory Method Pattern Implementation
from abc import ABC, abstractmethod

class ItineraryItemFactory(ABC):
    """Factory abstrata para criação de ItineraryItems"""
    
    @abstractmethod
    def create_item(self, item_id, trip_id, **kwargs):
        """Método abstrato para criar um item do itinerário"""
        pass

class FlightFactory(ItineraryItemFactory):
    """Factory concreta para criação de voos"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Flight(item_id, trip_id, **kwargs)

class HotelFactory(ItineraryItemFactory):
    """Factory concreta para criação de hotéis"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Hotel(item_id, trip_id, **kwargs)

class ActivityFactory(ItineraryItemFactory):
    """Factory concreta para criação de atividades"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Activity(item_id, trip_id, **kwargs)

class ExpenseFactory(ItineraryItemFactory):
    """Factory concreta para criação de despesas"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Expense(item_id, trip_id, **kwargs)

class TravelGuideFactory(ItineraryItemFactory):
    """Factory concreta para criação de guias de viagem"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return TravelGuide(item_id, trip_id, **kwargs)

class TravelResourceFactory(ItineraryItemFactory):
    """Factory concreta para criação de recursos de viagem"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return TravelResource(item_id, trip_id, **kwargs)

class ReviewFactory(ItineraryItemFactory):
    """Factory concreta para criação de avaliações"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Review(item_id, trip_id, **kwargs)

class UserContributionFactory(ItineraryItemFactory):
    """Factory concreta para criação de contribuições de usuário"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return UserContribution(item_id, trip_id, **kwargs)

class UserReactionFactory(ItineraryItemFactory):
    """Factory concreta para criação de reações de usuário"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return UserReaction(item_id, trip_id, **kwargs)

class UserPreferenceFactory(ItineraryItemFactory):
    """Factory concreta para criação de preferências de usuário"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return UserPreference(item_id, trip_id, **kwargs)

class RecommendationFactory(ItineraryItemFactory):
    """Factory concreta para criação de recomendações"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return Recommendation(item_id, trip_id, **kwargs)

class TravelProfileFactory(ItineraryItemFactory):
    """Factory concreta para criação de perfis de viagem"""
    
    def create_item(self, item_id, trip_id, **kwargs):
        return TravelProfile(item_id, trip_id, **kwargs)

# Template Method Pattern Implementation
class ItineraryItemProcessor(ABC):
    """
    Classe abstrata que define o template method para processamento de itens do itinerário.
    Define a estrutura fixa do algoritmo, mas permite que subclasses personalizem passos específicos.
    """
    
    def process_item(self, item_data, trip_id, user_id):
        """
        Template method - define a estrutura fixa do algoritmo de processamento
        """
        print(f"Iniciando processamento de {self.get_item_type()}...")
        
        # Passos fixos do algoritmo
        validated_data = self.validate_item_data(item_data)
        processed_item = self.create_item_object(validated_data, trip_id)
        enriched_item = self.enrich_item_data(processed_item, user_id)
        saved_item = self.save_item(enriched_item)
        
        # Passo final fixo
        self.log_processing_result(saved_item)
        print(f"Processamento de {self.get_item_type()} concluído!")
        
        return saved_item
    
    def validate_item_data(self, item_data):
        """
        Método concreto - validação básica comum a todos os itens
        """
        if not item_data:
            raise ValueError("Dados do item não podem ser vazios")
        
        if not item_data.get('trip_id'):
            raise ValueError("ID da viagem é obrigatório")
        
        # Validação específica do item
        return self.validate_specific_data(item_data)
    
    def create_item_object(self, validated_data, trip_id):
        """
        Método abstrato - deve ser implementado pelas subclasses
        """
        pass
    
    def enrich_item_data(self, item, user_id):
        """
        Método concreto - enriquecimento comum de dados
        """
        item.created_by = user_id
        item.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item.status = "active"
        
        # Enriquecimento específico
        return self.enrich_specific_data(item, user_id)
    
    def save_item(self, item):
        """
        Método concreto - salvamento comum
        """
        # Integração com o DataStore será feita através de injeção de dependência
        print(f"Salvando {self.get_item_type()} no banco de dados...")
        return item
    
    def log_processing_result(self, item):
        """
        Método concreto - logging comum
        """
        print(f"Item {self.get_item_type()} processado com sucesso - ID: {item.id}")
    
    @abstractmethod
    def get_item_type(self):
        """Retorna o tipo do item sendo processado"""
        pass
    
    @abstractmethod
    def validate_specific_data(self, item_data):
        """Validação específica para cada tipo de item"""
        pass
    
    @abstractmethod
    def enrich_specific_data(self, item, user_id):
        """Enriquecimento específico de dados para cada tipo"""
        pass

class FlightProcessor(ItineraryItemProcessor):
    """Processador específico para voos"""
    
    def get_item_type(self):
        return "flight"
    
    def validate_specific_data(self, item_data):
        """Validação específica para voos"""
        required_fields = ['company', 'code', 'departure', 'arrival']
        missing_fields = [field for field in required_fields if not item_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios do voo não preenchidos: {', '.join(missing_fields)}")
        
        # Validação de datas
        if item_data.get('departure') and item_data.get('arrival'):
            if item_data['departure'] > item_data['arrival']:
                raise ValueError("Data de partida não pode ser posterior à data de chegada")
        
        return item_data
    
    def create_item_object(self, validated_data, trip_id):
        """Cria objeto Flight usando o Builder Pattern"""
        return FlightBuilder() \
            .set_trip_id(trip_id) \
            .set_company(validated_data['company']) \
            .set_code(validated_data['code']) \
            .set_departure(validated_data['departure']) \
            .set_arrival(validated_data['arrival']) \
            .set_done(validated_data.get('is_done', False)) \
            .build()
    
    def enrich_specific_data(self, item, user_id):
        """Enriquecimento específico para voos"""
        # Adicionar informações específicas de voo
        item.confirmation_number = f"FL-{item.code}-{datetime.now().strftime('%Y%m%d')}"
        item.seat_preference = "Economy"  # Default
        return item

class HotelProcessor(ItineraryItemProcessor):
    """Processador específico para hotéis"""
    
    def get_item_type(self):
        return "hotel"
    
    def validate_specific_data(self, item_data):
        """Validação específica para hotéis"""
        required_fields = ['name', 'checkin', 'checkout']
        missing_fields = [field for field in required_fields if not item_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios do hotel não preenchidos: {', '.join(missing_fields)}")
        
        # Validação de datas
        if item_data.get('checkin') and item_data.get('checkout'):
            if item_data['checkin'] >= item_data['checkout']:
                raise ValueError("Data de check-in deve ser anterior ao check-out")
        
        return item_data
    
    def create_item_object(self, validated_data, trip_id):
        """Cria objeto Hotel usando o Builder Pattern"""
        return HotelBuilder() \
            .set_trip_id(trip_id) \
            .set_name(validated_data['name']) \
            .set_checkin(validated_data['checkin']) \
            .set_checkout(validated_data['checkout']) \
            .set_done(validated_data.get('is_done', False)) \
            .build()
    
    def enrich_specific_data(self, item, user_id):
        """Enriquecimento específico para hotéis"""
        # Adicionar informações específicas de hotel
        item.confirmation_number = f"HT-{hash(item.name) % 10000}-{datetime.now().strftime('%Y%m%d')}"
        item.room_type = "Standard"  # Default
        item.special_requests = []
        return item

class ActivityProcessor(ItineraryItemProcessor):
    """Processador específico para atividades"""
    
    def get_item_type(self):
        return "activity"
    
    def validate_specific_data(self, item_data):
        """Validação específica para atividades"""
        required_fields = ['description', 'date']
        missing_fields = [field for field in required_fields if not item_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios da atividade não preenchidos: {', '.join(missing_fields)}")
        
        # Validação de data futura para atividades
        if item_data.get('date'):
            activity_date = datetime.strptime(item_data['date'], '%Y-%m-%d')
            if activity_date < datetime.now():
                raise ValueError("Data da atividade não pode ser no passado")
        
        return item_data
    
    def create_item_object(self, validated_data, trip_id):
        """Cria objeto Activity usando o Builder Pattern"""
        return ActivityBuilder() \
            .set_trip_id(trip_id) \
            .set_description(validated_data['description']) \
            .set_date(validated_data['date']) \
            .set_done(validated_data.get('is_done', False)) \
            .build()
    
    def enrich_specific_data(self, item, user_id):
        """Enriquecimento específico para atividades"""
        # Adicionar informações específicas de atividade
        item.duration = "2 horas"  # Default
        item.difficulty_level = "Moderada"  # Default
        item.equipment_needed = []
        item.estimated_cost = 0.0
        return item

class ExpenseProcessor(ItineraryItemProcessor):
    """Processador específico para despesas"""
    
    def get_item_type(self):
        return "expense"
    
    def validate_specific_data(self, item_data):
        """Validação específica para despesas"""
        required_fields = ['description', 'amount', 'currency', 'date', 'category']
        missing_fields = [field for field in required_fields if not item_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios da despesa não preenchidos: {', '.join(missing_fields)}")
        
        # Validação de valor positivo
        if item_data.get('amount') and float(item_data['amount']) <= 0:
            raise ValueError("Valor da despesa deve ser positivo")
        
        return item_data
    
    def create_item_object(self, validated_data, trip_id):
        """Cria objeto Expense"""
        return Expense(
            id=None,  # Será definido pelo DataStore
            trip_id=trip_id,
            description=validated_data['description'],
            amount=float(validated_data['amount']),
            currency=validated_data['currency'],
            date=validated_data['date'],
            category=validated_data['category'],
            is_done=validated_data.get('is_done', False)
        )
    
    def enrich_specific_data(self, item, user_id):
        """Enriquecimento específico para despesas"""
        # Adicionar informações específicas de despesa
        item.exchange_rate = 1.0  # Default (seria calculado baseado na moeda)
        item.payment_method = "Cash"  # Default
        item.receipt_attached = False
        return item

# Builder Pattern Implementation
class TripBuilder:
    """Builder para construção de objetos Trip de forma fluente"""
    
    def __init__(self):
        self._trip_data = {
            'id': None,
            'user_id': None,
            'destination': None,
            'name': None,
            'start_date': None,
            'end_date': None,
            'is_suggestion': False,
            'budget': 0.0,
            'share_code': None,
            'collaborators': []
        }
    
    def set_id(self, trip_id):
        """Define o ID da viagem"""
        self._trip_data['id'] = trip_id
        return self
    
    def set_user_id(self, user_id):
        """Define o ID do usuário"""
        self._trip_data['user_id'] = user_id
        return self
    
    def set_destination(self, destination):
        """Define o destino da viagem"""
        self._trip_data['destination'] = destination
        return self
    
    def set_name(self, name):
        """Define o nome da viagem"""
        self._trip_data['name'] = name
        return self
    
    def set_dates(self, start_date, end_date):
        """Define as datas de início e fim da viagem"""
        self._trip_data['start_date'] = start_date
        self._trip_data['end_date'] = end_date
        return self
    
    def set_budget(self, budget):
        """Define o orçamento da viagem"""
        self._trip_data['budget'] = float(budget)
        return self
    
    def set_share_code(self, share_code):
        """Define o código de compartilhamento"""
        self._trip_data['share_code'] = share_code
        return self
    
    def add_collaborator(self, user_id):
        """Adiciona um colaborador à viagem"""
        if user_id not in self._trip_data['collaborators']:
            self._trip_data['collaborators'].append(user_id)
        return self
    
    def add_collaborators(self, user_ids):
        """Adiciona múltiplos colaboradores"""
        for user_id in user_ids:
            self.add_collaborator(user_id)
        return self
    
    def set_as_suggestion(self, is_suggestion=True):
        """Define se a viagem é uma sugestão"""
        self._trip_data['is_suggestion'] = is_suggestion
        return self
    
    def validate(self):
        """Valida se todos os campos obrigatórios estão preenchidos"""
        required_fields = ['user_id', 'destination', 'name', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if not self._trip_data[field]]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}")
        
        # Validar datas
        if self._trip_data['start_date'] and self._trip_data['end_date']:
            if self._trip_data['start_date'] > self._trip_data['end_date']:
                raise ValueError("Data de início não pode ser posterior à data de fim")
        
        return True
    
    def build(self):
        """Constrói e retorna o objeto Trip"""
        self.validate()
        return Trip(**self._trip_data)

class ItineraryItemBuilder:
    """Builder abstrato para construção de ItineraryItems"""
    
    def __init__(self):
        self._item_data = {
            'id': None,
            'trip_id': None,
            'is_done': False
        }
    
    def set_id(self, item_id):
        """Define o ID do item"""
        self._item_data['id'] = item_id
        return self
    
    def set_trip_id(self, trip_id):
        """Define o ID da viagem"""
        self._item_data['trip_id'] = trip_id
        return self
    
    def set_done(self, is_done=True):
        """Define se o item está concluído"""
        self._item_data['is_done'] = is_done
        return self
    
    def build(self):
        """Método abstrato para construir o item"""
        raise NotImplementedError("Subclasses devem implementar o método build()")

class FlightBuilder(ItineraryItemBuilder):
    """Builder específico para construção de voos"""
    
    def __init__(self):
        super().__init__()
        self._flight_data = {
            'company': None,
            'code': None,
            'departure': None,
            'arrival': None
        }
    
    def set_company(self, company):
        """Define a companhia aérea"""
        self._flight_data['company'] = company
        return self
    
    def set_code(self, code):
        """Define o código do voo"""
        self._flight_data['code'] = code
        return self
    
    def set_departure(self, departure):
        """Define a data/hora de partida"""
        self._flight_data['departure'] = departure
        return self
    
    def set_arrival(self, arrival):
        """Define a data/hora de chegada"""
        self._flight_data['arrival'] = arrival
        return self
    
    def set_flight_details(self, company, code, departure, arrival):
        """Define todos os detalhes do voo de uma vez"""
        self.set_company(company)
        self.set_code(code)
        self.set_departure(departure)
        self.set_arrival(arrival)
        return self
    
    def validate(self):
        """Valida os dados do voo"""
        required_fields = ['company', 'code', 'departure', 'arrival']
        missing_fields = [field for field in required_fields if not self._flight_data[field]]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios do voo não preenchidos: {', '.join(missing_fields)}")
        
        return True
    
    def build(self):
        """Constrói e retorna o objeto Flight"""
        self.validate()
        return Flight(self._item_data['id'], self._item_data['trip_id'], 
                     self._flight_data['company'], self._flight_data['code'],
                     self._flight_data['departure'], self._flight_data['arrival'],
                     self._item_data['is_done'])

class HotelBuilder(ItineraryItemBuilder):
    """Builder específico para construção de hotéis"""
    
    def __init__(self):
        super().__init__()
        self._hotel_data = {
            'name': None,
            'checkin': None,
            'checkout': None
        }
    
    def set_name(self, name):
        """Define o nome do hotel"""
        self._hotel_data['name'] = name
        return self
    
    def set_checkin(self, checkin):
        """Define a data de check-in"""
        self._hotel_data['checkin'] = checkin
        return self
    
    def set_checkout(self, checkout):
        """Define a data de check-out"""
        self._hotel_data['checkout'] = checkout
        return self
    
    def set_stay_dates(self, checkin, checkout):
        """Define as datas de estadia"""
        self.set_checkin(checkin)
        self.set_checkout(checkout)
        return self
    
    def validate(self):
        """Valida os dados do hotel"""
        required_fields = ['name', 'checkin', 'checkout']
        missing_fields = [field for field in required_fields if not self._hotel_data[field]]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios do hotel não preenchidos: {', '.join(missing_fields)}")
        
        return True
    
    def build(self):
        """Constrói e retorna o objeto Hotel"""
        self.validate()
        return Hotel(self._item_data['id'], self._item_data['trip_id'],
                    self._hotel_data['name'], self._hotel_data['checkin'],
                    self._hotel_data['checkout'], self._item_data['is_done'])

class ActivityBuilder(ItineraryItemBuilder):
    """Builder específico para construção de atividades"""
    
    def __init__(self):
        super().__init__()
        self._activity_data = {
            'description': None,
            'date': None
        }
    
    def set_description(self, description):
        """Define a descrição da atividade"""
        self._activity_data['description'] = description
        return self
    
    def set_date(self, date):
        """Define a data da atividade"""
        self._activity_data['date'] = date
        return self
    
    def set_activity_details(self, description, date):
        """Define todos os detalhes da atividade"""
        self.set_description(description)
        self.set_date(date)
        return self
    
    def validate(self):
        """Valida os dados da atividade"""
        required_fields = ['description', 'date']
        missing_fields = [field for field in required_fields if not self._activity_data[field]]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios da atividade não preenchidos: {', '.join(missing_fields)}")
        
        return True
    
    def build(self):
        """Constrói e retorna o objeto Activity"""
        self.validate()
        return Activity(self._item_data['id'], self._item_data['trip_id'],
                       self._activity_data['description'], self._activity_data['date'],
                       self._item_data['is_done'])

class ItineraryItem:
    def __init__(self, id, trip_id, is_done=False):
        self.id = id
        self.trip_id = trip_id
        self.is_done = is_done

    def to_dict(self):
        return self.__dict__

#  classes Flight, Hotel, Activity e Expense HERDAM ItineraryItem.
class Flight(ItineraryItem):
    def __init__(self, id, trip_id, company, code, departure, arrival, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.company = company
        self.code = code
        self.departure = departure
        self.arrival = arrival

class Hotel(ItineraryItem):
    def __init__(self, id, trip_id, name, checkin, checkout, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.name = name
        self.checkin = checkin
        self.checkout = checkout

class Activity(ItineraryItem):
    def __init__(self, id, trip_id, description, date, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.description = description
        self.date = date
        
class Expense(ItineraryItem):
    def __init__(self, id, trip_id, description, amount, currency, date, category, is_done=False):
        # A despesa também herda, mas o 'is_done' não é tão relevante aqui,
        super().__init__(id, trip_id, is_done)
        self.description = description
        self.amount = amount
        self.currency = currency
        self.date = date
        self.category = category

class TravelGuide(ItineraryItem):
    def __init__(self, id, trip_id, destination, title, content, category, tags=None, author="Sistema", created_date=None, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.destination = destination
        self.title = title
        self.content = content
        self.category = category
        self.tags = tags if tags else []
        self.author = author
        self.created_date = created_date or datetime.now().strftime("%Y-%m-%d")

class TravelResource(ItineraryItem):
    def __init__(self, id, trip_id, destination, title, resource_type, url=None, description="", contact_info=None, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.destination = destination
        self.title = title
        self.resource_type = resource_type
        self.url = url
        self.description = description
        self.contact_info = contact_info or {}

class Review(ItineraryItem):
    def __init__(self, id, trip_id, user_id, item_type, item_id, rating, comment="", date=None, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.item_type = item_type
        self.item_id = item_id
        self.rating = rating
        self.comment = comment
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.likes = 0
        self.dislikes = 0

class UserContribution(ItineraryItem):
    def __init__(self, id, trip_id, user_id, contribution_type, title, content, status="pending", date=None, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.contribution_type = contribution_type
        self.title = title
        self.content = content
        self.status = status
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.likes = 0
        self.views = 0

class UserReaction(ItineraryItem):
    def __init__(self, id, trip_id, user_id, target_type, target_id, reaction_type, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.target_type = target_type
        self.target_id = target_id
        self.reaction_type = reaction_type

class UserPreference(ItineraryItem):
    def __init__(self, id, trip_id, user_id, preference_type, value, weight=5, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.preference_type = preference_type
        self.value = value
        self.weight = weight
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Recommendation(ItineraryItem):
    def __init__(self, id, trip_id, user_id, recommendation_type, target_id, score, reason, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.recommendation_type = recommendation_type
        self.target_id = target_id
        self.score = score
        self.reason = reason
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.is_viewed = False
        self.is_accepted = False

class TravelProfile(ItineraryItem):
    def __init__(self, id, trip_id, user_id, profile_name, travel_style, budget_range, interests, climate_preference, accommodation_style, transport_preference, is_done=False):
        super().__init__(id, trip_id, is_done)
        self.user_id = user_id
        self.profile_name = profile_name
        self.travel_style = travel_style
        self.budget_range = budget_range
        self.interests = interests
        self.climate_preference = climate_preference
        self.accommodation_style = accommodation_style
        self.transport_preference = transport_preference
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.is_active = True


class User:
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password #seria diferente ao migrar para um banco de dados

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}

class Trip:
    def __init__(self, id, user_id, destination, name, start_date, end_date, is_suggestion=False, budget=0.0, share_code=None, collaborators=None):
        self.id = id
        self.user_id = user_id
        self.destination = destination
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.is_suggestion = is_suggestion
        self.budget = budget
        self.share_code = share_code
        self.collaborators = collaborators if collaborators is not None else []

    def to_dict(self):
        return self.__dict__


# Singleton Pattern Implementation
class DataStore:
    """
    Classe DataStore implementando o padrão Singleton
    Garante que apenas uma instância da classe exista em toda a aplicação
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls, filename='database.json'):
        """
        Método __new__ implementando o Singleton Pattern
        Thread-safe usando locks para ambientes multi-threaded
        """
        if cls._instance is None:
            with cls._lock:
                # Verificação dupla para garantir thread-safety
                if cls._instance is None:
                    cls._instance = super(DataStore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, filename='database.json'):
        """
        Inicialização que só ocorre uma vez, mesmo com múltiplas chamadas
        """
        # Evita reinicialização se já foi inicializado
        if DataStore._initialized:
            return
            
        self._filename = filename
        self._data = self._load_data()
        
        # Factory Method Pattern - Mapeamento de tipos para factories
        self._factories = {
            'flight': FlightFactory(),
            'hotel': HotelFactory(),
            'activity': ActivityFactory(),
            'expense': ExpenseFactory(),
            'travel_guide': TravelGuideFactory(),
            'travel_resource': TravelResourceFactory(),
            'review': ReviewFactory(),
            'user_contribution': UserContributionFactory(),
            'user_reaction': UserReactionFactory(),
            'user_preference': UserPreferenceFactory(),
            'recommendation': RecommendationFactory(),
            'travel_profile': TravelProfileFactory()
        }
        
        # Builder Pattern - Mapeamento de tipos para builders
        self._builders = {
            'flight': FlightBuilder,
            'hotel': HotelBuilder,
            'activity': ActivityBuilder
        }
        
        # Template Method Pattern - Mapeamento de tipos para processadores
        self._processors = {
            'flight': FlightProcessor(),
            'hotel': HotelProcessor(),
            'activity': ActivityProcessor(),
            'expense': ExpenseProcessor()
        }
        
        # Strategy Pattern - Contexts para gerenciar estratégias
        self._recommendation_context = RecommendationContext()
        self._budget_context = BudgetContext()
        
        # Marca como inicializado
        DataStore._initialized = True
    
    @classmethod
    def get_instance(cls, filename='database.json'):
        """
        Método de classe para obter a instância única do Singleton
        Interface preferida para acessar o DataStore
        """
        if cls._instance is None:
            cls._instance = cls(filename)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Método para resetar a instância (útil para testes)
        ATENÇÃO: Use apenas em testes ou reinicialização da aplicação
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False

    def _load_data(self):
        if not os.path.exists(self._filename):
            default_data = { 
                "users": [], "trips": [], "flights": [], "hotels": [], "activities": [], "expenses": [],
                "travel_guides": [], "travel_resources": [], "reviews": [], "user_contributions": [], "user_reactions": [],
                "user_preferences": [], "recommendations": [], "travel_profiles": []
            }
            with open(self._filename, 'w') as f: json.dump(default_data, f, indent=4)
            return default_data
        
        with open(self._filename, 'r') as f:
            try:
                data = json.load(f)
                for key in ["users", "trips", "flights", "hotels", "activities", "expenses", "travel_guides", "travel_resources", "reviews", "user_contributions", "user_reactions", "user_preferences", "recommendations", "travel_profiles"]: 
                    data.setdefault(key, [])
                return data
            except (json.JSONDecodeError, TypeError): 
                return {
                    "users": [], "trips": [], "flights": [], "hotels": [], "activities": [], "expenses": [],
                    "travel_guides": [], "travel_resources": [], "reviews": [], "user_contributions": [], "user_reactions": [],
                    "user_preferences": [], "recommendations": [], "travel_profiles": []
                }

    def _save_data(self):
        with open(self._filename, 'w') as f: json.dump(self._data, f, indent=4)

    def _get_next_id(self, collection_name):
        collection = self._data.get(collection_name, [])
        if not collection: return 1
        return max(item.get('id', 0) for item in collection) + 1
    
    def _generate_share_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def create_itinerary_item(self, item_type, item_id, trip_id, **kwargs):
        """
        Factory Method para criar itens do itinerário
        Usa o padrão Factory Method para encapsular a criação de objetos
        """
        if item_type not in self._factories:
            raise ValueError(f"Tipo de item não suportado: {item_type}")
        
        factory = self._factories[item_type]
        return factory.create_item(item_id, trip_id, **kwargs)
    
    def get_builder(self, item_type):
        """
        Builder Method para obter um builder específico
        Usa o padrão Builder para construção fluente de objetos
        """
        if item_type not in self._builders:
            raise ValueError(f"Builder não disponível para tipo: {item_type}")
        
        return self._builders[item_type]()
    
    def create_trip_with_builder(self, user_id, destination, name, start_date, end_date, **kwargs):
        """
        Método helper para criar uma viagem usando o Builder Pattern
        """
        trip_builder = TripBuilder() \
            .set_user_id(user_id) \
            .set_destination(destination) \
            .set_name(name) \
            .set_dates(start_date, end_date)
        
        # Aplicar configurações opcionais
        if 'budget' in kwargs:
            trip_builder.set_budget(kwargs['budget'])
        if 'share_code' in kwargs:
            trip_builder.set_share_code(kwargs['share_code'])
        if 'collaborators' in kwargs:
            trip_builder.add_collaborators(kwargs['collaborators'])
        if 'is_suggestion' in kwargs:
            trip_builder.set_as_suggestion(kwargs['is_suggestion'])
        
        return trip_builder.build()
    
    def process_item_with_template(self, item_type, item_data, trip_id, user_id):
        """
        Template Method Pattern - Processa um item usando o algoritmo definido
        """
        if item_type not in self._processors:
            raise ValueError(f"Processador não disponível para tipo: {item_type}")
        
        processor = self._processors[item_type]
        
        # Adicionar trip_id aos dados se não estiver presente
        if 'trip_id' not in item_data:
            item_data['trip_id'] = trip_id
        
        # Processar o item usando o template method
        processed_item = processor.process_item(item_data, trip_id, user_id)
        
        # Salvar no banco de dados
        collection_name = f"{item_type}s" if item_type != 'expense' else 'expenses'
        processed_item.id = self._get_next_id(collection_name)
        
        # Converter para dict e salvar
        item_dict = processed_item.to_dict()
        self._data[collection_name].append(item_dict)
        self._save_data()
        
        return processed_item
    
    def get_processor(self, item_type):
        """
        Retorna o processador para um tipo específico de item
        """
        if item_type not in self._processors:
            raise ValueError(f"Processador não disponível para tipo: {item_type}")
        
        return self._processors[item_type]
    
    # === Métodos usando Strategy Pattern ===
    
    def set_recommendation_strategy(self, strategy_type):
        """
        Define a estratégia de recomendação a ser usada
        """
        self._recommendation_context.set_strategy(strategy_type)
    
    def set_budget_strategy(self, strategy_type):
        """
        Define a estratégia de cálculo de orçamento a ser usada
        """
        self._budget_context.set_strategy(strategy_type)
    
    def get_recommendation_with_strategy(self, user_id, target_item, strategy_type="hybrid", context=None):
        """
        Obtém recomendação usando uma estratégia específica
        """
        user_preferences = self.get_user_preferences(user_id)
        user_profile = self.get_active_travel_profile(user_id)
        
        # Usar estratégia específica
        strategy = StrategyFactory.create_recommendation_strategy(strategy_type)
        score = strategy.calculate_score(user_preferences, user_profile, target_item, context)
        
        return {
            'score': score,
            'strategy_used': strategy.get_strategy_name(),
            'target_item': target_item,
            'user_id': user_id
        }
    
    def calculate_budget_with_strategy(self, trip_data, user_id, strategy_type="flexible"):
        """
        Calcula orçamento usando uma estratégia específica
        """
        user_preferences = self.get_user_preferences(user_id)
        user_profile = self.get_active_travel_profile(user_id)
        
        # Usar estratégia específica
        strategy = StrategyFactory.create_budget_strategy(strategy_type)
        budget = strategy.calculate_budget(trip_data, user_preferences, user_profile)
        
        return {
            'estimated_budget': budget,
            'strategy_used': strategy.get_strategy_name(),
            'trip_data': trip_data,
            'user_id': user_id
        }
    
    def get_available_recommendation_strategies(self):
        """
        Retorna as estratégias de recomendação disponíveis
        """
        return self._recommendation_context.get_available_strategies()
    
    def get_available_budget_strategies(self):
        """
        Retorna as estratégias de orçamento disponíveis
        """
        return self._budget_context.get_available_strategies()
    
    def generate_smart_recommendations(self, user_id, recommendation_type="destination", strategy_type="hybrid"):
        """
        Gera recomendações inteligentes usando Strategy Pattern
        """
        user_preferences = self.get_user_preferences(user_id)
        user_profile = self.get_active_travel_profile(user_id)
        
        if not user_preferences and not user_profile:
            return []
        
        recommendations = []
        
        if recommendation_type == "destination":
            destinations = [
                {"destination": "Madrid", "cost_level": "medium", "category": "cultural"},
                {"destination": "Recife", "cost_level": "low", "category": "cultural"},
                {"destination": "Paris", "cost_level": "high", "category": "cultural"},
                {"destination": "Tokyo", "cost_level": "high", "category": "cultural"},
                {"destination": "New York", "cost_level": "high", "category": "cultural"},
                {"destination": "Barcelona", "cost_level": "medium", "category": "cultural"},
                {"destination": "Rio de Janeiro", "cost_level": "medium", "category": "nature"},
                {"destination": "Bangkok", "cost_level": "low", "category": "cultural"},
                {"destination": "Reykjavik", "cost_level": "high", "category": "nature"},
                {"destination": "Prague", "cost_level": "low", "category": "cultural"}
            ]
            
            for dest_data in destinations:
                score = self.get_recommendation_with_strategy(
                    user_id, dest_data['destination'], strategy_type, dest_data
                )
                
                if score['score'] > 40:  # Threshold mínimo
                    reason = self._generate_strategy_reason(score, dest_data, user_preferences, user_profile)
                    rec = self.add_recommendation(
                        0, user_id, "destination", dest_data['destination'], 
                        score['score'], reason
                    )
                    recommendations.append({
                        'recommendation': rec,
                        'strategy_info': score
                    })
        
        elif recommendation_type == "activity":
            activities = self.get_all_travel_guides()
            for activity in activities:
                if activity.trip_id == 0:
                    context = {
                        'destination': activity.destination,
                        'category': activity.category
                    }
                    score = self.get_recommendation_with_strategy(
                        user_id, activity.id, strategy_type, context
                    )
                    
                    if score['score'] > 40:
                        reason = f"Baseado na estratégia {strategy_type} e seu interesse em {activity.category}"
                        rec = self.add_recommendation(
                            0, user_id, "activity", activity.id, score['score'], reason
                        )
                        recommendations.append({
                            'recommendation': rec,
                            'strategy_info': score
                        })
        
        return recommendations
    
    def _generate_strategy_reason(self, score_data, dest_data, user_preferences, user_profile):
        """
        Gera explicação da recomendação baseada na estratégia usada
        """
        strategy_name = score_data['strategy_used']
        reasons = []
        
        if strategy_name == "Climate-Based":
            climate_pref = next((p for p in user_preferences if p.preference_type == "climate"), None)
            if climate_pref:
                reasons.append(f"clima {climate_pref.value}")
        
        elif strategy_name == "Budget-Based":
            budget_pref = next((p for p in user_preferences if p.preference_type == "budget"), None)
            if budget_pref:
                reasons.append(f"orçamento {budget_pref.value}")
        
        elif strategy_name == "Interest-Based":
            interest_pref = next((p for p in user_preferences if p.preference_type == "interests"), None)
            if interest_pref:
                reasons.append(f"interesse em {interest_pref.value}")
        
        elif strategy_name == "Hybrid":
            reasons.append("combinação de múltiplos fatores pessoais")
        
        if not reasons:
            reasons.append("baseado no seu perfil")
        
        return f"Recomendado por: {', '.join(reasons)} (Estratégia: {strategy_name})"

    def add_user(self, name, email, password):
        user = User(self._get_next_id('users'), name, email, password)
        self._data['users'].append(user.__dict__)
        self._save_data()
        return user
    
    def find_user_by_email(self, email):
        user_data = next((u for u in self._data['users'] if u.get('email') == email), None)
        return User(**user_data) if user_data else None
    
    def find_user_by_id(self, user_id):
        user_data = next((u for u in self._data['users'] if u.get('id') == user_id), None)
        return User(**user_data) if user_data else None

    def add_trip(self, user_id, dest, name, start, end, share_code):
        if share_code and self.find_trip_by_share_code(share_code):
            return None 

        if not share_code:
            share_code = self._generate_share_code()
            while self.find_trip_by_share_code(share_code):
                share_code = self._generate_share_code()

        trip = Trip(self._get_next_id('trips'), user_id, dest, name, start, end, share_code=share_code, collaborators=[])
        self._data['trips'].append(trip.to_dict())
        self._save_data()
        return trip

    def find_trip_by_share_code(self, code):
        trip_data = next((t for t in self._data['trips'] if t.get('share_code') == code), None)
        return Trip(**trip_data) if trip_data else None

    def add_collaborator_to_trip(self, trip_id, user_id):
        for trip in self._data['trips']:
            if trip.get('id') == trip_id:
                if 'collaborators' not in trip or trip['collaborators'] is None:
                    trip['collaborators'] = []
                if user_id not in trip['collaborators'] and trip.get('user_id') != user_id:
                    trip['collaborators'].append(user_id)
                    self._save_data()
                return Trip(**trip)
        return None

    def get_user_trips(self, user_id):
        user_trips = []
        for t_data in self._data.get('trips', []):
            is_owner = t_data.get('user_id') == user_id
            is_collaborator = user_id in t_data.get('collaborators', [])
            if (is_owner or is_collaborator) and not t_data.get('is_suggestion', False):
                user_trips.append(Trip(**t_data))
        return user_trips

    def find_trip_by_id(self, trip_id):
        trip_data = next((t for t in self._data['trips'] if t.get('id') == trip_id), None)
        return Trip(**trip_data) if trip_data else None
    def get_suggestion_trips(self):
        return [Trip(**t_data) for t_data in self._data.get('trips', []) if t_data.get('is_suggestion', False)]
    def update_trip_budget(self, trip_id, budget):
        for trip in self._data['trips']:
            if trip.get('id') == trip_id:
                trip['budget'] = budget
                self._save_data()
                return Trip(**trip)
        return None
    def _update_item_status(self, collection_name, item_id, is_done):
        for item in self._data.get(collection_name, []):
            if item.get('id') == item_id:
                item['is_done'] = is_done
                self._save_data()
                return item
        return None

    def _add_item(self, collection_name, item_type, trip_id, **kwargs):
        """
        Método refatorado para usar Factory Method Pattern
        Agora usa o factory para criar itens em vez de instanciar classes diretamente
        """
        item_id = self._get_next_id(collection_name)
        item = self.create_itinerary_item(item_type, item_id, trip_id, **kwargs)
        self._data[collection_name].append(item.to_dict())
        self._save_data()
        return item
    
    def add_flight(self, trip_id, **kwargs): return self._add_item('flights', 'flight', trip_id, **kwargs)
    def add_hotel(self, trip_id, **kwargs): return self._add_item('hotels', 'hotel', trip_id, **kwargs)
    def add_activity(self, trip_id, **kwargs): return self._add_item('activities', 'activity', trip_id, **kwargs)
    def add_expense(self, trip_id, **kwargs): return self._add_item('expenses', 'expense', trip_id, **kwargs)
    
    # Métodos que usam Builder Pattern para criação mais flexível
    def add_flight_with_builder(self, trip_id, company, code, departure, arrival, is_done=False):
        """Adiciona um voo usando o Builder Pattern"""
        flight = self.get_builder('flight') \
            .set_trip_id(trip_id) \
            .set_company(company) \
            .set_code(code) \
            .set_departure(departure) \
            .set_arrival(arrival) \
            .set_done(is_done) \
            .build()
        
        flight.id = self._get_next_id('flights')
        self._data['flights'].append(flight.to_dict())
        self._save_data()
        return flight
    
    def add_hotel_with_builder(self, trip_id, name, checkin, checkout, is_done=False):
        """Adiciona um hotel usando o Builder Pattern"""
        hotel = self.get_builder('hotel') \
            .set_trip_id(trip_id) \
            .set_name(name) \
            .set_checkin(checkin) \
            .set_checkout(checkout) \
            .set_done(is_done) \
            .build()
        
        hotel.id = self._get_next_id('hotels')
        self._data['hotels'].append(hotel.to_dict())
        self._save_data()
        return hotel
    
    def add_activity_with_builder(self, trip_id, description, date, is_done=False):
        """Adiciona uma atividade usando o Builder Pattern"""
        activity = self.get_builder('activity') \
            .set_trip_id(trip_id) \
            .set_description(description) \
            .set_date(date) \
            .set_done(is_done) \
            .build()
        
        activity.id = self._get_next_id('activities')
        self._data['activities'].append(activity.to_dict())
        self._save_data()
        return activity

    def get_expenses_for_trip(self, trip_id):
        return [Expense(**e) for e in self._data.get('expenses', []) if e.get('trip_id') == trip_id]
    def remove_expense(self, expense_id):
        initial_len = len(self._data['expenses'])
        self._data['expenses'] = [e for e in self._data['expenses'] if e.get('id') != expense_id]
        if len(self._data['expenses']) < initial_len:
            self._save_data()
            return True
        return False
    def get_details_for_trip(self, trip_id):
        return {
            "flights": [f for f in self._data.get('flights', []) if f.get('trip_id') == trip_id],
            "hotels": [h for h in self._data.get('hotels', []) if h.get('trip_id') == trip_id],
            "activities": [a for a in self._data.get('activities', []) if a.get('trip_id') == trip_id]
        }
    
    def add_travel_guide(self, trip_id, destination, title, content, category, tags=None, author="Sistema"):
        guide = self.create_itinerary_item('travel_guide', self._get_next_id('travel_guides'), trip_id, 
                                         destination=destination, title=title, content=content, 
                                         category=category, tags=tags, author=author)
        self._data['travel_guides'].append(guide.to_dict())
        self._save_data()
        return guide
    
    def get_travel_guides_by_destination(self, destination):
        return [TravelGuide(**g) for g in self._data.get('travel_guides', []) if g.get('destination', '').lower() == destination.lower()]
    
    def get_travel_guides_by_category(self, category):
        return [TravelGuide(**g) for g in self._data.get('travel_guides', []) if g.get('category') == category]
    
    def get_all_travel_guides(self):
        guides = []
        for g in self._data.get('travel_guides', []):
            guide_data = {k: v for k, v in g.items() if k in ['id', 'trip_id', 'destination', 'title', 'content', 'category', 'tags', 'author', 'created_date', 'is_done']}
            guides.append(TravelGuide(**guide_data))
        return guides
    
    def add_travel_resource(self, trip_id, destination, title, resource_type, url=None, description="", contact_info=None):
        resource = self.create_itinerary_item('travel_resource', self._get_next_id('travel_resources'), trip_id,
                                            destination=destination, title=title, resource_type=resource_type,
                                            url=url, description=description, contact_info=contact_info)
        self._data['travel_resources'].append(resource.to_dict())
        self._save_data()
        return resource
    
    def get_travel_resources_by_destination(self, destination):
        return [TravelResource(**r) for r in self._data.get('travel_resources', []) if r.get('destination', '').lower() == destination.lower()]
    
    def get_travel_resources_by_type(self, resource_type):
        return [TravelResource(**r) for r in self._data.get('travel_resources', []) if r.get('resource_type') == resource_type]
    
    def get_all_travel_resources(self):
        return [TravelResource(**r) for r in self._data.get('travel_resources', [])]
    
    def add_review(self, trip_id, user_id, item_type, item_id, rating, comment=""):
        review = self.create_itinerary_item('review', self._get_next_id('reviews'), trip_id,
                                          user_id=user_id, item_type=item_type, item_id=item_id,
                                          rating=rating, comment=comment)
        self._data['reviews'].append(review.to_dict())
        self._save_data()
        return review
    
    def get_reviews_by_item(self, item_type, item_id):
        return [Review(**r) for r in self._data.get('reviews', []) if r.get('item_type') == item_type and r.get('item_id') == item_id]
    
    def get_reviews_by_user(self, user_id):
        return [Review(**r) for r in self._data.get('reviews', []) if r.get('user_id') == user_id]
    
    def get_all_reviews(self):
        return [Review(**r) for r in self._data.get('reviews', [])]
    
    def get_average_rating(self, item_type, item_id):
        reviews = self.get_reviews_by_item(item_type, item_id)
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    def add_user_contribution(self, trip_id, user_id, contribution_type, title, content):
        contribution = self.create_itinerary_item('user_contribution', self._get_next_id('user_contributions'), trip_id,
                                                user_id=user_id, contribution_type=contribution_type,
                                                title=title, content=content)
        self._data['user_contributions'].append(contribution.to_dict())
        self._save_data()
        return contribution
    
    def get_contributions_by_type(self, contribution_type):
        return [UserContribution(**c) for c in self._data.get('user_contributions', []) if c.get('contribution_type') == contribution_type and c.get('status') == 'approved']
    
    def get_contributions_by_user(self, user_id):
        return [UserContribution(**c) for c in self._data.get('user_contributions', []) if c.get('user_id') == user_id]
    
    def get_pending_contributions(self):
        return [UserContribution(**c) for c in self._data.get('user_contributions', []) if c.get('status') == 'pending']
    
    def approve_contribution(self, contribution_id):
        for contribution in self._data.get('user_contributions', []):
            if contribution.get('id') == contribution_id:
                contribution['status'] = 'approved'
                self._save_data()
                return UserContribution(**contribution)
        return None
    
    def reject_contribution(self, contribution_id):
        for contribution in self._data.get('user_contributions', []):
            if contribution.get('id') == contribution_id:
                contribution['status'] = 'rejected'
                self._save_data()
                return UserContribution(**contribution)
        return None
    
    def add_user_reaction(self, trip_id, user_id, target_type, target_id, reaction_type):
        existing_reaction = next((r for r in self._data.get('user_reactions', []) 
                                if r.get('user_id') == user_id and r.get('target_type') == target_type 
                                and r.get('target_id') == target_id), None)
        
        if existing_reaction:
            existing_reaction['reaction_type'] = reaction_type
            self._save_data()
            return UserReaction(**existing_reaction)
        else:
            reaction = self.create_itinerary_item('user_reaction', self._get_next_id('user_reactions'), trip_id,
                                                user_id=user_id, target_type=target_type, target_id=target_id,
                                                reaction_type=reaction_type)
            self._data['user_reactions'].append(reaction.to_dict())
            self._save_data()
            return reaction
    
    def get_reactions_count(self, target_type, target_id):
        reactions = [r for r in self._data.get('user_reactions', []) 
                    if r.get('target_type') == target_type and r.get('target_id') == target_id]
        likes = len([r for r in reactions if r.get('reaction_type') == 'like'])
        dislikes = len([r for r in reactions if r.get('reaction_type') == 'dislike'])
        return likes, dislikes
    
    def remove_user_reaction(self, user_id, target_type, target_id):
        initial_len = len(self._data['user_reactions'])
        self._data['user_reactions'] = [r for r in self._data['user_reactions'] 
                                      if not (r.get('user_id') == user_id and r.get('target_type') == target_type 
                                             and r.get('target_id') == target_id)]
        if len(self._data['user_reactions']) < initial_len:
            self._save_data()
            return True
        return False
    
    def add_user_preference(self, trip_id, user_id, preference_type, value, weight=5):
        preference = self.create_itinerary_item('user_preference', self._get_next_id('user_preferences'), trip_id,
                                              user_id=user_id, preference_type=preference_type, value=value, weight=weight)
        self._data['user_preferences'].append(preference.to_dict())
        self._save_data()
        return preference
    
    def get_user_preferences(self, user_id):
        preferences = []
        for p in self._data.get('user_preferences', []):
            if p.get('user_id') == user_id:
                # Remover campos extras que não estão no construtor
                pref_data = {k: v for k, v in p.items() if k in ['id', 'trip_id', 'user_id', 'preference_type', 'value', 'weight', 'is_done']}
                preferences.append(UserPreference(**pref_data))
        return preferences
    
    def update_user_preference(self, user_id, preference_type, value, weight=5):
        for pref in self._data.get('user_preferences', []):
            if pref.get('user_id') == user_id and pref.get('preference_type') == preference_type:
                pref['value'] = value
                pref['weight'] = weight
                pref['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data()
                return UserPreference(**pref)
        
        return self.add_user_preference(0, user_id, preference_type, value, weight)
    
    def add_travel_profile(self, trip_id, user_id, profile_name, travel_style, budget_range, interests, climate_preference, accommodation_style, transport_preference):
        profile = self.create_itinerary_item('travel_profile', self._get_next_id('travel_profiles'), trip_id,
                                           user_id=user_id, profile_name=profile_name, travel_style=travel_style,
                                           budget_range=budget_range, interests=interests, climate_preference=climate_preference,
                                           accommodation_style=accommodation_style, transport_preference=transport_preference)
        self._data['travel_profiles'].append(profile.to_dict())
        self._save_data()
        return profile
    
    def get_user_travel_profiles(self, user_id):
        profiles = []
        for p in self._data.get('travel_profiles', []):
            if p.get('user_id') == user_id and p.get('is_active', True):
                profile_data = {k: v for k, v in p.items() if k in ['id', 'trip_id', 'user_id', 'profile_name', 'travel_style', 'budget_range', 'interests', 'climate_preference', 'accommodation_style', 'transport_preference', 'created_date', 'is_active', 'is_done']}
                profiles.append(TravelProfile(**profile_data))
        return profiles
    
    def get_active_travel_profile(self, user_id):
        profiles = self.get_user_travel_profiles(user_id)
        return profiles[0] if profiles else None
    
    def add_recommendation(self, trip_id, user_id, recommendation_type, target_id, score, reason):
        recommendation = self.create_itinerary_item('recommendation', self._get_next_id('recommendations'), trip_id,
                                                 user_id=user_id, recommendation_type=recommendation_type,
                                                 target_id=target_id, score=score, reason=reason)
        self._data['recommendations'].append(recommendation.to_dict())
        self._save_data()
        return recommendation
    
    def get_user_recommendations(self, user_id, limit=10):
        recommendations = [Recommendation(**r) for r in self._data.get('recommendations', []) if r.get('user_id') == user_id]
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]
    
    def mark_recommendation_viewed(self, recommendation_id):
        for rec in self._data.get('recommendations', []):
            if rec.get('id') == recommendation_id:
                rec['is_viewed'] = True
                self._save_data()
                return Recommendation(**rec)
        return None
    
    def mark_recommendation_accepted(self, recommendation_id):
        for rec in self._data.get('recommendations', []):
            if rec.get('id') == recommendation_id:
                rec['is_accepted'] = True
                self._save_data()
                return Recommendation(**rec)
        return None
    
    def generate_personalized_recommendations(self, user_id, recommendation_type="destination"):
        user_preferences = self.get_user_preferences(user_id)
        user_profile = self.get_active_travel_profile(user_id)
        
        if not user_preferences and not user_profile:
            return []
        
        recommendations = []
        
        if recommendation_type == "destination":
            destinations = ["Madrid", "Recife", "Paris", "Tokyo", "New York", "Barcelona", "Rio de Janeiro"]
            
            for dest in destinations:
                score = self._calculate_destination_score(dest, user_preferences, user_profile)
                if score > 30:
                    existing_rec = next((r for r in self._data.get('recommendations', []) 
                                       if r.get('user_id') == user_id and r.get('target_id') == dest), None)
                    if not existing_rec:
                        reason = self._generate_recommendation_reason(dest, score, user_preferences, user_profile)
                        rec = self.add_recommendation(0, user_id, "destination", dest, score, reason)
                        recommendations.append(rec)
        
        elif recommendation_type == "activity":
            activities = self.get_all_travel_guides()
            for activity in activities:
                if activity.trip_id == 0:
                    score = self._calculate_activity_score(activity, user_preferences, user_profile)
                    if score > 30:
                        reason = f"Baseado no seu interesse em {activity.category}"
                        rec = self.add_recommendation(0, user_id, "activity", activity.id, score, reason)
                        recommendations.append(rec)
        
        return recommendations
    
    def _calculate_destination_score(self, destination, user_preferences, user_profile):
        score = 50
        
        for pref in user_preferences:
            if pref.preference_type == "climate":
                if destination in ["Madrid", "Barcelona"] and pref.value == "temperate":
                    score += 20
                elif destination in ["Recife", "Rio de Janeiro"] and pref.value == "tropical":
                    score += 20
            
            elif pref.preference_type == "interests":
                if pref.value == "cultural" and destination in ["Madrid", "Paris", "Barcelona"]:
                    score += 15
                elif pref.value == "nature" and destination in ["Rio de Janeiro", "Tokyo"]:
                    score += 15
        
        if user_profile:
            if user_profile.budget_range == "low" and destination in ["Recife", "Barcelona"]:
                score += 10
            elif user_profile.budget_range == "high" and destination in ["Paris", "Tokyo", "New York"]:
                score += 10
            
            if user_profile.travel_style == "cultural" and destination in ["Madrid", "Paris", "Barcelona"]:
                score += 15
        
        return min(score, 100)
    
    def _calculate_activity_score(self, activity, user_preferences, user_profile):
        score = 50
        
        for pref in user_preferences:
            if pref.preference_type == "interests":
                if pref.value in activity.tags:
                    score += 20
        
        if user_profile:
            if activity.category in user_profile.interests:
                score += 25
        
        return min(score, 100)
    
    def _generate_recommendation_reason(self, destination, score, user_preferences, user_profile):
        reasons = []
        
        if user_profile:
            if user_profile.travel_style == "cultural":
                reasons.append("destino cultural")
            if user_profile.budget_range == "low":
                reasons.append("orçamento acessível")
        
        for pref in user_preferences:
            if pref.preference_type == "climate" and pref.value == "tropical" and destination in ["Recife", "Rio de Janeiro"]:
                reasons.append("clima tropical")
            elif pref.preference_type == "interests" and pref.value == "cultural" and destination in ["Madrid", "Paris"]:
                reasons.append("rico em cultura")
        
        if not reasons:
            reasons.append("popular entre viajantes")
        
        return f"Recomendado por: {', '.join(reasons)}"


#  Configuração da Aplicação Flask ---
# Usando Singleton Pattern para garantir uma única instância do DataStore
# Isso garante que todos os módulos da aplicação compartilhem os mesmos dados
# e evita problemas de sincronização entre diferentes instâncias
db = DataStore.get_instance()


#  Rotas da API ---
# As rotas foram movidas para o módulo routes.py para melhor organização


# Dados de exemplo foram movidos para o módulo sample_data.py

#  Execução da Aplicação 
def create_application():
    """
    Função principal para criar e configurar a aplicação
    Segue o padrão Application Factory
    """
    # Criar aplicação Flask usando configuração modular
    app = create_app()
    
    # Registrar todas as rotas da API
    register_routes(app, db)
    
    # Inicializar dados de exemplo
    initialize_sample_data(db)
    
    return app

# Execução principal
if __name__ == '__main__':
    app = create_application()
    app.run(debug=True)

