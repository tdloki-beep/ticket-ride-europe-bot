#!/bin/bash

# Скрипт для деплоя Ticket to Ride Europe Bot

echo "🚂 Ticket to Ride Europe Bot Deployment Script"
echo "==============================================="

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env и добавьте туда BOT_TOKEN"
    echo "Пример: BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
    exit 1
fi

# Читаем токен из .env
source .env

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN не установлен в файле .env!"
    exit 1
fi

echo "✅ Токен бота найден"

# Спрашиваем пользователя о способе деплоя
echo ""
echo "Выберите способ деплоя:"
echo "1. Docker (локально)"
echo "2. Railway (рекомендуется)"
echo "3. Render"
echo "4. Heroku"
echo "5. PythonAnywhere"
echo ""
read -p "Ваш выбор (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🐳 Деплой через Docker..."
        
        # Проверяем наличие Docker
        if ! command -v docker-compose &> /dev/null; then
            echo "❌ Docker Compose не установлен!"
            echo "Установите Docker: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        echo "📦 Сборка Docker образа..."
        docker-compose build
        
        echo "🚀 Запуск контейнера..."
        docker-compose up -d
        
        echo "✅ Бот запущен в Docker контейнере!"
        echo "Логи: docker-compose logs -f"
        echo "Остановка: docker-compose down"
        ;;
        
    2)
        echo ""
        echo "🚄 Деплой на Railway..."
        echo ""
        echo "Инструкция по деплою на Railway:"
        echo "1. Перейдите на https://railway.app"
        echo "2. Зарегистрируйтесь или войдите"
        echo "3. Создайте новый проект (New Project)"
        echo "4. Выберите 'Deploy from GitHub repo'"
        echo "5. Подключите этот репозиторий"
        echo "6. В разделе Variables добавьте:"
        echo "   BOT_TOKEN=$BOT_TOKEN"
        echo "7. Нажмите Deploy"
        echo ""
        echo "Railway предоставляет бесплатный хостинг с 500 часами в месяц!"
        ;;
        
    3)
        echo ""
        echo "🎨 Деплой на Render..."
        echo ""
        echo "Инструкция по деплою на Render:"
        echo "1. Перейдите на https://render.com"
        echo "2. Зарегистрируйтесь или войдите"
        echo "3. Выберите 'New' -> 'Web Service'"
        echo "4. Подключите GitHub репозиторий"
        echo "5. Настройте:"
        echo "   - Environment: Python"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python bot.py"
        echo "6. В разделе Environment добавьте:"
        echo "   BOT_TOKEN=$BOT_TOKEN"
        echo "7. Выберите бесплатный план"
        echo "8. Нажмите Create Web Service"
        ;;
        
    4)
        echo ""
        echo "🚀 Деплой на Heroku..."
        
        # Проверяем наличие Heroku CLI
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI не установлен!"
            echo "Установите: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        echo "🔐 Проверка авторизации в Heroku..."
        if ! heroku auth:whoami &> /dev/null; then
            echo "❌ Необходимо войти в Heroku!"
            echo "Выполните: heroku login"
            exit 1
        fi
        
        read -p "Введите название приложения (например, ticket-ride-bot): " app_name
        
        echo "📦 Создание приложения..."
        heroku create $app_name
        
        echo "🔧 Настройка переменных окружения..."
        heroku config:set BOT_TOKEN=$BOT_TOKEN --app $app_name
        
        echo "📤 Загрузка кода..."
        git init
        git add .
        git commit -m "Initial commit"
        heroku git:remote -a $app_name
        git push heroku main
        
        echo "✅ Бот развернут на Heroku!"
        echo "URL: https://$app_name.herokuapp.com"
        ;;
        
    5)
        echo ""
        echo "🐍 Деплой на PythonAnywhere..."
        echo ""
        echo "Инструкция по деплою на PythonAnywhere:"
        echo "1. Перейдите на https://pythonanywhere.com"
        echo "2. Зарегистрируйтесь (есть бесплатный план)"
        echo "3. Перейдите в Files tab"
        echo "4. Загрузите все файлы проекта"
        echo "5. Откройте консоль (Bash)"
        echo "6. Установите зависимости:"
        echo "   pip install -r requirements.txt --user"
        echo "7. Перейдите в Task tab"
        echo "8. Создайте новую задачу:"
        echo "   Command: python /home/yourusername/bot.py"
        echo "9. Установите переменную окружения в Environment variables:"
        echo "   BOT_TOKEN=$BOT_TOKEN"
        echo "10. Запустите задачу"
        ;;
        
    *)
        echo "❌ Неверный выбор!"
        exit 1
        ;;
esac

echo ""
echo "🎉 Готово!"
echo ""
echo "📱 Не забудьте:"
echo "1. Создайте бота в @BotFather"
echo "2. Установите команды бота через @BotFather"
echo "3. Добавьте бота в группу или пишите ему в личку"
echo ""
echo "🎲 Приятной игры в Ticket to Ride: Europe! 🚂"