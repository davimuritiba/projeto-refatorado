# --- Rotas da API ---
"""
Arquivo contendo todas as rotas da API do Travel Itinerary Planner.
Organizadas por funcionalidade para melhor manutenibilidade.
"""

from flask import request, jsonify
from datetime import datetime
from config import Config

# Função helper para verificar permissões
def user_has_permission(db, trip_id, user_id):
    """Verifica se o usuário tem permissão para acessar uma viagem"""
    trip = db.find_trip_by_id(trip_id)
    if not trip:
        return False, (jsonify({'message': Config.MESSAGES['NOT_FOUND']}), Config.HTTP_STATUS['NOT_FOUND'])
    collaborators = trip.collaborators if trip.collaborators is not None else []
    if trip.user_id == user_id or user_id in collaborators:
        return True, None
    return False, (jsonify({'message': Config.MESSAGES['FORBIDDEN']}), Config.HTTP_STATUS['FORBIDDEN'])

# Função helper para adicionar itens à viagem
def add_item_to_trip(db, trip_id, item_type):
    """Função helper para adicionar itens à viagem usando Factory Method"""
    data = request.get_json()
    user_id = data.pop('user_id', None)
    has_perm, error_resp = user_has_permission(db, trip_id, user_id)
    if not has_perm: 
        return error_resp

    add_method = getattr(db, f"add_{item_type}")
    item = add_method(trip_id, **data)
    return jsonify({item_type: item.to_dict()}), Config.HTTP_STATUS['CREATED']

# Função helper para atualizar status de itens
def update_item_status(db, item_type, item_id):
    """Função helper para atualizar status de itens"""
    data = request.get_json()
    collection_name = 'activities' if item_type == 'activity' else f'{item_type}s'
    updated_item = db._update_item_status(collection_name, item_id, data['is_done'])
    return jsonify(updated_item) if updated_item else (jsonify({'message': f'{item_type.capitalize()} not found'}), Config.HTTP_STATUS['NOT_FOUND'])

def register_routes(app, db):
    """
    Registra todas as rotas da aplicação
    Recebe a instância do Flask app e do DataStore
    """
    
    # === Rotas de Autenticação ===
    @app.route('/api/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        if db.find_user_by_email(data['email']): 
            return jsonify({'message': 'Este email já está em uso.'}), Config.HTTP_STATUS['CONFLICT']
        user = db.add_user(data['name'], data['email'], data['password'])
        return jsonify({'user': user.to_dict()}), Config.HTTP_STATUS['CREATED']

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = db.find_user_by_email(data['email'])
        if user and user.password == data['password']: 
            return jsonify({'user': user.to_dict()}), Config.HTTP_STATUS['OK']
        return jsonify({'message': Config.MESSAGES['UNAUTHORIZED']}), Config.HTTP_STATUS['UNAUTHORIZED']

    # === Rotas de Viagens ===
    @app.route('/api/trips', methods=['POST'])
    def create_trip():
        data = request.get_json()
        share_code = data.get('share_code', '').strip()
        trip = db.add_trip(data['user_id'], data['destination'], data['name'], data['start_date'], data['end_date'], share_code)
        
        if not trip:
            return jsonify({'message': 'Este código de partilha já está em uso. Por favor, escolha outro.'}), Config.HTTP_STATUS['CONFLICT']

        return jsonify({'trip': trip.to_dict()}), Config.HTTP_STATUS['CREATED']

    @app.route('/api/trips/join', methods=['POST'])
    def join_trip():
        data = request.get_json()
        share_code = data.get('share_code')
        user_id = data.get('user_id')
        trip = db.find_trip_by_share_code(share_code)
        if not trip:
            return jsonify({'message': 'Código de partilha inválido.'}), Config.HTTP_STATUS['NOT_FOUND']
        
        updated_trip = db.add_collaborator_to_trip(trip.id, user_id)
        return jsonify({'trip': updated_trip.to_dict()}), Config.HTTP_STATUS['OK']

    @app.route('/api/my-trips', methods=['GET'])
    def get_my_trips():
        user_id = int(request.args.get('user_id'))
        user_trips = db.get_user_trips(user_id)
        return jsonify({"trips": [t.to_dict() for t in user_trips]}), Config.HTTP_STATUS['OK']

    @app.route('/api/suggestions', methods=['GET'])
    def get_suggestions():
        suggestion_trips = db.get_suggestion_trips()
        return jsonify({"trips": [t.to_dict() for t in suggestion_trips]}), Config.HTTP_STATUS['OK']

    @app.route('/api/trips/<int:trip_id>', methods=['GET'])
    def get_trip(trip_id):
        trip = db.find_trip_by_id(trip_id)
        return jsonify({'trip': trip.to_dict()}) if trip else (jsonify({'message': 'Viagem não encontrada.'}), Config.HTTP_STATUS['NOT_FOUND'])

    @app.route('/api/trips/<int:trip_id>/budget', methods=['PATCH'])
    def update_budget(trip_id):
        data = request.get_json()
        user_id = data.get('user_id')
        has_perm, error_resp = user_has_permission(db, trip_id, user_id)
        if not has_perm: 
            return error_resp
        updated_trip = db.update_trip_budget(trip_id, float(data['budget']))
        return jsonify({'trip': updated_trip.to_dict()}) if updated_trip else (jsonify({'message': 'Viagem não encontrada.'}), Config.HTTP_STATUS['NOT_FOUND'])

    @app.route('/api/trips/<int:trip_id>/details', methods=['GET'])
    def get_trip_details(trip_id):
        details = db.get_details_for_trip(trip_id)
        return jsonify(details), Config.HTTP_STATUS['OK']

    # === Rotas de Itens do Itinerário (Factory Method) ===
    @app.route('/api/trips/<int:trip_id>/flights', methods=['POST'])
    def add_flight_to_trip(trip_id): 
        return add_item_to_trip(db, trip_id, 'flight')

    @app.route('/api/trips/<int:trip_id>/hotels', methods=['POST'])
    def add_hotel_to_trip(trip_id): 
        return add_item_to_trip(db, trip_id, 'hotel')

    @app.route('/api/trips/<int:trip_id>/activities', methods=['POST'])
    def add_activity_to_trip(trip_id): 
        return add_item_to_trip(db, trip_id, 'activity')

    # === Rotas usando Template Method Pattern ===
    @app.route('/api/trips/<int:trip_id>/process-flight', methods=['POST'])
    def process_flight_with_template(trip_id):
        """Nova rota que usa Template Method Pattern para processar voos"""
        data = request.get_json()
        user_id = data.pop('user_id', None)
        has_perm, error_resp = user_has_permission(db, trip_id, user_id)
        if not has_perm: 
            return error_resp

        try:
            processed_flight = db.process_item_with_template('flight', data, trip_id, user_id)
            return jsonify({
                'message': 'Voo processado com sucesso usando Template Method',
                'flight': processed_flight.to_dict()
            }), Config.HTTP_STATUS['CREATED']
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']

    @app.route('/api/trips/<int:trip_id>/process-hotel', methods=['POST'])
    def process_hotel_with_template(trip_id):
        """Nova rota que usa Template Method Pattern para processar hotéis"""
        data = request.get_json()
        user_id = data.pop('user_id', None)
        has_perm, error_resp = user_has_permission(db, trip_id, user_id)
        if not has_perm: 
            return error_resp

        try:
            processed_hotel = db.process_item_with_template('hotel', data, trip_id, user_id)
            return jsonify({
                'message': 'Hotel processado com sucesso usando Template Method',
                'hotel': processed_hotel.to_dict()
            }), Config.HTTP_STATUS['CREATED']
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']

    @app.route('/api/trips/<int:trip_id>/process-activity', methods=['POST'])
    def process_activity_with_template(trip_id):
        """Nova rota que usa Template Method Pattern para processar atividades"""
        data = request.get_json()
        user_id = data.pop('user_id', None)
        has_perm, error_resp = user_has_permission(db, trip_id, user_id)
        if not has_perm: 
            return error_resp

        try:
            processed_activity = db.process_item_with_template('activity', data, trip_id, user_id)
            return jsonify({
                'message': 'Atividade processada com sucesso usando Template Method',
                'activity': processed_activity.to_dict()
            }), Config.HTTP_STATUS['CREATED']
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']

    @app.route('/api/trips/<int:trip_id>/process-expense', methods=['POST'])
    def process_expense_with_template(trip_id):
        """Nova rota que usa Template Method Pattern para processar despesas"""
        data = request.get_json()
        user_id = data.pop('user_id', None)
        has_perm, error_resp = user_has_permission(db, trip_id, user_id)
        if not has_perm: 
            return error_resp

        try:
            processed_expense = db.process_item_with_template('expense', data, trip_id, user_id)
            return jsonify({
                'message': 'Despesa processada com sucesso usando Template Method',
                'expense': processed_expense.to_dict()
            }), Config.HTTP_STATUS['CREATED']
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']

    @app.route('/api/processors', methods=['GET'])
    def get_available_processors():
        """Rota que retorna os processadores disponíveis (Template Method Pattern)"""
        processors_info = []
        for item_type, processor in db._processors.items():
            processors_info.append({
                'type': item_type,
                'description': f'Processador para {item_type}s usando Template Method Pattern',
                'available_methods': [
                    'validate_item_data',
                    'create_item_object', 
                    'enrich_item_data',
                    'save_item',
                    'log_processing_result'
                ]
            })
        
        return jsonify({
            'message': 'Processadores disponíveis usando Template Method Pattern',
            'processors': processors_info
        }), Config.HTTP_STATUS['OK']

    # === Rotas de Despesas ===
    @app.route('/api/trips/<int:trip_id>/expenses', methods=['GET', 'POST'])
    def handle_expenses(trip_id):
        if request.method == 'GET':
            expenses = db.get_expenses_for_trip(trip_id)
            return jsonify({"expenses": [e.to_dict() for e in expenses]}), Config.HTTP_STATUS['OK']
        if request.method == 'POST':
            return add_item_to_trip(db, trip_id, 'expense')

    @app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
    def delete_expense(expense_id):
        if db.remove_expense(expense_id):
            return jsonify({'message': 'Despesa removida com sucesso.'}), Config.HTTP_STATUS['OK']
        return jsonify({'message': 'Despesa não encontrada.'}), Config.HTTP_STATUS['NOT_FOUND']

    # === Rotas de Status de Itens ===
    @app.route('/api/flights/<int:item_id>/status', methods=['PATCH'])
    def update_flight_status(item_id): 
        return update_item_status(db, 'flight', item_id)

    @app.route('/api/hotels/<int:item_id>/status', methods=['PATCH'])
    def update_hotel_status(item_id): 
        return update_item_status(db, 'hotel', item_id)

    @app.route('/api/activities/<int:item_id>/status', methods=['PATCH'])
    def update_activity_status(item_id): 
        return update_item_status(db, 'activity', item_id)

    # === Rotas de Guias de Viagem ===
    @app.route('/api/travel-guides', methods=['GET'])
    def get_travel_guides():
        destination = request.args.get('destination')
        category = request.args.get('category')
        
        if destination:
            guides = db.get_travel_guides_by_destination(destination)
        elif category:
            guides = db.get_travel_guides_by_category(category)
        else:
            guides = db.get_all_travel_guides()
        
        return jsonify({"guides": [guide.to_dict() for guide in guides]}), Config.HTTP_STATUS['OK']

    @app.route('/api/travel-guides', methods=['POST'])
    def create_travel_guide():
        data = request.get_json()
        guide = db.add_travel_guide(
            trip_id=data.get('trip_id', 0),
            destination=data['destination'],
            title=data['title'],
            content=data['content'],
            category=data['category'],
            tags=data.get('tags', []),
            author=data.get('author', 'Sistema')
        )
        return jsonify({"guide": guide.to_dict()}), Config.HTTP_STATUS['CREATED']

    @app.route('/api/travel-guides/<int:guide_id>', methods=['GET'])
    def get_travel_guide(guide_id):
        guides = db.get_all_travel_guides()
        guide = next((g for g in guides if g.id == guide_id), None)
        if guide:
            return jsonify({"guide": guide.to_dict()}), Config.HTTP_STATUS['OK']
        return jsonify({'message': 'Guia não encontrado.'}), Config.HTTP_STATUS['NOT_FOUND']

    # === Rotas de Recursos de Viagem ===
    @app.route('/api/travel-resources', methods=['GET'])
    def get_travel_resources():
        destination = request.args.get('destination')
        resource_type = request.args.get('type')
        
        if destination:
            resources = db.get_travel_resources_by_destination(destination)
        elif resource_type:
            resources = db.get_travel_resources_by_type(resource_type)
        else:
            resources = db.get_all_travel_resources()
        
        return jsonify({"resources": [resource.to_dict() for resource in resources]}), Config.HTTP_STATUS['OK']

    @app.route('/api/travel-resources', methods=['POST'])
    def create_travel_resource():
        data = request.get_json()
        resource = db.add_travel_resource(
            trip_id=data.get('trip_id', 0),
            destination=data['destination'],
            title=data['title'],
            resource_type=data['resource_type'],
            url=data.get('url'),
            description=data.get('description', ''),
            contact_info=data.get('contact_info', {})
        )
        return jsonify({"resource": resource.to_dict()}), Config.HTTP_STATUS['CREATED']

    @app.route('/api/travel-resources/<int:resource_id>', methods=['GET'])
    def get_travel_resource(resource_id):
        resources = db.get_all_travel_resources()
        resource = next((r for r in resources if r.id == resource_id), None)
        if resource:
            return jsonify({"resource": resource.to_dict()}), Config.HTTP_STATUS['OK']
        return jsonify({'message': 'Recurso não encontrado.'}), Config.HTTP_STATUS['NOT_FOUND']

    # === Rotas usando Strategy Pattern ===
    
    @app.route('/api/recommendations/strategies', methods=['GET'])
    def get_recommendation_strategies():
        """Retorna as estratégias de recomendação disponíveis"""
        strategies = db.get_available_recommendation_strategies()
        return jsonify({
            'message': 'Estratégias de recomendação disponíveis',
            'strategies': strategies,
            'descriptions': {
                'climate': 'Baseada em preferências climáticas',
                'budget': 'Baseada em orçamento disponível',
                'interest': 'Baseada em interesses pessoais',
                'hybrid': 'Combinação de múltiplos fatores'
            }
        }), Config.HTTP_STATUS['OK']
    
    @app.route('/api/budget/strategies', methods=['GET'])
    def get_budget_strategies():
        """Retorna as estratégias de cálculo de orçamento disponíveis"""
        strategies = db.get_available_budget_strategies()
        return jsonify({
            'message': 'Estratégias de orçamento disponíveis',
            'strategies': strategies,
            'descriptions': {
                'daily': 'Cálculo baseado em orçamento diário',
                'category': 'Cálculo baseado em categorias de gastos',
                'flexible': 'Cálculo adaptativo ao perfil do usuário'
            }
        }), Config.HTTP_STATUS['OK']
    
    @app.route('/api/recommendations/<int:user_id>/smart', methods=['POST'])
    def generate_smart_recommendations(user_id):
        """Gera recomendações inteligentes usando Strategy Pattern"""
        data = request.get_json()
        recommendation_type = data.get('type', 'destination')
        strategy_type = data.get('strategy', 'hybrid')
        
        try:
            recommendations = db.generate_smart_recommendations(
                user_id, recommendation_type, strategy_type
            )
            
            return jsonify({
                'message': f'Recomendações geradas usando estratégia {strategy_type}',
                'recommendations': [
                    {
                        'recommendation': rec['recommendation'].to_dict(),
                        'strategy_info': rec['strategy_info']
                    } for rec in recommendations
                ],
                'strategy_used': strategy_type,
                'total_recommendations': len(recommendations)
            }), Config.HTTP_STATUS['OK']
            
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']
    
    @app.route('/api/recommendations/<int:user_id>/test-strategy', methods=['POST'])
    def test_recommendation_strategy(user_id):
        """Testa uma estratégia específica de recomendação"""
        data = request.get_json()
        target_item = data.get('target_item')
        strategy_type = data.get('strategy', 'hybrid')
        context = data.get('context', {})
        
        if not target_item:
            return jsonify({'message': 'target_item é obrigatório'}), Config.HTTP_STATUS['BAD_REQUEST']
        
        try:
            result = db.get_recommendation_with_strategy(user_id, target_item, strategy_type, context)
            
            return jsonify({
                'message': f'Teste de estratégia {strategy_type} concluído',
                'result': result
            }), Config.HTTP_STATUS['OK']
            
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']
    
    @app.route('/api/budget/<int:user_id>/calculate', methods=['POST'])
    def calculate_budget_with_strategy(user_id):
        """Calcula orçamento usando uma estratégia específica"""
        data = request.get_json()
        strategy_type = data.get('strategy', 'flexible')
        
        # Validar dados da viagem
        required_fields = ['destination', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'message': f'Campos obrigatórios não preenchidos: {", ".join(missing_fields)}'
            }), Config.HTTP_STATUS['BAD_REQUEST']
        
        try:
            result = db.calculate_budget_with_strategy(data, user_id, strategy_type)
            
            return jsonify({
                'message': f'Orçamento calculado usando estratégia {strategy_type}',
                'result': result
            }), Config.HTTP_STATUS['OK']
            
        except ValueError as e:
            return jsonify({'message': f'Erro de validação: {str(e)}'}), Config.HTTP_STATUS['BAD_REQUEST']
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']
    
    @app.route('/api/strategy/compare', methods=['POST'])
    def compare_strategies():
        """Compara diferentes estratégias para o mesmo input"""
        data = request.get_json()
        user_id = data.get('user_id')
        target_item = data.get('target_item')
        context = data.get('context', {})
        
        if not user_id or not target_item:
            return jsonify({
                'message': 'user_id e target_item são obrigatórios'
            }), Config.HTTP_STATUS['BAD_REQUEST']
        
        try:
            # Testar todas as estratégias disponíveis
            strategies = db.get_available_recommendation_strategies()
            comparison_results = []
            
            for strategy_type in strategies:
                result = db.get_recommendation_with_strategy(user_id, target_item, strategy_type, context)
                comparison_results.append(result)
            
            # Ordenar por score
            comparison_results.sort(key=lambda x: x['score'], reverse=True)
            
            return jsonify({
                'message': 'Comparação de estratégias concluída',
                'target_item': target_item,
                'user_id': user_id,
                'comparison_results': comparison_results,
                'best_strategy': comparison_results[0] if comparison_results else None
            }), Config.HTTP_STATUS['OK']
            
        except Exception as e:
            return jsonify({'message': f'Erro interno: {str(e)}'}), Config.HTTP_STATUS['INTERNAL_ERROR']
