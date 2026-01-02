import os
import logging
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import BOT_TOKEN, MAX_PLAYERS, MIN_PLAYERS
from game_state import GameState, games
from game_logic import GameLogic
from ai_strategy import AIStrategy
from map_visualizer import MapVisualizer

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Визуализатор карты
map_visualizer = MapVisualizer()

# Стратегия для бота
ai_strategy = AIStrategy(aggression_level=0.7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие и помощь"""
    welcome_text = """
🚂 Добро пожаловать в Ticket to Ride: Europe!

Я - бот для игры в Ticket to Ride. Вот доступные команды:

🎮 *ИГРА*
/newgame - Создать новую игру
/join - Присоединиться к игре
/startgame - Начать игру (только для создателя)
/leave - Покинуть игру

🗺 *КАРТА*
/map - Показать карту
/hand - Показать свои карты
/status - Статус игры

🤖 *БОТ*
/bot - Добавить бота в игру

📖 *ПРАВИЛА*
/rules - Правила игры

Нажмите /newgame чтобы начать!
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать новую игру"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Проверяем, есть ли уже игра
    if chat_id in games:
        await update.message.reply_text("❌ В этом чате уже есть активная игра!")
        return
    
    # Создаем новую игру
    game = GameState(chat_id)
    games[chat_id] = game
    
    # Добавляем создателя
    game.add_player(user_id, user_name)
    
    await update.message.reply_text(
        f"🎮 Новая игра создана!\n\n"
        f"Создатель: {user_name}\n"
        f"Игроков: 1/{MAX_PLAYERS}\n\n"
        f"Ожидаем других игроков...\n"
        f"Используйте /join чтобы присоединиться!"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Присоединиться к игре"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Проверяем, есть ли игра
    if chat_id not in games:
        await update.message.reply_text("❌ В этом чате нет активной игры! Создайте игру командой /newgame")
        return
    
    game = games[chat_id]
    
    # Проверяем фазу игры
    if game.phase != "waiting":
        await update.message.reply_text("❌ Игра уже началась! Дождитесь следующей партии.")
        return
    
    # Проверяем, не в игре ли уже игрок
    if user_id in game.players:
        await update.message.reply_text("❌ Вы уже в игре!")
        return
    
    # Проверяем количество игроков
    if len(game.players) >= MAX_PLAYERS:
        await update.message.reply_text("❌ Максимальное количество игроков достигнуто!")
        return
    
    # Добавляем игрока
    game.add_player(user_id, user_name)
    
    # Получаем список игроков
    players_list = "\n".join([f"• {p.name}" for p in game.players.values()])
    
    await update.message.reply_text(
        f"✅ {user_name} присоединился к игре!\n\n"
        f"Игроков: {len(game.players)}/{MAX_PLAYERS}\n\n"
        f"Текущие игроки:\n{players_list}"
    )

async def startgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начать игру"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Проверяем, есть ли игра
    if chat_id not in games:
        await update.message.reply_text("❌ В этом чате нет активной игры!")
        return
    
    game = games[chat_id]
    
    # Проверяем, является ли пользователь создателем
    creator_id = list(game.players.keys())[0]
    if user_id != creator_id:
        await update.message.reply_text("❌ Только создатель игры может начать игру!")
        return
    
    # Проверяем количество игроков
    if len(game.players) < MIN_PLAYERS:
        await update.message.reply_text(f"❌ Минимальное количество игроков: {MIN_PLAYERS}")
        return
    
    # Начинаем игру
    success = game.start_game()
    if not success:
        await update.message.reply_text("❌ Не удалось начать игру!")
        return
    
    # Получаем текущего игрока
    current_player = game.get_current_player()
    
    # Отправляем карту
    map_image = map_visualizer.create_map_image(game)
    await context.bot.send_photo(chat_id=chat_id, photo=map_image, 
                               caption="🗺 Игра началась! Вот карта Европы")
    
    # Информируем о начале игры
    await update.message.reply_text(
        f"🎲 ИГРА НАЧАЛАСЬ! 🎲\n\n"
        f"Первый ходит: {current_player.name}\n\n"
        f"Используйте команды:\n"
        f"/draw - Взять карты\n"
        f"/claim - Захватить маршрут\n"
        f"/routes - Взять карты маршрутов\n"
        f"/hand - Посмотреть свои карты\n"
        f"/map - Посмотреть карту"
    )

async def map_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать карту"""
    chat_id = update.effective_chat.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    # Создаем и отправляем изображение карты
    map_image = map_visualizer.create_map_image(game)
    await context.bot.send_photo(chat_id=chat_id, photo=map_image,
                               caption="🗺 Текущее состояние карты Европы")

async def hand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать карты игрока"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    if user_id not in game.players:
        await update.message.reply_text("❌ Вы не участвуете в игре!")
        return
    
    player = game.players[user_id]
    
    # Создаем изображение карт
    hand_image = map_visualizer.create_player_hand_image(player)
    
    # Формируем текстовую информацию
    color_names = {
        'red': '🔴 Красный',
        'blue': '🔵 Синий',
        'green': '🟢 Зеленый',
        'yellow': '🟡 Желтый',
        'purple': '🟣 Фиолетовый',
        'black': '⚫ Черный',
        'white': '⚪ Белый',
        'orange': '🟠 Оранжевый',
        'locomotive': '🚂 Локомотив'
    }
    
    # Подсчитываем карты
    color_counts = {}
    for card in player.hand:
        color_counts[card] = color_counts.get(card, 0) + 1
    
    hand_text = f"🎴 *Ваши карты* ({len(player.hand)} шт.):\n\n"
    for color, count in color_counts.items():
        color_name = color_names.get(color, color)
        hand_text += f"{color_name}: {count}\n"
    
    hand_text += f"\n🚂 Вагонов: {player.trains}\n"
    hand_text += f"🎯 Очков: {player.points}\n"
    hand_text += f"📋 Карт маршрутов: {len(player.routes)}"
    
    await context.bot.send_photo(chat_id=chat_id, photo=hand_image,
                               caption=hand_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статус игры"""
    chat_id = update.effective_chat.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    # Формируем информацию об игроках
    players_info = []
    for player_id, player in game.players.items():
        status_icon = "▶️" if player_id == game.current_player_id else "⏸"
        players_info.append(
            f"{status_icon} {player.name}: {player.points} очков ({player.trains} вагонов)"
        )
    
    current_player = game.get_current_player()
    current_player_name = current_player.name if current_player else "Никто"
    
    status_text = f"""
📊 *Статус игры*

🎮 Фаза: {game.phase.value}
🎯 Ходит: {current_player_name}

👥 Игроки:
{"\n".join(players_info)}

🎴 Открытые карты: {len(game.open_cards)}
📚 Колода: {len(game.train_deck)} карт
    """
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Взять карту вагона"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    if game.phase != "playing":
        await update.message.reply_text("❌ Игра еще не началась!")
        return
    
    if user_id not in game.players:
        await update.message.reply_text("❌ Вы не участвуете в игре!")
        return
    
    if user_id != game.current_player_id:
        await update.message.reply_text("❌ Не ваш ход!")
        return
    
    # Создаем клавиатуру для выбора карт
    keyboard = []
    
    # Открытые карты
    for i, card in enumerate(game.open_cards):
        color_emoji = get_color_emoji(card)
        keyboard.append([InlineKeyboardButton(f"{color_emoji} Карта #{i+1}", 
                                            callback_data=f"draw_open_{i}")])
    
    # Карта из колоды
    keyboard.append([InlineKeyboardButton("🎴 Взять из колоды", 
                                        callback_data="draw_deck")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Выберите карту:", reply_markup=reply_markup)

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Захватить маршрут"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    if game.phase != "playing":
        await update.message.reply_text("❌ Игра еще не началась!")
        return
    
    if user_id not in game.players:
        await update.message.reply_text("❌ Вы не участвуете в игре!")
        return
    
    if user_id != game.current_player_id:
        await update.message.reply_text("❌ Не ваш ход!")
        return
    
    player = game.players[user_id]
    
    # Получаем доступные маршруты
    available_routes = GameLogic.get_available_routes(player, game)
    
    if not available_routes:
        await update.message.reply_text("❌ Нет доступных маршрутов для захвата!")
        return
    
    # Создаем клавиатуру для выбора маршрута
    keyboard = []
    for i, route in enumerate(available_routes[:10]):  # Показываем не более 10 маршрутов
        city1, city2, length, color, is_tunnel = route
        color_emoji = get_color_emoji(color)
        keyboard.append([InlineKeyboardButton(
            f"{color_emoji} {city1} - {city2} ({length})", 
            callback_data=f"claim_route_{i}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Выберите маршрут для захвата:", 
                                  reply_markup=reply_markup)

async def routes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Взять карты маршрутов"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Нет активной игры!")
        return
    
    game = games[chat_id]
    
    if game.phase != "playing":
        await update.message.reply_text("❌ Игра еще не началась!")
        return
    
    if user_id not in game.players:
        await update.message.reply_text("❌ Вы не участвуете в игре!")
        return
    
    if user_id != game.current_player_id:
        await update.message.reply_text("❌ Не ваш ход!")
        return
    
    # Берем 3 карты маршрутов
    drawn_routes = GameLogic.draw_route_cards(game.players[user_id], game, count=3)
    
    await update.message.reply_text(
        f"📋 Вы взяли {len(drawn_routes)} карты маршрутов!\n\n"
        f"Теперь у вас {len(game.players[user_id].routes)} карт маршрутов."
    )

async def bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить бота в игру"""
    chat_id = update.effective_chat.id
    
    if chat_id not in games:
        await update.message.reply_text("❌ Сначала создайте игру командой /newgame")
        return
    
    game = games[chat_id]
    
    if game.phase != "waiting":
        await update.message.reply_text("❌ Игра уже началась!")
        return
    
    # Создаем бота
    bot_id = -1  # Специальный ID для бота
    bot_name = "🤖 Бот"
    
    if bot_id in game.players:
        await update.message.reply_text("❌ Бот уже в игре!")
        return
    
    # Добавляем бота
    game.add_player(bot_id, bot_name)
    game.players[bot_id].is_bot = True
    
    await update.message.reply_text("🤖 Бот добавлен в игру!")

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать правила"""
    rules_text = """
📖 *ПРАВИЛА Ticket to Ride: Europe*

🎯 *Цель игры*
Соберите наибольшее количество очков, прокладывая железнодорожные маршруты между городами Европы.

🎴 *Карты*
- Карты вагонов 8 цветов + локомотивы
- Карты маршрутов с указанием городов и очков

🎮 *Ход*
1. Взять 2 карты вагонов (из открытых или колоды)
2. Захватить маршрут (потратив вагоны и карты)
3. Взять карты маршрутов

🏗 *Захват маршрута*
- Потратите карты нужного цвета
- Поставьте свои вагоны на маршрут
- Получите очки за длину маршрута

🚂 *Локомотивы*
- Универсальные карты (заменяют любой цвет)
- Нужны для туннелей и ферри

📋 *Карты маршрутов*
- Показывают, какие города нужно соединить
- Дают дополнительные очки в конце игры

🏁 *Конец игры*
Игра заканчивается, когда у игрока остается 2 или менее вагонов

💰 *Очки*
- За маршруты: 1-15 очков
- За выполненные маршруты: от 5 до 20+ очков
- За длину пути: дополнительные очки
    """
    
    await update.message.reply_text(rules_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    
    if chat_id not in games:
        await query.edit_message_text("❌ Игра не найдена!")
        return
    
    game = games[chat_id]
    
    if user_id not in game.players:
        await query.edit_message_text("❌ Вы не в игре!")
        return
    
    if user_id != game.current_player_id:
        await query.edit_message_text("❌ Не ваш ход!")
        return
    
    data = query.data
    
    # Обработка взятия карт
    if data.startswith("draw_open_"):
        card_index = int(data.split("_")[-1])
        success = GameLogic.draw_train_card(game.players[user_id], game, card_index)
        if success:
            await query.edit_message_text(f"✅ Взята открытая карта!")
            game.next_turn()
    
    elif data == "draw_deck":
        success = GameLogic.draw_train_card(game.players[user_id], game)
        if success:
            await query.edit_message_text(f"✅ Взята карта из колоды!")
            game.next_turn()
    
    # Обработка захвата маршрута
    elif data.startswith("claim_route_"):
        route_index = int(data.split("_")[-1])
        available_routes = GameLogic.get_available_routes(game.players[user_id], game)
        
        if 0 <= route_index < len(available_routes):
            route = available_routes[route_index]
            success = GameLogic.claim_route(game.players[user_id], route, game)
            
            if success:
                city1, city2, length, color, is_tunnel = route
                points = GameLogic.ROUTE_POINTS.get(length, 0)
                await query.edit_message_text(
                    f"✅ Захвачен маршрут {city1} - {city2}!\n"
                    f"Получено {points} очков"
                )
                
                # Проверяем конец игры
                if GameLogic.check_end_game(game):
                    # Подсчитываем финальные очки
                    scores = GameLogic.calculate_final_scores(game)
                    
                    # Формируем результаты
                    results = []
                    for player_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                        player = game.players[player_id]
                        results.append(f"{player.name}: {score} очков")
                    
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🏆 ИГРА ОКОНЧЕНА! 🏆\n\nРезультаты:\n" + "\n".join(results)
                    )
                    
                    # Удаляем игру
                    del games[chat_id]
                else:
                    game.next_turn()
            else:
                await query.edit_message_text("❌ Не удалось захватить маршрут!")

async def bot_move(context: ContextTypes.DEFAULT_TYPE):
    """Автоматический ход бота"""
    job = context.job
    chat_id = job.chat_id
    
    if chat_id not in games:
        return
    
    game = games[chat_id]
    
    # Проверяем, ходит ли бот
    current_player = game.get_current_player()
    if not current_player or not current_player.is_bot:
        return
    
    # Принимаем решение
    action, params = ai_strategy.decide_next_move(game, current_player)
    
    # Выполняем действие
    if action == PlayerAction.CLAIM_ROUTE:
        city1 = params['city1']
        city2 = params['city2']
        route = GameLogic.get_route_by_cities(city1, city2)
        if route:
            GameLogic.claim_route(current_player, route, game)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🤖 Бот захватил маршрут: {city1} - {city2}"
            )
    
    elif action == PlayerAction.DRAW_CARDS:
        if params.get('from_deck'):
            GameLogic.draw_train_card(current_player, game)
            await context.bot.send_message(
                chat_id=chat_id,
                text="🤖 Бот взял карту из колоды"
            )
        else:
            card_index = params.get('card_index', 0)
            GameLogic.draw_train_card(current_player, game, card_index)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🤖 Бот взял открытую карту #{card_index + 1}"
            )
    
    # Следующий ход
    game.next_turn()
    
    # Обновляем карту
    map_image = map_visualizer.create_map_image(game)
    await context.bot.send_photo(chat_id=chat_id, photo=map_image,
                               caption="🗺 Карта после хода бота")

def get_color_emoji(color: str) -> str:
    """Получить эмодзи для цвета"""
    emojis = {
        'red': '🔴',
        'blue': '🔵',
        'green': '🟢',
        'yellow': '🟡',
        'purple': '🟣',
        'black': '⚫',
        'white': '⚪',
        'orange': '🟠',
        'gray': '🔘',
        'locomotive': '🚂'
    }
    return emojis.get(color, '🎴')

def main():
    """Основная функция"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("newgame", newgame))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("startgame", startgame))
    application.add_handler(CommandHandler("map", map_command))
    application.add_handler(CommandHandler("hand", hand))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("draw", draw))
    application.add_handler(CommandHandler("claim", claim))
    application.add_handler(CommandHandler("routes", routes))
    application.add_handler(CommandHandler("bot", bot_command))
    application.add_handler(CommandHandler("rules", rules))
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Запуск бота...")
    application.run_polling()

if __name__ == '__main__':
    main()