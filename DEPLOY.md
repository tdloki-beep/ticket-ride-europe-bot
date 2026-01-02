# 🚀 Деплой Ticket to Ride Europe Bot

## Быстрый деплой на Render (рекомендуется)

### Шаг 1: Подготовка
1. Убедитесь, что у вас есть:
   - Аккаунт на GitHub
   - Токен бота от @BotFather

### Шаг 2: Загрузка на GitHub
```bash
# Создайте новый репозиторий на GitHub
# Затем выполните:
git init
git add .
git commit -m "Ticket to Ride Europe Bot"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Шаг 3: Деплой на Render
1. Перейдите на https://render.com
2. Зарегистрируйтесь или войдите
3. Нажмите "New" → "Web Service"
4. Выберите "Build and deploy from a Git repository"
5. Настройте:
   - **Name**: ticket-ride-europe-bot
   - **Environment**: Python
   - **Build Command**: pip install -r requirements.txt
   - **Start Command**: python run_bot.py
   - **Instance Type**: Free

6. В разделе "Environment" добавьте переменную:
   - **Key**: BOT_TOKEN
   - **Value**: Ваш токен от @BotFather

7. Нажмите "Create Web Service"

### Готово! 🎉
Бот будет автоматически развернут и запущен.

---

## Альтернативные варианты

### Railway (ещё проще)
1. railway.app
2. New Project → Deploy from GitHub
3. Выберите репозиторий
4. Добавьте переменную BOT_TOKEN
5. Deploy

### Heroku
```bash
# Установите Heroku CLI
heroku login
heroku create your-bot-name
heroku config:set BOT_TOKEN=YOUR_TOKEN
git push heroku main
```

### PythonAnywhere
1. pythonanywhere.com
2. Upload files
3. pip install -r requirements.txt --user
4. Create scheduled task
5. Set environment variable

---

## 📱 После деплоя

1. Найдите бота в Telegram по имени
2. Напишите `/start`
3. Создайте игру: `/newgame`
4. Добавьте бота: `/bot`
5. Начните игру: `/startgame`

## 🎮 Приятной игры!

Проблемы? Проверьте:
- Логи на платформе деплоя
- Токен бота корректный
- Бот добавлен в группу или чат

---

**Создано с ❤️ для Ticket to Ride: Europe**