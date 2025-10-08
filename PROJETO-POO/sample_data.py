# --- Inicialização de Dados de Exemplo ---
"""
Arquivo responsável por inicializar dados de exemplo no banco de dados.
Contém guias de viagem, recursos, avaliações e outros dados para demonstração.
"""

from datetime import datetime

def initialize_sample_data(db):
    """
    Função para inicializar dados de exemplo no banco de dados
    Recebe uma instância do DataStore como parâmetro
    """
    # Verificar se já existem dados
    if len(db.get_all_travel_guides()) == 0:
        _initialize_travel_guides(db)
        _initialize_travel_resources(db)
        _initialize_reviews(db)
        _initialize_user_contributions(db)
        _initialize_user_preferences(db)
        _initialize_travel_profiles(db)
        _initialize_recommendations(db)
        _test_template_method_pattern(db)
        _test_strategy_pattern(db)

        print("Dados de exemplo inicializados com sucesso!")

def _initialize_travel_guides(db):
    """Inicializa guias de viagem de exemplo"""
    
    # Guia de Madrid - Cultural
    db.add_travel_guide(
        trip_id=0,
        destination="Madrid",
        title="Guia Cultural de Madrid",
        content="""
        Madrid é uma cidade rica em cultura e história. Aqui estão os principais pontos turísticos:

        **Museus Imperdíveis:**
        - Museu do Prado: Uma das maiores coleções de arte europeia
        - Museu Reina Sofía: Arte moderna e contemporânea, incluindo o Guernica de Picasso
        - Museu Thyssen-Bornemisza: Coleção privada com obras de mestres clássicos

        **Arquitetura:**
        - Palácio Real: Residência oficial da família real espanhola
        - Plaza Mayor: Praça histórica no centro da cidade
        - Puerta del Sol: Praça mais famosa de Madrid

        **Dicas:**
        - Visite o Parque do Retiro para relaxar
        - Experimente o famoso churros com chocolate quente
        - Use o transporte público, é eficiente e barato
        """,
        category="cultural",
        tags=["museus", "história", "arte", "arquitetura"]
    )
    
    # Guia de Madrid - Gastronomia
    db.add_travel_guide(
        trip_id=0,
        destination="Madrid",
        title="Gastronomia de Madrid",
        content="""
        A gastronomia madrilenha é uma delícia para os sentidos:

        **Pratos Típicos:**
        - Cocido Madrileño: Estufado tradicional com grão-de-bico e carne
        - Bocadillo de Calamares: Sanduíche de lula frita
        - Churros con Chocolate: Doce tradicional para o café da manhã

        **Bairros Gastronômicos:**
        - La Latina: Tapas e vida noturna
        - Malasaña: Restaurantes modernos e trendy
        - Chueca: Cozinha internacional e LGBT-friendly

        **Dicas:**
        - Almoce tarde (14h-16h) como os locais
        - Jante ainda mais tarde (21h-23h)
        - Peça tapas para compartilhar
        """,
        category="gastronomia",
        tags=["tapas", "churros", "cozinha tradicional", "vida noturna"]
    )

    # Guia de Recife - Cultural
    db.add_travel_guide(
        trip_id=0,
        destination="Recife",
        title="Guia Cultural de Recife",
        content="""
        Recife é o coração cultural do Nordeste brasileiro:

        **Pontos Históricos:**
        - Marco Zero: Centro histórico da cidade
        - Instituto Ricardo Brennand: Museu com arte medieval
        - Forte das Cinco Pontas: Fortaleza colonial bem preservada

        **Arte e Cultura:**
        - Museu Cais do Sertão: Homenagem a Luiz Gonzaga
        - Paço do Frevo: Centro cultural dedicado ao frevo
        - Oficina Cerâmica Francisco Brennand: Arte contemporânea

        **Eventos:**
        - Carnaval de Recife: Uma das maiores festas do Brasil
        - São João: Festa junina tradicional
        - Festival de Inverno de Garanhuns

        **Dicas:**
        - Visite Olinda, cidade vizinha histórica
        - Experimente a culinária local no Mercado da Boa Vista
        - Use protetor solar, o sol é forte o ano todo
        """,
        category="cultural",
        tags=["história", "carnaval", "frevo", "arte", "marco zero"]
    )

    # Guia de Recife - Transporte
    db.add_travel_guide(
        trip_id=0,
        destination="Recife",
        title="Transporte em Recife",
        content="""
        Como se locomover em Recife:

        **Transporte Público:**
        - Metrô: Linha única que conecta o centro ao aeroporto
        - Ônibus: Rede extensa, mas pode ser lenta no trânsito
        - BRT: Corredor expresso para algumas áreas

        **Transporte Privado:**
        - Uber/99: Muito usado e acessível
        - Táxi: Disponível mas mais caro que apps
        - Aluguel de carro: Útil para explorar o interior

        **Dicas:**
        - Evite o horário de pico (7h-9h, 17h-19h)
        - O trânsito pode ser intenso no centro
        - Muitos hotéis oferecem traslado do aeroporto
        """,
        category="transporte",
        tags=["metrô", "uber", "trânsito", "aeroporto"]
    )

def _initialize_travel_resources(db):
    """Inicializa recursos de viagem de exemplo"""
    
    # Recursos de Madrid
    db.add_travel_resource(
        trip_id=0,
        destination="Madrid",
        title="Hospital La Paz",
        resource_type="hospital",
        description="Hospital público de referência em Madrid",
        contact_info={
            "telefone": "+34 91 727 70 00",
            "endereco": "Paseo de la Castellana, 261, 28046 Madrid",
            "emergencia": "112"
        }
    )

    db.add_travel_resource(
        trip_id=0,
        destination="Madrid",
        title="Embaixada do Brasil em Madrid",
        resource_type="embaixada",
        description="Representação diplomática brasileira na Espanha",
        contact_info={
            "telefone": "+34 91 700 46 00",
            "endereco": "Calle de Fernando el Santo, 6, 28010 Madrid",
            "email": "madrid@itamaraty.gov.br"
        }
    )

    # Recursos de Recife
    db.add_travel_resource(
        trip_id=0,
        destination="Recife",
        title="Hospital Real Português",
        resource_type="hospital",
        description="Hospital privado de referência em Recife",
        contact_info={
            "telefone": "(81) 3416-5000",
            "endereco": "R. do Bonjardim, 159 - Santo Amaro, Recife - PE",
            "emergencia": "192"
        }
    )

    db.add_travel_resource(
        trip_id=0,
        destination="Recife",
        title="Consulado Geral da Espanha",
        resource_type="embaixada",
        description="Representação consular espanhola em Recife",
        contact_info={
            "telefone": "(81) 3427-7200",
            "endereco": "R. da Consolação, 80 - Boa Vista, Recife - PE",
            "email": "cog.recife@maec.es"
        }
    )

def _initialize_reviews(db):
    """Inicializa avaliações de exemplo"""
    
    # Avaliações de destinos
    db.add_review(
        trip_id=0,
        user_id=1,
        item_type="destination",
        item_id=1,
        rating=5,
        comment="Madrid é uma cidade incrível! Os museus são fantásticos e a vida noturna é animada. Recomendo muito!"
    )
    
    db.add_review(
        trip_id=0,
        user_id=1,
        item_type="destination", 
        item_id=2,
        rating=4,
        comment="Recife tem uma cultura riquíssima! O Carnaval é espetacular e a comida é deliciosa. Só cuidado com o sol forte."
    )
    
    db.add_review(
        trip_id=0,
        user_id=2,
        item_type="destination",
        item_id=1,
        rating=4,
        comment="Adorei a arquitetura de Madrid. O Palácio Real é lindo, mas fiquei decepcionado com alguns restaurantes turísticos."
    )

def _initialize_user_contributions(db):
    """Inicializa contribuições de usuários de exemplo"""
    
    db.add_user_contribution(
        trip_id=0,
        user_id=1,
        contribution_type="tip",
        title="Dica: Melhor época para visitar Madrid",
        content="A melhor época para visitar Madrid é de abril a junho e de setembro a novembro. O clima está agradável e há menos turistas. Evite agosto, pois faz muito calor e muitos estabelecimentos fecham para férias."
    )
    
    db.add_user_contribution(
        trip_id=0,
        user_id=2,
        contribution_type="tip",
        title="Como economizar em Recife",
        content="Para economizar em Recife: use o transporte público (metrô é barato), coma em restaurantes populares no centro, visite as praias públicas (não pague ingressos desnecessários) e negocie preços em feiras."
    )
    
    db.add_user_contribution(
        trip_id=0,
        user_id=1,
        contribution_type="destination",
        title="Toledo - Cidade medieval próxima a Madrid",
        content="Toledo é uma cidade medieval encantadora a apenas 1h de Madrid. Vale muito a pena fazer um bate-volta! A catedral é impressionante e as vistas da cidade são espetaculares."
    )

def _initialize_user_preferences(db):
    """Inicializa preferências de usuários de exemplo"""
    
    # Preferências do usuário 1
    db.add_user_preference(
        trip_id=0,
        user_id=1,
        preference_type="climate",
        value="temperate",
        weight=8
    )
    
    db.add_user_preference(
        trip_id=0,
        user_id=1,
        preference_type="interests",
        value="cultural",
        weight=9
    )
    
    db.add_user_preference(
        trip_id=0,
        user_id=1,
        preference_type="budget",
        value="medium",
        weight=7
    )
    
    # Preferências do usuário 2
    db.add_user_preference(
        trip_id=0,
        user_id=2,
        preference_type="climate",
        value="tropical",
        weight=9
    )
    
    db.add_user_preference(
        trip_id=0,
        user_id=2,
        preference_type="interests",
        value="nature",
        weight=8
    )
    
    db.add_user_preference(
        trip_id=0,
        user_id=2,
        preference_type="budget",
        value="low",
        weight=9
    )

def _initialize_travel_profiles(db):
    """Inicializa perfis de viagem de exemplo"""
    
    db.add_travel_profile(
        trip_id=0,
        user_id=1,
        profile_name="Viajante Cultural",
        travel_style="cultural",
        budget_range="medium",
        interests=["cultural", "history", "art", "museums"],
        climate_preference="temperate",
        accommodation_style="hotel",
        transport_preference="public"
    )
    
    db.add_travel_profile(
        trip_id=0,
        user_id=2,
        profile_name="Aventureiro Economista",
        travel_style="backpacker",
        budget_range="low",
        interests=["nature", "adventure", "beaches", "local_culture"],
        climate_preference="tropical",
        accommodation_style="hostel",
        transport_preference="mixed"
    )

def _initialize_recommendations(db):
    """Inicializa recomendações personalizadas"""
    
    db.generate_personalized_recommendations(1, "destination")
    db.generate_personalized_recommendations(2, "destination")
    db.generate_personalized_recommendations(1, "activity")
    db.generate_personalized_recommendations(2, "activity")

def _test_template_method_pattern(db):
    """Testa o Template Method Pattern com dados de exemplo"""
    
    print("\n=== Testando Template Method Pattern ===")
    
    # Criar uma viagem de exemplo para testar
    test_trip = db.add_trip(1, "Tokyo", "Viagem de Teste Template Method", "2024-06-01", "2024-06-10", "")
    
    if test_trip:
        # Testar processamento de voo usando Template Method
        flight_data = {
            'company': 'JAL',
            'code': 'JL001',
            'departure': '2024-06-01T08:00:00',
            'arrival': '2024-06-01T15:30:00'
        }
        
        try:
            processed_flight = db.process_item_with_template('flight', flight_data, test_trip.id, 1)
            print(f"✅ Voo processado com Template Method: {processed_flight.company} {processed_flight.code}")
        except Exception as e:
            print(f"❌ Erro ao processar voo: {e}")
        
        # Testar processamento de hotel usando Template Method
        hotel_data = {
            'name': 'Hotel Tokyo Station',
            'checkin': '2024-06-01',
            'checkout': '2024-06-05'
        }
        
        try:
            processed_hotel = db.process_item_with_template('hotel', hotel_data, test_trip.id, 1)
            print(f"✅ Hotel processado com Template Method: {processed_hotel.name}")
        except Exception as e:
            print(f"❌ Erro ao processar hotel: {e}")
        
        # Testar processamento de atividade usando Template Method
        activity_data = {
            'description': 'Visita ao Templo Senso-ji',
            'date': '2024-06-02'
        }
        
        try:
            processed_activity = db.process_item_with_template('activity', activity_data, test_trip.id, 1)
            print(f"✅ Atividade processada com Template Method: {processed_activity.description}")
        except Exception as e:
            print(f"❌ Erro ao processar atividade: {e}")
        
        # Testar processamento de despesa usando Template Method
        expense_data = {
            'description': 'Almoço no restaurante local',
            'amount': 45.50,
            'currency': 'JPY',
            'date': '2024-06-02',
            'category': 'food'
        }
        
        try:
            processed_expense = db.process_item_with_template('expense', expense_data, test_trip.id, 1)
            print(f"✅ Despesa processada com Template Method: {processed_expense.description} - ¥{processed_expense.amount}")
        except Exception as e:
            print(f"❌ Erro ao processar despesa: {e}")
    
    print("=== Template Method Pattern testado com sucesso! ===\n")

def _test_strategy_pattern(db):
    """Testa o Strategy Pattern com dados de exemplo"""
    
    print("\n=== Testando Strategy Pattern ===")
    
    # Testar estratégias de recomendação
    print("\n📊 Testando Estratégias de Recomendação:")
    
    # Testar com usuário 1 (cultural, temperate, medium budget)
    test_context = {"destination": "Madrid", "cost_level": "medium", "category": "cultural"}
    
    try:
        # Testar estratégia Climate-Based
        result = db.get_recommendation_with_strategy(1, "Madrid", "climate", test_context)
        print(f"✅ Estratégia Climate-Based: Score {result['score']} para Madrid (Usuário 1)")
        
        # Testar estratégia Budget-Based
        result = db.get_recommendation_with_strategy(1, "Madrid", "budget", test_context)
        print(f"✅ Estratégia Budget-Based: Score {result['score']} para Madrid (Usuário 1)")
        
        # Testar estratégia Interest-Based
        result = db.get_recommendation_with_strategy(1, "Madrid", "interest", test_context)
        print(f"✅ Estratégia Interest-Based: Score {result['score']} para Madrid (Usuário 1)")
        
        # Testar estratégia Hybrid
        result = db.get_recommendation_with_strategy(1, "Madrid", "hybrid", test_context)
        print(f"✅ Estratégia Hybrid: Score {result['score']} para Madrid (Usuário 1)")
        
    except Exception as e:
        print(f"❌ Erro ao testar estratégias de recomendação: {e}")
    
    # Testar com usuário 2 (nature, tropical, low budget)
    test_context_2 = {"destination": "Recife", "cost_level": "low", "category": "cultural"}
    
    try:
        # Testar estratégia Climate-Based
        result = db.get_recommendation_with_strategy(2, "Recife", "climate", test_context_2)
        print(f"✅ Estratégia Climate-Based: Score {result['score']} para Recife (Usuário 2)")
        
        # Testar estratégia Budget-Based
        result = db.get_recommendation_with_strategy(2, "Recife", "budget", test_context_2)
        print(f"✅ Estratégia Budget-Based: Score {result['score']} para Recife (Usuário 2)")
        
        # Testar estratégia Hybrid
        result = db.get_recommendation_with_strategy(2, "Recife", "hybrid", test_context_2)
        print(f"✅ Estratégia Hybrid: Score {result['score']} para Recife (Usuário 2)")
        
    except Exception as e:
        print(f"❌ Erro ao testar estratégias de recomendação para usuário 2: {e}")
    
    # Testar estratégias de cálculo de orçamento
    print("\n💰 Testando Estratégias de Cálculo de Orçamento:")
    
    trip_data = {
        'destination': 'Madrid',
        'start_date': '2024-06-01',
        'end_date': '2024-06-10'
    }
    
    try:
        # Testar estratégia Daily Budget
        result = db.calculate_budget_with_strategy(trip_data, 1, "daily")
        print(f"✅ Estratégia Daily Budget: ${result['estimated_budget']:.2f} para viagem de 9 dias em Madrid")
        
        # Testar estratégia Category-Based
        result = db.calculate_budget_with_strategy(trip_data, 1, "category")
        print(f"✅ Estratégia Category-Based: ${result['estimated_budget']:.2f} para viagem de 9 dias em Madrid")
        
        # Testar estratégia Flexible
        result = db.calculate_budget_with_strategy(trip_data, 1, "flexible")
        print(f"✅ Estratégia Flexible: ${result['estimated_budget']:.2f} para viagem de 9 dias em Madrid")
        
    except Exception as e:
        print(f"❌ Erro ao testar estratégias de orçamento: {e}")
    
    # Testar geração de recomendações inteligentes
    print("\n🎯 Testando Geração de Recomendações Inteligentes:")
    
    try:
        # Gerar recomendações usando estratégia Hybrid
        recommendations = db.generate_smart_recommendations(1, "destination", "hybrid")
        print(f"✅ Recomendações Hybrid geradas: {len(recommendations)} destinos recomendados")
        
        # Gerar recomendações usando estratégia Climate-Based
        recommendations = db.generate_smart_recommendations(1, "destination", "climate")
        print(f"✅ Recomendações Climate-Based geradas: {len(recommendations)} destinos recomendados")
        
        # Gerar recomendações de atividades
        recommendations = db.generate_smart_recommendations(1, "activity", "interest")
        print(f"✅ Recomendações de atividades geradas: {len(recommendations)} atividades recomendadas")
        
    except Exception as e:
        print(f"❌ Erro ao gerar recomendações inteligentes: {e}")
    
    # Testar comparação de estratégias
    print("\n⚖️ Testando Comparação de Estratégias:")
    
    try:
        # Comparar todas as estratégias para o mesmo destino
        strategies = db.get_available_recommendation_strategies()
        print(f"✅ Estratégias disponíveis: {', '.join(strategies)}")
        
        # Testar cada estratégia para Paris
        for strategy in strategies:
            result = db.get_recommendation_with_strategy(1, "Paris", strategy, {"destination": "Paris", "cost_level": "high", "category": "cultural"})
            print(f"   📈 {strategy}: Score {result['score']} para Paris")
        
    except Exception as e:
        print(f"❌ Erro ao comparar estratégias: {e}")
    
    print("\n=== Strategy Pattern testado com sucesso! ===\n")
