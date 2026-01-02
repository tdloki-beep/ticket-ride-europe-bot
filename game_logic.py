from typing import List, Tuple, Optional, Dict
from game_state import GameState, Player, PlayerAction
from config import ROUTE_POINTS, CITIES, ROUTES
import random

class GameLogic:
    """Основная игровая логика"""
    
    @staticmethod
    def can_claim_route(player: Player, route_info: Tuple, game_state: GameState) -> Tuple[bool, str]:
        """
        Проверить, может ли игрок захватить маршрут
        Возвращает (может_захватить, сообщение_об_ошибке)
        """
        city1, city2, length, color, is_tunnel = route_info
        
        # Проверка количества вагонов
        if player.trains < length:
            return False, "Недостаточно вагонов"
        
        # Проверка карт в руке
        if color == "gray":
            # Для серых маршрутов - любой цвет
            # Найдем цвет, которого больше всего
            color_counts = {}
            for card in player.hand:
                if card != 'locomotive':
                    color_counts[card] = color_counts.get(card, 0) + 1
            
            if not color_counts:
                return False, "Нет подходящих карт"
            
            best_color = max(color_counts.keys(), key=lambda x: color_counts[x])
            available_cards = color_counts.get(best_color, 0)
            locomotives = player.hand.count('locomotive')
            
            if available_cards + locomotives < length:
                return False, f"Недостаточно карт цвета {best_color}"
        else:
            # Для цветных маршрутов
            available_cards = player.hand.count(color)
            locomotives = player.hand.count('locomotive')
            
            if available_cards + locomotives < length:
                return False, f"Недостаточно карт цвета {color}"
        
        return True, "Можно захватить"
    
    @staticmethod
    def claim_route(player: Player, route_info: Tuple, game_state: GameState, chosen_color: str = None) -> bool:
        """
        Захватить маршрут
        """
        city1, city2, length, color, is_tunnel = route_info
        
        can_claim, message = GameLogic.can_claim_route(player, route_info, game_state)
        if not can_claim:
            return False
        
        # Определяем, какие карты использовать
        if color == "gray":
            if chosen_color is None:
                # Автоматически выбираем цвет, которого больше всего
                color_counts = {}
                for card in player.hand:
                    if card != 'locomotive':
                        color_counts[card] = color_counts.get(card, 0) + 1
                
                if color_counts:
                    chosen_color = max(color_counts.keys(), key=lambda x: color_counts[x])
                else:
                    chosen_color = 'locomotive'
            
            # Используем карты выбранного цвета
            cards_to_use = []
            available_cards = player.hand.count(chosen_color)
            locomotives = player.hand.count('locomotive')
            
            # Используем обычные карты
            for _ in range(min(available_cards, length)):
                cards_to_use.append(chosen_color)
            
            # Добавляем локомотивы, если не хватает
            remaining = length - len(cards_to_use)
            for _ in range(min(locomotives, remaining)):
                cards_to_use.append('locomotive')
        else:
            # Цветной маршрут
            cards_to_use = []
            available_cards = player.hand.count(color)
            locomotives = player.hand.count('locomotive')
            
            # Используем карты нужного цвета
            for _ in range(min(available_cards, length)):
                cards_to_use.append(color)
            
            # Добавляем локомотивы
            remaining = length - len(cards_to_use)
            for _ in range(min(locomotives, remaining)):
                cards_to_use.append('locomotive')
        
        # Удаляем карты из руки
        for card in cards_to_use:
            player.hand.remove(card)
        
        # Добавляем в сброс
        game_state.discard_pile.extend(cards_to_use)
        
        # Уменьшаем количество вагонов
        player.trains -= length
        
        # Добавляем очки
        player.points += ROUTE_POINTS.get(length, 0)
        
        # Добавляем маршрут к игроку
        player.claimed_routes.append({
            'cities': [city1, city2],
            'length': length,
            'color': color
        })
        
        return True
    
    @staticmethod
    def draw_train_card(player: Player, game_state: GameState, card_index: int = None) -> bool:
        """
        Взять карту вагона
        """
        if card_index is not None and 0 <= card_index < len(game_state.open_cards):
            # Берем открытую карту
            card = game_state.open_cards.pop(card_index)
            player.hand.append(card)
            
            # Добавляем новую карту из колоды
            if game_state.train_deck:
                game_state.open_cards.append(game_state.train_deck.pop())
        else:
            # Берем из колоды
            if game_state.train_deck:
                card = game_state.train_deck.pop()
                player.hand.append(card)
        
        return True
    
    @staticmethod
    def draw_route_cards(player: Player, game_state: GameState, count: int = 3) -> List[str]:
        """
        Взять карты маршрутов
        """
        drawn_routes = []
        for _ in range(count):
            if game_state.route_deck:
                route = game_state.route_deck.pop()
                drawn_routes.append(route)
        
        return drawn_routes
    
    @staticmethod
    def check_end_game(game_state: GameState) -> bool:
        """
        Проверить, закончилась ли игра
        """
        for player in game_state.players.values():
            if player.trains <= 2:
                return True
        return False
    
    @staticmethod
    def calculate_final_scores(game_state: GameState) -> Dict[int, int]:
        """
        Подсчитать финальные очки
        """
        scores = {}
        for player_id, player in game_state.players.items():
            scores[player_id] = player.points
        return scores
    
    @staticmethod
    def get_available_routes(player: Player, game_state: GameState) -> List[Tuple]:
        """
        Получить список доступных для захвата маршрутов
        """
        available_routes = []
        for route in ROUTES:
            can_claim, _ = GameLogic.can_claim_route(player, route, game_state)
            if can_claim:
                available_routes.append(route)
        return available_routes
    
    @staticmethod
    def get_route_by_cities(city1: str, city2: str) -> Optional[Tuple]:
        """
        Найти маршрут по городам
        """
        for route in ROUTES:
            if (route[0] == city1 and route[1] == city2) or \
               (route[0] == city2 and route[1] == city1):
                return route
        return None