# 🚀 Быстрый старт - Ticket to Ride Europe Bot

## Вариант 1: Локальный запуск (2 минуты)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Получите токен у @BotFather в Telegram
# 3. Создайте файл .env
echo "BOT_TOKEN=ВАШ_ТОКЕН" > .env

# 4. Запустите бота
python start_bot.py
```

## Вариант 2: Docker (5 минут)

```bash
# 1. Создайте файл .env с токеном
echo "BOT_TOKEN=ВАШ_ТОКЕН" > .env

# 2. Запустите через Docker
docker-compose up --build
```

## Вариант 3: Бесплатный хостинг (10 минут)

### Railway (самый простой)
1. Загрузите файлы на GitHub
2. Перейдите на railway.app
3. New Project → Deploy from GitHub
4. Выберите репозиторий
5. Добавьте переменную BOT_TOKEN
6. Нажмите Deploy

### Render
1. Загрузите на GitHub
2. render.com → New → Web Service
3. Выберите GitHub репозиторий
4. Настройте:
   - Environment: Python
   - Build: `pip install -r requirements.txt`
   - Start: `python run_bot.py`
5. Добавьте переменную BOT_TOKEN
6. Deploy

## 🎮 Как играть

1. Найдите бота в Telegram
2. `/start` - начать
3. `/newgame` - создать игру
4. `/join` - присоединиться (другие игроки)
5. `/bot` - добавить AI
6. `/startgame` - начать игру

## 📱 Команды бота

### Основные:
- `/start` - помощь
- `/rules` - правила
- `/newgame` - новая игра
- `/join` - присоединиться
- `/startgame` - начать

### Игровые:
- `/map` - показать карту
- `/hand` - ваши карты
- `/status` - статус игры
- `/draw` - взять карты
- `/claim` - захватить маршрут
- `/routes` - взять маршруты

## 🎯 Особенности

- 🗺 Полная карта Европы (50 городов, 70 маршрутов)
- 🤖 Умный AI с прогнозом ходов
- 🎨 Красивые изображения карты
- 📱 Удобный Telegram интерфейс
- 🆓 Работает на бесплатном хостинге

## 🆘 Проблемы?

1. **Ошибка токена**: Получите реальный токен у @BotFather
2. **Ошибки импорта**: Установите зависимости `pip install -r requirements.txt`
3. **Бот не отвечает**: Проверьте логи на платформе деплоя

## 🎲 Приятной игры!

Создайте бота, добавьте друзей и играйте в Ticket to Ride: Europe прямо в Telegram! 🚂