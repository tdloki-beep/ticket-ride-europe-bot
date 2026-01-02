from typing import List, Tuple, Optional, Dict
from game_state import GameState, Player, PlayerAction
from game_logic import GameLogic
from config import ROUTE_POINTS
import random

class AIStrategy:
    """Стратегия для AI игрока"""
    
    def __init__(self, aggression_level: float = 0.7):
        """
        aggression_level: уровень агрессивности (0.0 - 1.0)
        - 0.0 - очень осторожный
        - 1.0 - очень агрессивный
        """
        self.aggression_level = aggression_level
        self.long_routes_priority = 0.8  # Приоритет длинных маршрутов
        self.card_collection_weight = 0.6  # Важность сбора карт
        
    def decide_next_move(self, game_state: GameState, player: Player) -> Tuple[PlayerAction, Dict]:
        """
        Принять решение о следующем ходе
        Возвращает (действие, параметры)
        """
        available_routes = GameLogic.get_available_routes(player, game_state)
        
        # Анализируем ситуацию
        situation = self._analyze_situation(game_state, player, available_routes)
        
        # Выбираем стратегию в зависимости от ситуации
        if situation['urgency'] > 0.8 and available_routes:
            # Срочная ситуация - захватываем маршрут
            return self._select_route_to_claim(player, available_routes, situation)
        elif situation['need_cards'] > 0.7:
            # Нужны карты - берем карты
            return self._select_cards_to_draw(game_state, situation)
        elif available_routes and random.random() < self.aggression_level:
            # Агрессивная стратегия - захватываем маршрут
            return self._select_route_to_claim(player, available_routes, situation)
        else:
            # Консервативная стратегия - собираем карты
            return self._select_cards_to_draw(game_state, situation)
    
    def _analyze_situation(self, game_state: GameState, player: Player, available_routes: List) -> Dict:
        """
        Проанализировать текущую игровую ситуацию
        """
        # Количество оставшихся вагонов
        trains_left = player.trains
        total_trains = 45
        trains_used = total_trains - trains_left
        
        # Прогресс игры (0.0 - начало, 1.0 - конец)
        game_progress = trains_used / total_trains
        
        # Срочность (нужно ли срочно захватывать маршруты)
        urgency = 0.0
        if trains_left < 10:
            urgency = 0.9
        elif trains_left < 20 and game_progress > 0.5:
            urgency = 0.7
        elif game_progress > 0.7:
            urgency = 0.6
        
        # Потребность в картах
        need_cards = 0.0
        if len(player.hand) < 5:
            need_cards = 0.9
        elif len(player.hand) < 10:
            need_cards = 0.6
        
        # Оценка доступных маршрутов
        route_scores = []
        for route in available_routes:
            score = self._evaluate_route(route, player, game_state)
            route_scores.append((route, score))
        
        # Сортируем по оценке
        route_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'game_progress': game_progress,
            'urgency': urgency,
            'need_cards': need_cards,
            'route_scores': route_scores,
            'best_route': route_scores[0] if route_scores else None
        }
    
    def _evaluate_route(self, route: Tuple, player: Player, game_state: GameState) -> float:
        """
        Оценить ценность маршрута
        """
        city1, city2, length, color, is_tunnel = route
        
        # Базовые очки за маршрут
        base_points = ROUTE_POINTS.get(length, 0)
        
        # Множители
        length_multiplier = 1.0
        if length >= 5:
            length_multiplier = 1.5  # Длинные маршруты ценнее
        elif length <= 2:
            length_multiplier = 0.8  # Короткие менее ценны
        
        # Цветовой множитель
        color_multiplier = 1.0
        if color == "gray":
            # Серые маршруты более универсальны
            color_multiplier = 1.2
        
        # Эффективность использования карт
        if color == "gray":
            # Для серых маршрутов смотрим, какие карты есть
            color_counts = {}
            for card in player.hand:
                if card != 'locomotive':
                    color_counts[card] = color_counts.get(card, 0) + 1
            
            if color_counts:
                best_color_count = max(color_counts.values())
                card_efficiency = min(best_color_count / length, 1.0)
            else:
                card_efficiency = 0.5  # Только локомотивы
        else:
            # Для цветных маршрутов
            color_cards = player.hand.count(color)
            locomotives = player.hand.count('locomotive')
            total_suitable = color_cards + locomotives
            card_efficiency = min(total_suitable / length, 1.0)
        
        # Стратегическая ценность (связность сети)
        strategic_value = self._calculate_strategic_value(route, player)
        
        # Итоговая оценка
        score = (base_points * length_multiplier * color_multiplier * 
                card_efficiency * strategic_value)
        
        return score
    
    def _calculate_strategic_value(self, route: Tuple, player: Player) -> float:
        """
        Рассчитать стратегическую ценность маршрута
        (насколько он помогает связать сеть)
        """
        city1, city2, length, color, is_tunnel = route
        
        # Получаем города, которые уже соединены игроком
        connected_cities = set()
        for claimed_route in player.claimed_routes:
            connected_cities.update(claimed_route['cities'])
        
        # Если маршрут соединяет с существующей сетью - высокая ценность
        if city1 in connected_cities or city2 in connected_cities:
            return 1.5
        
        # Если это изолированный маршрут - базовая ценность
        return 1.0
    
    def _select_route_to_claim(self, player: Player, available_routes: List, situation: Dict) -> Tuple[PlayerAction, Dict]:
        """
        Выбрать маршрут для захвата
        """
        best_route, score = situation['best_route']
        
        # Если оценка слишком низкая - не захватываем
        if score < 3.0 and situation['urgency'] < 0.5:
            return self._select_cards_to_draw(None, situation)
        
        city1, city2, length, color, is_tunnel = best_route
        
        # Для серых маршрутов определяем цвет
        chosen_color = None
        if color == "gray":
            color_counts = {}
            for card in player.hand:
                if card != 'locomotive':
                    color_counts[card] = color_counts.get(card, 0) + 1
            
            if color_counts:
                chosen_color = max(color_counts.keys(), key=lambda x: color_counts[x])
        
        return PlayerAction.CLAIM_ROUTE, {
            'city1': city1,
            'city2': city2,
            'chosen_color': chosen_color
        }
    
    def _select_cards_to_draw(self, game_state: GameState, situation: Dict) -> Tuple[PlayerAction, Dict]:
        """
        Выбрать карты для взятия
        """
        # Стратегия выбора карт
        # 1. Приоритет локомотивам (универсальные)
        # 2. Цветам, которых не хватает для маршрутов
        # 3. Разнообразию
        
        if game_state and game_state.open_cards:
            # Смотрим открытые карты
            open_cards = game_state.open_cards
            locomotive_indices = [i for i, card in enumerate(open_cards) if card == 'locomotive']
            
            # Если есть локомотив - берем его
            if locomotive_indices and random.random() < 0.7:
                return PlayerAction.DRAW_CARDS, {
                    'card_index': locomotive_indices[0],
                    'from_deck': False
                }
            
            # Иначе берем случайную открытую карту
            if open_cards:
                card_index = random.randint(0, len(open_cards) - 1)
                return PlayerAction.DRAW_CARDS, {
                    'card_index': card_index,
                    'from_deck': False
                }
        
        # Берем из колоды
        return PlayerAction.DRAW_CARDS, {
            'from_deck': True
        }
    
    def predict_next_move(self, game_state: GameState, player: Player) -> str:
        """
        Предсказать следующий ход (для отображения пользователю)
        """
        action, params = self.decide_next_move(game_state, player)
        
        if action == PlayerAction.CLAIM_ROUTE:
            city1 = params['city1']
            city2 = params['city2']
            return f"🤖 Бот планирует захватить маршрут: {city1} → {city2}"
        elif action == PlayerAction.DRAW_CARDS:
            if params.get('from_deck'):
                return "🤖 Бот планирует взять карту из колоды"
            else:
                card_index = params.get('card_index', 0)
                return f"🤖 Бот планирует взять открытую карту #{card_index + 1}"
        elif action == PlayerAction.DRAW_ROUTES:
            return "🤖 Бот планирует взять карты маршрутов"
        
        return "🤖 Бот думает..."
    
    def get_strategy_explanation(self) -> str:
        """
        Получить объяснение текущей стратегии
        """
        strategies = [
            "🎯 Агрессивная стратегия: захват длинных маршрутов",
            "🎯 Баланс: захват маршрутов + сбор карт",
            "🎯 Консервативная стратегия: сбор карт и ожидание",
            "🎯 Адаптивная стратегия: реагирование на действия соперников"
        ]
        
        if self.aggression_level > 0.8:
            return strategies[0]
        elif self.aggression_level > 0.6:
            return strategies[1]
        elif self.aggression_level > 0.3:
            return strategies[2]
        else:
            return strategies[3]