#!/usr/bin/env python3
"""
Запуск Ticket to Ride Europe Bot
"""

import os
from flask import Flask
import threading
import time
import sys
from pathlib import Path

# Добавляем текущую директорию в PATH
sys.path.insert(0, str(Path(__file__).parent))

# Устанавливаем тестовый токен (замените на реальный)
TEST_TOKEN = "123456789:TEST_TOKEN_REPLACE_WITH_REAL"

# Если нет переменной окружения, используем тестовый токен
if 'BOT_TOKEN' not in os.environ:
    os.environ['BOT_TOKEN'] = TEST_TOKEN
    print(f"⚠️  Используется тестовый токен: {TEST_TOKEN}")
    print("⚠️  Замените его на реальный токен из @BotFather")
    print()

print("🚂 Ticket to Ride Europe Bot")
print("=" * 40)
print()
print("Для работы бота необходимо:")
print("1. Получить токен у @BotFather в Telegram")
print("2. Установить токен в переменную окружения BOT_TOKEN")
print("3. Убедиться, что все зависимости установлены")
print()

try:
    # Импортируем и запускаем бота
    from bot import main
    
    print("✅ Модули успешно импортированы")
    print("🚀 Запуск бота...")
    print()
    
    # Запускаем основную функцию
    main()
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print()
    print("Установите зависимости:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Ошибка при запуске: {e}")
    sys.exit(1from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK', 200

def run_health_server():
    app.run(host='0.0.0.0', port=8080, debug=False)

# Запускаем health server в отдельном потоке
threading.Thread(target=run_health_server, daemon=True).start()

# Даём время на запуск сервера
time.sleep(2)

)