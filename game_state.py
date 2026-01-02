from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

class GamePhase(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"

class PlayerAction(Enum):
    DRAW_CARDS = "draw_cards"
    CLAIM_ROUTE = "claim_route"
    DRAW_ROUTES = "draw_routes"

class Player:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name
        self.trains = 45  # Количество вагонов
        self.hand = []  # Карты в руке
        self.routes = []  # Карты маршрутов
        self.claimed_routes = []  # Захваченные маршруты
        self.points = 0
        self.is_bot = False
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'trains': self.trains,
            'hand': self.hand,
            'routes': self.routes,
            'claimed_routes': self.claimed_routes,
            'points': self.points,
            'is_bot': self.is_bot
        }
    
    @classmethod
    def from_dict(cls, data):
        player = cls(data['user_id'], data['name'])
        player.trains = data['trains']
        player.hand = data['hand']
        player.routes = data['routes']
        player.claimed_routes = data['claimed_routes']
        player.points = data['points']
        player.is_bot = data['is_bot']
        return player

class GameState:
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.phase = GamePhase.WAITING
        self.players: Dict[int, Player] = {}
        self.current_player_id: Optional[int] = None
        self.open_cards = []  # Открытые карты
        self.train_deck = []  # Колода вагонов
        self.route_deck = []  # Колода маршрутов
        self.discard_pile = []  # Сброс
        self.last_activity = None
        self.winner = None
        
    def add_player(self, user_id: int, name: str) -> bool:
        """Добавить игрока в игру"""
        if self.phase != GamePhase.WAITING:
            return False
        if len(self.players) >= 5:
            return False
        if user_id in self.players:
            return False
            
        self.players[user_id] = Player(user_id, name)
        return True
    
    def remove_player(self, user_id: int) -> bool:
        """Удалить игрока из игры"""
        if user_id not in self.players:
            return False
        del self.players[user_id]
        return True
    
    def start_game(self) -> bool:
        """Начать игру"""
        if len(self.players) < 2:
            return False
            
        self.phase = GamePhase.PLAYING
        # Инициализация колод и карт
        self._initialize_decks()
        self._deal_initial_cards()
        
        # Первый игрок
        self.current_player_id = list(self.players.keys())[0]
        return True
    
    def _initialize_decks(self):
        """Инициализация колод"""
        from config import TRAIN_CARDS_COUNT
        
        # Колода вагонов
        self.train_deck = []
        for color, count in TRAIN_CARDS_COUNT.items():
            self.train_deck.extend([color] * count)
        
        # Перемешиваем
        import random
        random.shuffle(self.train_deck)
        
        # Открытые карты
        self.open_cards = []
        for _ in range(5):
            self.open_cards.append(self.train_deck.pop())
        
        # Колода маршрутов (упрощенная)
        self.route_deck = [f"Маршрут_{i}" for i in range(30)]
        random.shuffle(self.route_deck)
    
    def _deal_initial_cards(self):
        """Раздача начальных карт"""
        from config import INITIAL_CARDS, INITIAL_ROUTE_CARDS
        
        for player in self.players.values():
            # Начальные карты вагонов
            for _ in range(INITIAL_CARDS):
                player.hand.append(self.train_deck.pop())
            
            # Начальные карты маршрутов
            for _ in range(INITIAL_ROUTE_CARDS):
                player.routes.append(self.route_deck.pop())
    
    def get_current_player(self) -> Optional[Player]:
        """Получить текущего игрока"""
        if self.current_player_id is None:
            return None
        return self.players.get(self.current_player_id)
    
    def next_turn(self):
        """Следующий ход"""
        player_ids = list(self.players.keys())
        current_index = player_ids.index(self.current_player_id)
        next_index = (current_index + 1) % len(player_ids)
        self.current_player_id = player_ids[next_index]
    
    def to_dict(self):
        return {
            'chat_id': self.chat_id,
            'phase': self.phase.value,
            'players': {k: v.to_dict() for k, v in self.players.items()},
            'current_player_id': self.current_player_id,
            'open_cards': self.open_cards,
            'train_deck_size': len(self.train_deck),
            'route_deck_size': len(self.route_deck),
            'discard_pile': self.discard_pile,
            'winner': self.winner
        }
    
    @classmethod
    def from_dict(cls, data):
        game = cls(data['chat_id'])
        game.phase = GamePhase(data['phase'])
        game.players = {k: Player.from_dict(v) for k, v in data['players'].items()}
        game.current_player_id = data['current_player_id']
        game.open_cards = data['open_cards']
        game.train_deck = ['unknown'] * data['train_deck_size']  # Восстанавливаем размер
        game.route_deck = ['unknown'] * data['route_deck_size']
        game.discard_pile = data['discard_pile']
        game.winner = data['winner']
        return game

# Хранилище игр (в продакшене лучше использовать БД)
games: Dict[int, GameState] = {}