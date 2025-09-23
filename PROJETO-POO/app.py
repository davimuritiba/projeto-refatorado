# --- Importações ---
import json
import os
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify #converter dict python para database.json
from flask_cors import CORS #FUNCIONAMENTO DA API

#Classes 

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


# Classe de Armazenamento com json
class DataStore:
    def __init__(self, filename='database.json'):
        self._filename = filename
        self._data = self._load_data()

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

    def _add_item(self, collection_name, item_class, trip_id, **kwargs):
        # Este método agora pode adicionar qualquer 'ItineraryItem'
        item = item_class(self._get_next_id(collection_name), trip_id, **kwargs)
        self._data[collection_name].append(item.to_dict())
        self._save_data()
        return item
    
    def add_flight(self, trip_id, **kwargs): return self._add_item('flights', Flight, trip_id, **kwargs)
    def add_hotel(self, trip_id, **kwargs): return self._add_item('hotels', Hotel, trip_id, **kwargs)
    def add_activity(self, trip_id, **kwargs): return self._add_item('activities', Activity, trip_id, **kwargs)
    def add_expense(self, trip_id, **kwargs): return self._add_item('expenses', Expense, trip_id, **kwargs)

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
        guide = TravelGuide(self._get_next_id('travel_guides'), trip_id, destination, title, content, category, tags, author)
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
        resource = TravelResource(self._get_next_id('travel_resources'), trip_id, destination, title, resource_type, url, description, contact_info)
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
        review = Review(self._get_next_id('reviews'), trip_id, user_id, item_type, item_id, rating, comment)
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
        contribution = UserContribution(self._get_next_id('user_contributions'), trip_id, user_id, contribution_type, title, content)
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
            reaction = UserReaction(self._get_next_id('user_reactions'), trip_id, user_id, target_type, target_id, reaction_type)
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
        preference = UserPreference(self._get_next_id('user_preferences'), trip_id, user_id, preference_type, value, weight)
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
        profile = TravelProfile(self._get_next_id('travel_profiles'), trip_id, user_id, profile_name, travel_style, budget_range, interests, climate_preference, accommodation_style, transport_preference)
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
        recommendation = Recommendation(self._get_next_id('recommendations'), trip_id, user_id, recommendation_type, target_id, score, reason)
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
app = Flask(__name__)
CORS(app)
db = DataStore()


# Helpers ---
def user_has_permission(trip_id, user_id):
    trip = db.find_trip_by_id(trip_id)
    if not trip:
        return False, (jsonify({'message': 'Viagem não encontrada.'}), 404)
    collaborators = trip.collaborators if trip.collaborators is not None else []
    if trip.user_id == user_id or user_id in collaborators:
        return True, None
    return False, (jsonify({'message': 'Permissão negada.'}), 403)


#  Rotas da API ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if db.find_user_by_email(data['email']): 
        return jsonify({'message': 'Este email já está em uso.'}), 409
    user = db.add_user(data['name'], data['email'], data['password'])
    return jsonify({'user': user.to_dict()}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.find_user_by_email(data['email'])
    if user and user.password == data['password']: 
        return jsonify({'user': user.to_dict()}), 200
    return jsonify({'message': 'Credenciais inválidas.'}), 401

@app.route('/api/trips', methods=['POST'])
def create_trip():
    data = request.get_json()
    share_code = data.get('share_code', '').strip()
    trip = db.add_trip(data['user_id'], data['destination'], data['name'], data['start_date'], data['end_date'], share_code)
    
    if not trip:
        return jsonify({'message': 'Este código de partilha já está em uso. Por favor, escolha outro.'}), 409

    return jsonify({'trip': trip.to_dict()}), 201

@app.route('/api/trips/join', methods=['POST'])
def join_trip():
    data = request.get_json()
    share_code = data.get('share_code')
    user_id = data.get('user_id')
    trip = db.find_trip_by_share_code(share_code)
    if not trip:
        return jsonify({'message': 'Código de partilha inválido.'}), 404
    
    updated_trip = db.add_collaborator_to_trip(trip.id, user_id)
    return jsonify({'trip': updated_trip.to_dict()}), 200

@app.route('/api/my-trips', methods=['GET'])
def get_my_trips():
    user_id = int(request.args.get('user_id'))
    user_trips = db.get_user_trips(user_id)
    return jsonify({"trips": [t.to_dict() for t in user_trips]}), 200

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    suggestion_trips = db.get_suggestion_trips()
    return jsonify({"trips": [t.to_dict() for t in suggestion_trips]}), 200

@app.route('/api/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    trip = db.find_trip_by_id(trip_id)
    return jsonify({'trip': trip.to_dict()}) if trip else (jsonify({'message': 'Viagem não encontrada.'}), 404)

@app.route('/api/trips/<int:trip_id>/budget', methods=['PATCH'])
def update_budget(trip_id):
    data = request.get_json()
    user_id = data.get('user_id')
    has_perm, error_resp = user_has_permission(trip_id, user_id)
    if not has_perm: return error_resp
    updated_trip = db.update_trip_budget(trip_id, float(data['budget']))
    return jsonify({'trip': updated_trip.to_dict()}) if updated_trip else (jsonify({'message': 'Viagem não encontrada.'}), 404)

@app.route('/api/trips/<int:trip_id>/details', methods=['GET'])
def get_trip_details(trip_id):
    details = db.get_details_for_trip(trip_id)
    return jsonify(details), 200

def add_item_to_trip(trip_id, item_type):
    data = request.get_json()
    user_id = data.pop('user_id', None)
    has_perm, error_resp = user_has_permission(trip_id, user_id)
    if not has_perm: return error_resp

    add_method = getattr(db, f"add_{item_type}")
    item = add_method(trip_id, **data)
    return jsonify({item_type: item.to_dict()}), 201

@app.route('/api/trips/<int:trip_id>/flights', methods=['POST'])
def add_flight_to_trip(trip_id): return add_item_to_trip(trip_id, 'flight')
@app.route('/api/trips/<int:trip_id>/hotels', methods=['POST'])
def add_hotel_to_trip(trip_id): return add_item_to_trip(trip_id, 'hotel')
@app.route('/api/trips/<int:trip_id>/activities', methods=['POST'])
def add_activity_to_trip(trip_id): return add_item_to_trip(trip_id, 'activity')

@app.route('/api/trips/<int:trip_id>/expenses', methods=['GET', 'POST'])
def handle_expenses(trip_id):
    if request.method == 'GET':
        expenses = db.get_expenses_for_trip(trip_id)
        return jsonify({"expenses": [e.to_dict() for e in expenses]}), 200
    if request.method == 'POST':
        return add_item_to_trip(trip_id, 'expense')

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    if db.remove_expense(expense_id):
        return jsonify({'message': 'Despesa removida com sucesso.'}), 200
    return jsonify({'message': 'Despesa não encontrada.'}), 404

def update_item_status(item_type, item_id):
    data = request.get_json()
    collection_name = 'activities' if item_type == 'activity' else f'{item_type}s'
    updated_item = db._update_item_status(collection_name, item_id, data['is_done'])
    return jsonify(updated_item) if updated_item else (jsonify({'message': f'{item_type.capitalize()} not found'}), 404)

@app.route('/api/flights/<int:item_id>/status', methods=['PATCH'])
def update_flight_status(item_id): return update_item_status('flight', item_id)
@app.route('/api/hotels/<int:item_id>/status', methods=['PATCH'])
def update_hotel_status(item_id): return update_item_status('hotel', item_id)
@app.route('/api/activities/<int:item_id>/status', methods=['PATCH'])
def update_activity_status(item_id): return update_item_status('activity', item_id)

# Rotas para Guias de Viagem
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
    
    return jsonify({"guides": [guide.to_dict() for guide in guides]}), 200

@app.route('/api/travel-guides', methods=['POST'])
def create_travel_guide():
    data = request.get_json()
    guide = db.add_travel_guide(
        destination=data['destination'],
        title=data['title'],
        content=data['content'],
        category=data['category'],
        tags=data.get('tags', []),
        author=data.get('author', 'Sistema')
    )
    return jsonify({"guide": guide.to_dict()}), 201

@app.route('/api/travel-guides/<int:guide_id>', methods=['GET'])
def get_travel_guide(guide_id):
    guides = db.get_all_travel_guides()
    guide = next((g for g in guides if g.id == guide_id), None)
    if guide:
        return jsonify({"guide": guide.to_dict()}), 200
    return jsonify({'message': 'Guia não encontrado.'}), 404

# Rotas para Recursos de Viagem
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
    
    return jsonify({"resources": [resource.to_dict() for resource in resources]}), 200

@app.route('/api/travel-resources', methods=['POST'])
def create_travel_resource():
    data = request.get_json()
    resource = db.add_travel_resource(
        destination=data['destination'],
        title=data['title'],
        resource_type=data['resource_type'],
        url=data.get('url'),
        description=data.get('description', ''),
        contact_info=data.get('contact_info', {})
    )
    return jsonify({"resource": resource.to_dict()}), 201

@app.route('/api/travel-resources/<int:resource_id>', methods=['GET'])
def get_travel_resource(resource_id):
    resources = db.get_all_travel_resources()
    resource = next((r for r in resources if r.id == resource_id), None)
    if resource:
        return jsonify({"resource": resource.to_dict()}), 200
    return jsonify({'message': 'Recurso não encontrado.'}), 404


# Função para inicializar dados de exemplo
def initialize_sample_data():
    # Verificar se já existem dados
    if len(db.get_all_travel_guides()) == 0:
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

        db.generate_personalized_recommendations(1, "destination")
        db.generate_personalized_recommendations(2, "destination")
        db.generate_personalized_recommendations(1, "activity")
        db.generate_personalized_recommendations(2, "activity")

        print("Dados de exemplo inicializados com sucesso!")

#  Execução da Aplicação 
if __name__ == '__main__':
    initialize_sample_data()
    app.run(debug=True)

