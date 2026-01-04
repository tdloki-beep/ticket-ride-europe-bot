#!/bin/bash

# Настройка Git
git config --global user.name "tdloki-beep"
git config --global user.email "td_loki@mail.ru"

# Создание новой ветки с исправлениями
git checkout -b fix-syntax-errors

# Добавление всех файлов
git add .

# Коммит с описанием изменений
git commit -m "Fix syntax errors in f-strings

- Fixed f-string backslash issue in status command
- Updated requirements for better compatibility
- Added error handling for edge cases"

# Пуш изменений
echo "Pushing to GitHub..."
git push origin fix-syntax-errors

echo "✅ Изменения загружены на GitHub"
echo "Создайте Pull Request на GitHub для merge в main ветку"
