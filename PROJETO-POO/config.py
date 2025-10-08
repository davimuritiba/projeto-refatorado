# --- Configuração da Aplicação Flask ---
"""
Arquivo de configuração centralizado para a aplicação Travel Itinerary Planner.
Contém todas as configurações da aplicação Flask e constantes do sistema.
"""

from flask import Flask
from flask_cors import CORS
import os

def create_app():
    """
    Factory function para criar e configurar a aplicação Flask
    Segue o padrão Application Factory do Flask
    """
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuração CORS para permitir requisições da API
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Configurações do banco de dados JSON
    app.config['DATABASE_FILE'] = 'database.json'
    
    # Configurações de logging
    app.config['LOG_LEVEL'] = 'INFO'
    
    return app

# Constantes da aplicação
class Config:
    """Classe com constantes de configuração"""
    
    # Tipos de itens do itinerário suportados
    SUPPORTED_ITEM_TYPES = [
        'flight', 'hotel', 'activity', 'expense',
        'travel_guide', 'travel_resource', 'review',
        'user_contribution', 'user_reaction', 'user_preference',
        'recommendation', 'travel_profile'
    ]
    
    # Campos obrigatórios para diferentes tipos
    REQUIRED_FIELDS = {
        'flight': ['company', 'code', 'departure', 'arrival'],
        'hotel': ['name', 'checkin', 'checkout'],
        'activity': ['description', 'date'],
        'expense': ['description', 'amount', 'currency', 'date', 'category']
    }
    
    # Códigos de status HTTP
    HTTP_STATUS = {
        'OK': 200,
        'CREATED': 201,
        'BAD_REQUEST': 400,
        'UNAUTHORIZED': 401,
        'FORBIDDEN': 403,
        'NOT_FOUND': 404,
        'CONFLICT': 409,
        'INTERNAL_ERROR': 500
    }
    
    # Mensagens de resposta padrão
    MESSAGES = {
        'SUCCESS': 'Operação realizada com sucesso',
        'NOT_FOUND': 'Recurso não encontrado',
        'UNAUTHORIZED': 'Credenciais inválidas',
        'FORBIDDEN': 'Permissão negada',
        'CONFLICT': 'Conflito de dados',
        'VALIDATION_ERROR': 'Erro de validação',
        'INTERNAL_ERROR': 'Erro interno do servidor'
    }
