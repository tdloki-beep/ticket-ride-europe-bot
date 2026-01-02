#!/usr/bin/env python3
"""
Автоматический деплой на Render
"""

import os
import sys
import json
import subprocess

def deploy_to_render():
    """Деплой на Render через их CLI"""
    
    print("🚀 Деплой на Render")
    print("=" * 50)
    
    # Проверяем наличие Render CLI
    try:
        result = subprocess.run(['render', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
        print("✅ Render CLI найден")
    except FileNotFoundError:
        print("❌ Render CLI не найден")
        print("Установите Render CLI: https://render.com/docs/cli")
        print("Или используйте веб-интерфейс: https://render.com")
        return False
    
    # Проверяем токен
    if 'BOT_TOKEN' not in os.environ:
        print("❌ BOT_TOKEN не установлен")
        print("Установите переменную окружения BOT_TOKEN")
        return False
    
    print("✅ BOT_TOKEN найден")
    
    # Создаем render.yaml
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "ticket-ride-europe-bot",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python run_bot.py",
                "envVars": [
                    {
                        "key": "BOT_TOKEN",
                        "value": os.environ['BOT_TOKEN']
                    }
                ],
                "plan": "free"
            }
        ]
    }
    
    with open('render.yaml', 'w') as f:
        json.dump(render_config, f, indent=2)
    
    print("✅ Создан render.yaml")
    
    # Инициализируем Git, если нужно
    if not os.path.exists('.git'):
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Initial commit'])
        print("✅ Инициализирован Git репозиторий")
    
    print("\n📋 Что дальше:")
    print("1. Загрузите код на GitHub")
    print("2. На render.com создайте новый Web Service")
    print("3. Выберите 'Deploy from Git Repository'")
    print("4. Укажите ваш GitHub репозиторий")
    print("5. Render автоматически развернет бота")
    
    print("\n🎉 Готово!")
    return True

def create_github_repo():
    """Создание GitHub репозитория"""
    
    print("\n📁 Создание GitHub репозитория")
    
    # Проверяем GitHub CLI
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        print("✅ GitHub CLI найден")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ GitHub CLI не найден")
        print("Установите: https://cli.github.com/")
        return False
    
    # Спрашиваем название репозитория
    repo_name = input("Введите название репозитория (ticket-ride-europe-bot): ").strip()
    if not repo_name:
        repo_name = "ticket-ride-europe-bot"
    
    # Создаем репозиторий
    try:
        result = subprocess.run(
            ['gh', 'repo', 'create', repo_name, '--private', '--source', '.'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Репозиторий создан: {result.stdout.strip()}")
            
            # Пушим код
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', 'Initial commit'])
            subprocess.run(['git', 'push', '-u', 'origin', 'main'])
            print("✅ Код загружен на GitHub")
            
            return True
        else:
            print(f"❌ Ошибка создания репозитория: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("Ticket to Ride Europe Bot - Автоматический деплой")
    print("=" * 55)
    print()
    
    # Меню
    print("Выберите действие:")
    print("1. Подготовить для Render (создать render.yaml)")
    print("2. Создать GitHub репозиторий")
    print("3. Полная инструкция по деплою")
    print()
    
    choice = input("Ваш выбор (1-3): ").strip()
    
    if choice == "1":
        deploy_to_render()
    elif choice == "2":
        create_github_repo()
    elif choice == "3":
        print("\n📖 Полная инструкция:")
        print("1. Создайте бота в @BotFather и получите токен")
        print("2. Установите токен: export BOT_TOKEN=your_token")
        print("3. Создайте GitHub репозиторий (опция 2)")
        print("4. Подготовьте для Render (опция 1)")
        print("5. На render.com создайте Web Service из GitHub")
        print("6. Выберите ваш репозиторий")
        print("7. Deploy!")
    else:
        print("❌ Неверный выбор")