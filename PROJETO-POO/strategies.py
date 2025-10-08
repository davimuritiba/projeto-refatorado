# --- Strategy Pattern Implementation ---
"""
Implementação do padrão Strategy para algoritmos de recomendação, 
cálculo de orçamento e validação de dados no Travel Itinerary Planner.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

# === Strategy para Algoritmos de Recomendação ===

class RecommendationStrategy(ABC):
    """Interface Strategy para algoritmos de recomendação"""
    
    @abstractmethod
    def calculate_score(self, user_preferences, user_profile, target_item, context=None):
        """Calcula score de recomendação para um item"""
        pass
    
    @abstractmethod
    def get_strategy_name(self):
        """Retorna o nome da estratégia"""
        pass

class ClimateBasedRecommendation(RecommendationStrategy):
    """Estratégia de recomendação baseada em preferências climáticas"""
    
    def calculate_score(self, user_preferences, user_profile, target_item, context=None):
        score = 30  # Score base
        
        # Verificar preferências climáticas
        climate_pref = next((p for p in user_preferences if p.preference_type == "climate"), None)
        if climate_pref:
            destination = context.get('destination', '') if context else ''
            
            if climate_pref.value == "temperate" and destination in ["Madrid", "Paris", "Barcelona", "London"]:
                score += 40
            elif climate_pref.value == "tropical" and destination in ["Recife", "Rio de Janeiro", "Cancun", "Bangkok"]:
                score += 40
            elif climate_pref.value == "cold" and destination in ["Reykjavik", "Stockholm", "Oslo"]:
                score += 40
        
        return min(score, 100)
    
    def get_strategy_name(self):
        return "Climate-Based"

class BudgetBasedRecommendation(RecommendationStrategy):
    """Estratégia de recomendação baseada em orçamento"""
    
    def calculate_score(self, user_preferences, user_profile, target_item, context=None):
        score = 25  # Score base
        
        # Verificar perfil de orçamento
        if user_profile:
            budget_pref = next((p for p in user_preferences if p.preference_type == "budget"), None)
            if budget_pref:
                destination = context.get('destination', '') if context else ''
                cost_level = context.get('cost_level', 'medium') if context else 'medium'
                
                if budget_pref.value == "low" and cost_level == "low":
                    score += 45
                elif budget_pref.value == "medium" and cost_level in ["low", "medium"]:
                    score += 40
                elif budget_pref.value == "high" and cost_level in ["medium", "high"]:
                    score += 35
        
        return min(score, 100)
    
    def get_strategy_name(self):
        return "Budget-Based"

class InterestBasedRecommendation(RecommendationStrategy):
    """Estratégia de recomendação baseada em interesses"""
    
    def calculate_score(self, user_preferences, user_profile, target_item, context=None):
        score = 35  # Score base
        
        # Verificar interesses do usuário
        interest_pref = next((p for p in user_preferences if p.preference_type == "interests"), None)
        if interest_pref:
            destination = context.get('destination', '') if context else ''
            item_category = context.get('category', '') if context else ''
            
            if interest_pref.value == "cultural" and destination in ["Madrid", "Paris", "Rome", "Athens"]:
                score += 35
            elif interest_pref.value == "nature" and destination in ["Rio de Janeiro", "Costa Rica", "New Zealand"]:
                score += 35
            elif interest_pref.value == "adventure" and item_category == "adventure":
                score += 30
        
        return min(score, 100)
    
    def get_strategy_name(self):
        return "Interest-Based"

class HybridRecommendation(RecommendationStrategy):
    """Estratégia híbrida que combina múltiplos fatores"""
    
    def calculate_score(self, user_preferences, user_profile, target_item, context=None):
        # Combinar scores de diferentes estratégias
        climate_strategy = ClimateBasedRecommendation()
        budget_strategy = BudgetBasedRecommendation()
        interest_strategy = InterestBasedRecommendation()
        
        climate_score = climate_strategy.calculate_score(user_preferences, user_profile, target_item, context)
        budget_score = budget_strategy.calculate_score(user_preferences, user_profile, target_item, context)
        interest_score = interest_strategy.calculate_score(user_preferences, user_profile, target_item, context)
        
        # Média ponderada
        total_score = (climate_score * 0.3 + budget_score * 0.3 + interest_score * 0.4)
        
        return min(int(total_score), 100)
    
    def get_strategy_name(self):
        return "Hybrid"

# === Strategy para Cálculo de Orçamento ===

class BudgetCalculationStrategy(ABC):
    """Interface Strategy para cálculos de orçamento"""
    
    @abstractmethod
    def calculate_budget(self, trip_data, user_preferences, context=None):
        """Calcula orçamento estimado"""
        pass
    
    @abstractmethod
    def get_strategy_name(self):
        """Retorna o nome da estratégia"""
        pass

class DailyBudgetStrategy(BudgetCalculationStrategy):
    """Estratégia de cálculo baseada em orçamento diário"""
    
    def calculate_budget(self, trip_data, user_preferences, context=None):
        start_date = datetime.strptime(trip_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(trip_data['end_date'], '%Y-%m-%d')
        days = (end_date - start_date).days
        
        # Orçamento base por dia
        base_daily = 100.0  # USD
        
        # Ajustar baseado nas preferências
        budget_pref = next((p for p in user_preferences if p.preference_type == "budget"), None)
        if budget_pref:
            if budget_pref.value == "low":
                base_daily = 50.0
            elif budget_pref.value == "medium":
                base_daily = 100.0
            elif budget_pref.value == "high":
                base_daily = 200.0
        
        # Ajustar baseado no destino
        destination = trip_data.get('destination', '')
        if destination in ["Paris", "Tokyo", "New York"]:
            base_daily *= 1.5  # Destinos caros
        elif destination in ["Recife", "Bangkok", "Prague"]:
            base_daily *= 0.7  # Destinos mais baratos
        
        return days * base_daily
    
    def get_strategy_name(self):
        return "Daily Budget"

class CategoryBasedBudgetStrategy(BudgetCalculationStrategy):
    """Estratégia de cálculo baseada em categorias de gastos"""
    
    def calculate_budget(self, trip_data, user_preferences, context=None):
        # Categorias de gastos com valores base
        categories = {
            'accommodation': 80.0,  # por noite
            'food': 40.0,          # por dia
            'transport': 30.0,     # por dia
            'activities': 50.0,    # por dia
            'shopping': 25.0       # por dia
        }
        
        start_date = datetime.strptime(trip_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(trip_data['end_date'], '%Y-%m-%d')
        days = (end_date - start_date).days
        nights = days - 1
        
        total_budget = 0
        
        # Ajustar valores baseado nas preferências
        budget_pref = next((p for p in user_preferences if p.preference_type == "budget"), None)
        multiplier = 1.0
        if budget_pref:
            if budget_pref.value == "low":
                multiplier = 0.6
            elif budget_pref.value == "high":
                multiplier = 1.5
        
        # Calcular orçamento por categoria
        total_budget += categories['accommodation'] * nights * multiplier
        total_budget += categories['food'] * days * multiplier
        total_budget += categories['transport'] * days * multiplier
        total_budget += categories['activities'] * days * multiplier
        total_budget += categories['shopping'] * days * multiplier
        
        return total_budget
    
    def get_strategy_name(self):
        return "Category-Based Budget"

class FlexibleBudgetStrategy(BudgetCalculationStrategy):
    """Estratégia flexível que se adapta ao perfil do usuário"""
    
    def calculate_budget(self, trip_data, user_preferences, user_profile, context=None):
        base_strategy = DailyBudgetStrategy()
        base_budget = base_strategy.calculate_budget(trip_data, user_preferences, context)
        
        # Ajustes baseados no perfil de viagem
        if user_profile:
            if user_profile.travel_style == "backpacker":
                base_budget *= 0.7
            elif user_profile.travel_style == "luxury":
                base_budget *= 2.0
            elif user_profile.travel_style == "business":
                base_budget *= 1.5
        
        # Ajustes baseados nas preferências específicas
        for pref in user_preferences:
            if pref.preference_type == "accommodation_style":
                if pref.value == "hostel":
                    base_budget *= 0.8
                elif pref.value == "luxury_hotel":
                    base_budget *= 1.8
        
        return base_budget
    
    def get_strategy_name(self):
        return "Flexible Budget"

# === Context para gerenciar estratégias ===

class RecommendationContext:
    """Context que gerencia as estratégias de recomendação"""
    
    def __init__(self):
        self.strategies = {
            'climate': ClimateBasedRecommendation(),
            'budget': BudgetBasedRecommendation(),
            'interest': InterestBasedRecommendation(),
            'hybrid': HybridRecommendation()
        }
        self.current_strategy = self.strategies['hybrid']  # Estratégia padrão
    
    def set_strategy(self, strategy_type):
        """Define a estratégia atual"""
        if strategy_type in self.strategies:
            self.current_strategy = self.strategies[strategy_type]
        else:
            raise ValueError(f"Estratégia não encontrada: {strategy_type}")
    
    def get_recommendation(self, user_preferences, user_profile, target_item, context=None):
        """Obtém recomendação usando a estratégia atual"""
        return self.current_strategy.calculate_score(
            user_preferences, user_profile, target_item, context
        )
    
    def get_available_strategies(self):
        """Retorna lista de estratégias disponíveis"""
        return list(self.strategies.keys())

class BudgetContext:
    """Context que gerencia as estratégias de cálculo de orçamento"""
    
    def __init__(self):
        self.strategies = {
            'daily': DailyBudgetStrategy(),
            'category': CategoryBasedBudgetStrategy(),
            'flexible': FlexibleBudgetStrategy()
        }
        self.current_strategy = self.strategies['flexible']  # Estratégia padrão
    
    def set_strategy(self, strategy_type):
        """Define a estratégia atual"""
        if strategy_type in self.strategies:
            self.current_strategy = self.strategies[strategy_type]
        else:
            raise ValueError(f"Estratégia não encontrada: {strategy_type}")
    
    def calculate_budget(self, trip_data, user_preferences, user_profile=None, context=None):
        """Calcula orçamento usando a estratégia atual"""
        return self.current_strategy.calculate_budget(
            trip_data, user_preferences, context
        )
    
    def get_available_strategies(self):
        """Retorna lista de estratégias disponíveis"""
        return list(self.strategies.keys())

# === Factory para criar estratégias ===

class StrategyFactory:
    """Factory para criar instâncias de estratégias"""
    
    @staticmethod
    def create_recommendation_strategy(strategy_type):
        """Cria estratégia de recomendação"""
        strategies = {
            'climate': ClimateBasedRecommendation(),
            'budget': BudgetBasedRecommendation(),
            'interest': InterestBasedRecommendation(),
            'hybrid': HybridRecommendation()
        }
        
        if strategy_type not in strategies:
            raise ValueError(f"Estratégia de recomendação não encontrada: {strategy_type}")
        
        return strategies[strategy_type]
    
    @staticmethod
    def create_budget_strategy(strategy_type):
        """Cria estratégia de orçamento"""
        strategies = {
            'daily': DailyBudgetStrategy(),
            'category': CategoryBasedBudgetStrategy(),
            'flexible': FlexibleBudgetStrategy()
        }
        
        if strategy_type not in strategies:
            raise ValueError(f"Estratégia de orçamento não encontrada: {strategy_type}")
        
        return strategies[strategy_type]
