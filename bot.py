import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8279994734:AAFytYh9IGtDYOhajQ8U6ApewGy8gbnsv9g"
ADMIN_ID = 5920598476

DATA_FILE = "college_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ratings": {}, "user_ratings": {}}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

# ========== СТУДЕНТЫ СО СМАЙЛИКАМИ (37) ==========
STUDENTS = [
    "👩‍🏫 Абалбекова Алия",
    "💃🏻 Акунова Айара",
    "🤓 Акылбеков Сейитбек",
    "😴 Алымкулов Марлен",
    "😇 Амиракулова Айлун",
    "🤪 Асатиллоева Зарема",
    "🎒 Аширбаев Бектур",
    "🐻 Байдылдаев Мирлан",
    "🤠 Балтабаев Нурислам",
    "🍩 Батырбекова Алия",
    "🧚‍♂️ Джумашалиева Аиша",
    "😂 Жанышбеков Нурел",
    "👑 Зарылбек Чингиз",
    "😜 Исламбеков Самат",
    "🪪 Кавальчук Григорий",
    "🌼 Кадырова Аида",
    "🔥💪😎 Касымбеков Арсен",
    "🏋️ Майрамбеков Нурэл",
    "😎 Манарбеков Эльдар",
    "💏🏻 Мисиров Кутман",
    "🚬 Мищенко Максим",
    "👯 Молдосанов Даниэл",
    "🎀 Муканбетова Амина",
    "💇‍♂️ Назаров Ырыскелди",
    "⚽ Нуралиев Алинур",
    "🙅‍♀️ Нурланова Айдана",
    "🎮 Рахматиллаев Актилек",
    "🤫 Сабыров Эмилбек",
    "👴 Сайфидинов Бактилек",
    "☠️ Салыбаева Розалия",
    "📈 Сулайманкулов Байдоолот",
    "🤪 Таалайбеков Калэл",
    "🚬 Тележников Руслан",
    "🍩 Толкунбекова Толгонай",
    "🎴 Туланов Эмир",
    "🚲 Тургунбаев Бакы",
    "📏 Ырысбеков Саламат"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⭐ Оценить", callback_data="rate")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("👑 Админ", callback_data="admin")]
    ]
    await update.message.reply_text("🎓 Анонимный бот колледжа", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    
    # Главное меню "Оценить" → список студентов
    if query.data == "rate":
        keyboard = [[InlineKeyboardButton(s, callback_data=f"student_{s}")] for s in STUDENTS]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main")])
        await query.message.edit_text("👨‍🎓 Выбери одногруппника:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Выбрали студента → проверяем, есть ли уже оценка
    elif query.data.startswith("student_"):
        name = query.data.replace("student_", "")
        
        # Если уже оценил
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old_score = data["user_ratings"][name][user_id]
            keyboard = [
                [InlineKeyboardButton(f"✏️ Изменить ({old_score})", callback_data=f"change_{name}")],
                [InlineKeyboardButton(f"🗑 Удалить", callback_data=f"delete_{name}")],
                [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
            ]
            await query.message.edit_text(f"⚠️ Твоя оценка для {name}: {old_score}/10", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        # Если нет оценки → показываем кнопки 1–10
        keyboard = [
            [InlineKeyboardButton("1", callback_data=f"score_{name}_1"), InlineKeyboardButton("2", callback_data=f"score_{name}_2"), InlineKeyboardButton("3", callback_data=f"score_{name}_3"), InlineKeyboardButton("4", callback_data=f"score_{name}_4"), InlineKeyboardButton("5", callback_data=f"score_{name}_5")],
            [InlineKeyboardButton("6", callback_data=f"score_{name}_6"), InlineKeyboardButton("7", callback_data=f"score_{name}_7"), InlineKeyboardButton("8", callback_data=f"score_{name}_8"), InlineKeyboardButton("9", callback_data=f"score_{name}_9"), InlineKeyboardButton("10", callback_data=f"score_{name}_10")],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"⭐ Оцени {name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Сохраняем новую оценку
    elif query.data.startswith("score_"):
        parts = query.data.split("_")
        name = parts[1]
        score = int(parts[2])
        
        # Повторная проверка
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            await query.message.edit_text("❌ Ты уже оценил этого человека. Используй «Изменить» или «Удалить».")
            return
        
        if name not in data["ratings"]:
            data["ratings"][name] = []
        if name not in data["user_ratings"]:
            data["user_ratings"][name] = {}
        
        data["ratings"][name].append(score)
        data["user_ratings"][name][user_id] = score
        save_data()
        
        keyboard = [
            [InlineKeyboardButton("⭐ Оценить другого", callback_data="rate")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main")]
        ]
        await query.message.edit_text(f"✅ Оценка для {name}: {score}/10 сохранена!", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Изменение оценки
    elif query.data.startswith("change_"):
        name = query.data.replace("change_", "")
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()
        
        keyboard = [
            [InlineKeyboardButton("1", callback_data=f"score_{name}_1"), InlineKeyboardButton("2", callback_data=f"score_{name}_2"), InlineKeyboardButton("3", callback_data=f"score_{name}_3"), InlineKeyboardButton("4", callback_data=f"score_{name}_4"), InlineKeyboardButton("5", callback_data=f"score_{name}_5")],
            [InlineKeyboardButton("6", callback_data=f"score_{name}_6"), InlineKeyboardButton("7", callback_data=f"score_{name}_7"), InlineKeyboardButton("8", callback_data=f"score_{name}_8"), InlineKeyboardButton("9", callback_data=f"score_{name}_9"), InlineKeyboardButton("10", callback_data=f"score_{name}_10")],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"✏️ Новая оценка для {name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Удаление оценки
    elif query.data.startswith("delete_"):
        name = query.data.replace("delete_", "")
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()
            await query.message.edit_text(f"🗑 Оценка для {name} ({old}/10) удалена")
        else:
            await query.message.edit_text("❌ Оценка не найдена")
    
    # Статистика (рейтинг)
    elif query.data == "stats":
        stats = []
        for s in STUDENTS:
            scores = data["ratings"].get(s, [])
            if scores:
                avg = sum(scores) / len(scores)
                stats.append((s, avg, len(scores)))
        stats.sort(key=lambda x: x[1], reverse=True)
        
        if not stats:
            text = "📊 Пока нет оценок"
        else:
            text = "📊 Рейтинг одногруппников:\n\n"
            for i, (name, avg, cnt) in enumerate(stats, 1):
                medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i, f"{i}.")
                text += f"{medal} {name} — {avg:.1f}/10 ({cnt})\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # Админ-панель
    elif query.data == "admin":
        if update.effective_user.id != ADMIN_ID:
            await query.message.edit_text("❌ Нет доступа")
            return
        total = sum(len(v) for v in data["ratings"].values())
        await query.message.edit_text(f"👑 Админ\nОценок: {total}")
    
    # Назад в главное меню
    elif query.data == "main":
        keyboard = [
            [InlineKeyboardButton("⭐ Оценить", callback_data="rate")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("👑 Админ", callback_data="admin")]
        ]
        await query.message.edit_text("🎓 Анонимный бот колледжа", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Бот с ограничениями и смайликами запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()