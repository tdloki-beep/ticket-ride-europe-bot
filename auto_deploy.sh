#!/bin/bash

# Автоматический деплой Ticket to Ride Europe Bot

echo "🚀 Автоматический деплой бота"
echo "============================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверка наличия Git
if ! command -v git &> /dev/null; then
    log_error "Git не установлен!"
    log_info "Установите Git: https://git-scm.com/downloads"
    exit 1
fi

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Укажите путь к папке с проектом!"
    log_info "Использование: $0 /путь/к/проекту"
    exit 1
fi

PROJECT_DIR="$1"

# Проверка существования папки
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Папка $PROJECT_DIR не существует!"
    exit 1
fi

cd "$PROJECT_DIR"

log_info "Работаем в папке: $(pwd)"

# Проверка существования Git репозитория
if [ ! -d ".git" ]; then
    log_warning "Git репозиторий не найден, инициализируем..."
    git init
    git remote add origin https://github.com/tdloki-beep/ticket-ride-europe-bot.git
fi

# Проверка синтаксиса Python
log_info "Проверка синтаксиса Python..."
if python -m py_compile bot.py 2>/dev/null; then
    log_info "Синтаксис Python - OK"
else
    log_error "Ошибка синтаксиса Python!"
    log_info "Проверьте файл bot.py на ошибки"
    exit 1
fi

# Проверка requirements.txt
if [ ! -f "requirements.txt" ]; then
    log_error "Файл requirements.txt не найден!"
    exit 1
fi

log_info "requirements.txt - OK"

# Настройка Git
log_info "Настройка Git..."
git config user.name "tdloki-beep" || true
git config user.email "td_loki@mail.ru" || true

# Проверка изменений
if git diff --quiet && git diff --cached --quiet; then
    log_warning "Нет изменений для коммита"
    log_info "Добавьте изменения в файлы и запустите скрипт снова"
    exit 0
fi

# Создание новой ветки
BRANCH_NAME="fix-$(date +%Y%m%d-%H%M%S)"
log_info "Создание ветки $BRANCH_NAME..."
git checkout -b "$BRANCH_NAME"

# Добавление файлов
log_info "Добавление файлов..."
git add .

# Создание коммита
COMMIT_MSG="Fix syntax errors and improve compatibility

- Fixed f-string backslash issue
- Updated requirements for better compatibility
- Added error handling"

git commit -m "$COMMIT_MSG"

# Проверка аутентификации
log_info "Проверка аутентификации GitHub..."
if gh auth status 2>/dev/null; then
    log_info "GitHub CLI аутентифицирован"
    
    # Пуш через GitHub CLI
    log_info "Загрузка изменений через GitHub CLI..."
    if git push origin "$BRANCH_NAME"; then
        log_info "✅ Изменения загружены на GitHub!"
        log_info "Создайте Pull Request на GitHub для merge в main ветку"
    else
        log_error "Ошибка при загрузке через GitHub CLI"
        exit 1
    fi
else
    log_warning "GitHub CLI не найден или не аутентифицирован"
    log_info "Используем стандартный Git..."
    
    # Проверка remote URL
    if git remote get-url origin | grep -q "https://"; then
        log_info "Используется HTTPS аутентификация"
        log_warning "Вам может потребоваться ввести Personal Access Token"
    fi
    
    # Пуш через Git
    if git push origin "$BRANCH_NAME"; then
        log_info "✅ Изменения загружены на GitHub!"
    else
        log_error "Ошибка при загрузке!"
        log_info "Проверьте аутентификацию GitHub"
        exit 1
    fi
fi

# Информация о следующих шагах
echo ""
echo "🎉 Деплой завершен!"
echo "==================="
echo ""
echo "Что дальше:"
echo "1. Перейдите на GitHub.com"
echo "2. Создайте Pull Request из ветки $BRANCH_NAME в main"
echo "3. Render автоматически пересоберёт проект"
echo "4. Через 2-3 минуты бот будет запущен"
echo ""
echo "Проверка статуса на Render:"
echo "- Перейдите на https://dashboard.render.com"
echo "- Найдите ваш сервис"
echo "- Проверьте статус 'Deployed'"
echo ""
echo "Проверка работы бота:"
echo "- Найдите бота в Telegram"
echo "- Напишите /start"
echo "- Если бот отвечает - всё работает! 🎉"