#!/usr/bin/env python3
"""
Ticket to Ride Europe Bot - Запуск с демонстрацией
"""

import os
import sys
from pathlib import Path

# Цвета для терминала
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_banner():
    """Печать баннера"""
    print(Colors.BLUE + """
  _____      _                   _       _____      _ _ 
 |_   _|    | |                 | |     / ____|    | | |
   | |  ___ | |_ _ __ ___  _ __ | | ___| |     ___ | | |
   | | / _ \| __| '_ ` _ \| '_ \| |/ _ \ |    / _ \| | |
  _| || (_) | |_| | | | | | |_) | |  __/ |___| (_) | | |
 |_____\___/ \__|_| |_| |_| .__/|_|\___|\_____\___/|_|_|
                          | |                           
                          |_|                           
    """)
    print(Colors.YELLOW + "Ticket to Ride: Europe Telegram Bot")
    print(Colors.RESET + "=" * 50)

def check_environment():
    """Проверка окружения"""
    print(Colors.GREEN + "\n🔍 Проверка окружения:" + Colors.RESET)
    
    # Проверяем Python
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Проверяем зависимости
    required_packages = [
        'telegram', 'PIL', 'matplotlib', 'networkx', 'numpy', 'dotenv'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('telegram', 'telegram.ext'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - требуется установка")
            return False
    
    return True

def demo_mode():
    """Демонстрационный режим"""
    print(Colors.YELLOW + "\n🎮 Демонстрационный режим" + Colors.RESET)
    print("=" * 30)
    
    # Импортируем модули для демонстрации
    try:
        from config import CITIES, ROUTES
        from game_state import GameState, Player
        from ai_strategy import AIStrategy
        
        print(f"✅ Загружено {len(CITIES)} городов")
        print(f"✅ Загружено {len(ROUTES)} маршрутов")
        
        # Создаем тестовую игру
        game = GameState(12345)
        game.add_player(1, "Игрок 1")
        game.add_player(2, "🤖 Бот")
        game.players[2].is_bot = True
        
        print(f"✅ Создана тестовая игра с {len(game.players)} игроками")
        
        # Демонстрируем AI
        ai = AIStrategy()
        player = game.players[1]
        player.hand = ['red', 'red', 'blue', 'locomotive']
        
        action, params = ai.decide_next_move(game, player)
        print(f"✅ AI стратегия: {action.value}")
        
        prediction = ai.predict_next_move(game, player)
        print(f"✅ Прогноз хода: {prediction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в демонстрации: {e}")
        return False

def main():
    """Главная функция"""
    print_banner()
    
    # Проверяем окружение
    if not check_environment():
        print(Colors.RED + "\n❌ Не все зависимости установлены" + Colors.RESET)
        print("Установите: pip install -r requirements.txt")
        return
    
    # Демонстрация
    demo_mode()
    
    # Проверяем токен
    bot_token = os.environ.get('BOT_TOKEN', '')
    
    print(Colors.YELLOW + "\n🔑 Проверка токена:" + Colors.RESET)
    if bot_token and bot_token != "123456789:TEST_TOKEN_REPLACE_WITH_REAL":
        print(f"✅ Токен установлен: {bot_token[:10]}...")
        
        # Пытаемся запустить бота
        try:
            from bot import main as bot_main
            print(Colors.GREEN + "\n🚀 Запуск бота..." + Colors.RESET)
            bot_main()
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            
    else:
        print("❌ Тестовый токен установлен")
        print(Colors.YELLOW + "\n💡 Чтобы запустить бота:")
        print("1. Получите токен у @BotFather в Telegram")
        print("2. Установите токен:")
        print("   export BOT_TOKEN=ваш_токен")
        print("3. Запустите снова")
        print(Colors.RESET)
        
        # Предлагаем создать .env файл
        create_env = input("Создать файл .env с токеном? (y/n): ").lower()
        if create_env == 'y':
            token = input("Введите токен: ").strip()
            if token:
                with open('.env', 'w') as f:
                    f.write(f'BOT_TOKEN={token}\n')
                print("✅ Файл .env создан")
            else:
                print("❌ Токен не введен")

if __name__ == "__main__":
    main()