from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
from game_state import GameState, Player
from config import CITIES, ROUTES
import io
import base64

class MapVisualizer:
    """Визуализатор карты Ticket to Ride"""
    
    def __init__(self):
        # Цвета для разных типов карт
        self.color_map = {
            'red': '#FF4444',
            'blue': '#4444FF',
            'green': '#44FF44',
            'yellow': '#FFFF44',
            'purple': '#AA44FF',
            'black': '#444444',
            'white': '#FFFFFF',
            'orange': '#FF8844',
            'gray': '#AAAAAA',
            'locomotive': '#FFD700'
        }
        
        # Координаты городов (карта Европы для Ticket to Ride Europe)
        self.city_positions = {
            "Лондон": (0.15, 0.55),
            "Париж": (0.25, 0.50),
            "Берлин": (0.55, 0.55),
            "Вена": (0.58, 0.48),
            "Рим": (0.45, 0.35),
            "Мадрид": (0.10, 0.25),
            "Барселона": (0.20, 0.28),
            "Мюнхен": (0.48, 0.50),
            "Прага": (0.52, 0.52),
            "Варшава": (0.65, 0.52),
            "Будапешт": (0.60, 0.45),
            "Бухарест": (0.72, 0.42),
            "София": (0.68, 0.38),
            "Стамбул": (0.78, 0.40),
            "Афины": (0.65, 0.30),
            "Санкт-Петербург": (0.70, 0.65),
            "Москва": (0.80, 0.58),
            "Киев": (0.75, 0.48),
            "Вильнюс": (0.70, 0.55),
            "Рига": (0.68, 0.60),
            "Стокгольм": (0.58, 0.75),
            "Осло": (0.45, 0.78),
            "Копенгаген": (0.48, 0.65),
            "Амстердам": (0.32, 0.58),
            "Брюссель": (0.30, 0.52),
            "Цюрих": (0.40, 0.45),
            "Венеция": (0.47, 0.40),
            "Загреб": (0.53, 0.42),
            "Сараево": (0.58, 0.38),
            "Скопье": (0.62, 0.35),
            "Тирана": (0.60, 0.32),
            "Салоники": (0.65, 0.32),
            "Смирна": (0.75, 0.32),
            "Палермо": (0.42, 0.20),
            "Неаполь": (0.45, 0.28),
            "Флоренция": (0.43, 0.32),
            "Генуя": (0.38, 0.38),
            "Марсель": (0.32, 0.38),
            "Лион": (0.32, 0.45),
            "Бордо": (0.22, 0.42),
            "Нант": (0.22, 0.48),
            "Брест": (0.12, 0.48),
            "Плимут": (0.12, 0.52),
            "Дублин": (0.10, 0.58),
            "Эдинбург": (0.15, 0.72),
            "Гамбург": (0.48, 0.62),
            "Франкфурт": (0.42, 0.52),
            "Страсбург": (0.38, 0.48),
            "Милан": (0.42, 0.42),
            "Турин": (0.38, 0.42),
            "Бриндизи": (0.52, 0.28),
            "Лиссабон": (0.05, 0.22),
            "Голуэй": (0.08, 0.62),
            "Анкара": (0.82, 0.38),
            "Монреаль": (0.15, 0.82),
            "Ванкувер": (0.05, 0.85)
        }
        
        # Размеры для рисования
        self.figure_size = (16, 12)
        self.node_size = 800
        self.edge_width = 8
    
    def create_map_image(self, game_state: GameState) -> bytes:
        """
        Создать изображение карты с текущим состоянием игры
        """
        fig, ax = plt.subplots(1, 1, figsize=self.figure_size)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Рисуем фон (цвет моря/земли)
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#E8F4F8', zorder=0))
        
        # Рисуем маршруты
        self._draw_routes(ax, game_state)
        
        # Рисуем города
        self._draw_cities(ax, game_state)
        
        # Добавляем информационную панель
        self._draw_info_panel(ax, game_state)
        
        # Сохраняем изображение в буфер
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()
        
        return buf.read()
    
    def _draw_routes(self, ax, game_state: GameState):
        """
        Нарисовать маршруты на карте
        """
        # Сначала рисуем незахваченные маршруты
        for route in ROUTES:
            city1, city2, length, color, is_tunnel = route
            
            # Проверяем, захвачен ли маршрут
            is_claimed = False
            claimed_by = None
            
            for player in game_state.players.values():
                for claimed_route in player.claimed_routes:
                    if set(claimed_route['cities']) == {city1, city2}:
                        is_claimed = True
                        claimed_by = player
                        break
                if is_claimed:
                    break
            
            if not is_claimed:
                # Рисуем незахваченный маршрут
                self._draw_route_segment(ax, city1, city2, color, alpha=0.6)
            else:
                # Рисуем захваченный маршрут
                player_color = self._get_player_color(claimed_by.user_id)
                self._draw_route_segment(ax, city1, city2, player_color, alpha=0.9, claimed=True)
    
    def _draw_route_segment(self, ax, city1: str, city2: str, color: str, alpha: float = 0.8, claimed: bool = False):
        """
        Нарисовать отрезок маршрута между двумя городами
        """
        if city1 not in self.city_positions or city2 not in self.city_positions:
            return
        
        x1, y1 = self.city_positions[city1]
        x2, y2 = self.city_positions[city2]
        
        # Цвет маршрута
        route_color = self.color_map.get(color, '#888888')
        
        # Толщина линии
        line_width = 10 if claimed else 6
        
        # Рисуем линию
        ax.plot([x1, x2], [y1, y2], 
                color=route_color, 
                linewidth=line_width, 
                alpha=alpha,
                solid_capstyle='round',
                zorder=1)
        
        # Если маршрут захвачен, добавляем обводку
        if claimed:
            ax.plot([x1, x2], [y1, y2], 
                    color='white', 
                    linewidth=line_width + 4, 
                    alpha=0.3,
                    solid_capstyle='round',
                    zorder=0)
    
    def _draw_cities(self, ax, game_state: GameState):
        """
        Нарисовать города на карте
        """
        for city, (x, y) in self.city_positions.items():
            # Определяем цвет города
            city_color = '#FFFFFF'
            
            # Проверяем, связан ли город маршрутами
            is_connected = any(
                city in route[0:2] for route in ROUTES
            )
            
            if is_connected:
                # Рисуем город как круг
                circle = plt.Circle((x, y), 0.025, 
                                  color=city_color, 
                                  ec='black', 
                                  linewidth=2, 
                                  zorder=3)
                ax.add_patch(circle)
                
                # Добавляем название города
                ax.text(x, y - 0.04, city, 
                       ha='center', va='top', 
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', 
                               facecolor='white', 
                               edgecolor='black', 
                               alpha=0.8),
                       zorder=4)
    
    def _draw_info_panel(self, ax, game_state: GameState):
        """
        Нарисовать информационную панель
        """
        # Панель справа
        panel_x = 1.02
        panel_y = 0.95
        
        # Заголовок
        ax.text(panel_x, panel_y, "Ticket to Ride", 
               fontsize=16, fontweight='bold', 
               transform=ax.transAxes,
               bbox=dict(boxstyle='round,pad=0.5', 
                        facecolor='lightblue', 
                        edgecolor='black'))
        
        # Информация об игроках
        y_offset = -0.08
        for i, (player_id, player) in enumerate(game_state.players.items()):
            player_text = f"{player.name}: {player.points} очков ({player.trains} вагонов)"
            
            # Цвет игрока
            player_color = self._get_player_color(player_id)
            
            ax.text(panel_x, panel_y + y_offset * (i + 1), player_text,
                   fontsize=10,
                   transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.3',
                            facecolor=player_color,
                            alpha=0.3,
                            edgecolor='black'))
        
        # Текущий игрок
        current_player = game_state.get_current_player()
        if current_player:
            ax.text(panel_x, 0.05, 
                   f"Ходит: {current_player.name}",
                   fontsize=12, fontweight='bold',
                   transform=ax.transAxes,
                   bbox=dict(boxstyle='round,pad=0.4',
                            facecolor='yellow',
                            edgecolor='black'))
    
    def _get_player_color(self, player_id: int) -> str:
        """
        Получить цвет игрока
        """
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        return colors[player_id % len(colors)]
    
    def create_player_hand_image(self, player: Player) -> bytes:
        """
        Создать изображение карт игрока
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 4)
        ax.axis('off')
        
        # Заголовок
        ax.text(5, 3.5, f"Карты игрока {player.name}", 
               fontsize=16, ha='center', fontweight='bold')
        
        # Подсчет карт по цветам
        color_counts = {}
        for card in player.hand:
            color_counts[card] = color_counts.get(card, 0) + 1
        
        # Рисуем карты
        x_offset = 1
        y_offset = 2
        card_width = 0.8
        card_height = 1.2
        
        colors_order = ['red', 'blue', 'green', 'yellow', 'purple', 
                       'black', 'white', 'orange', 'locomotive']
        
        for color in colors_order:
            if color in color_counts:
                count = color_counts[color]
                
                # Рисуем карту
                rect = FancyBboxPatch((x_offset, y_offset), card_width, card_height,
                                     boxstyle="round,pad=0.05",
                                     facecolor=self.color_map[color],
                                     edgecolor='black',
                                     linewidth=2)
                ax.add_patch(rect)
                
                # Количество
                ax.text(x_offset + card_width/2, y_offset + card_height/2, 
                       str(count),
                       fontsize=20, ha='center', va='center',
                       fontweight='bold',
                       color='white' if color in ['black', 'blue', 'purple'] else 'black')
                
                # Название цвета
                color_names = {
                    'red': 'Красный',
                    'blue': 'Синий',
                    'green': 'Зеленый',
                    'yellow': 'Желтый',
                    'purple': 'Фиолетовый',
                    'black': 'Черный',
                    'white': 'Белый',
                    'orange': 'Оранжевый',
                    'locomotive': 'Локомотив'
                }
                
                ax.text(x_offset + card_width/2, y_offset - 0.2, 
                       color_names.get(color, color),
                       fontsize=8, ha='center', va='top')
                
                x_offset += card_width + 0.2
        
        # Информация о маршрутах
        ax.text(5, 0.8, f"Карт маршрутов: {len(player.routes)}", 
               fontsize=12, ha='center')
        ax.text(5, 0.4, f"Вагонов: {player.trains} | Очков: {player.points}", 
               fontsize=12, ha='center')
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()
        
        return buf.read()