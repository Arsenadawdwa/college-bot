import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8660740312:AAEPiCLc01IG10PHXJ7Xkv7bx5Y2oD4eF40"
ADMIN_ID = 5920598476

DATA_FILE = "college_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"ratings": {}, "user_ratings": {}, "history": []}
    return {"ratings": {}, "user_ratings": {}, "history": []}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

STUDENTS = [
    "👩‍🏫 Алия", "💃🏻 Айара", "🤓 Сейитбек", "😴 Марлен", "😇 Айлун",
    "🤪 Зарема", "🎒 Бектур", "🐱 Мирлан", "🤠 Нурислам", "🍩 Алия",
    "🌷 Аиша", "😂 Нурел", "👑 Чингиз", "😜 Самат", "🪪 Григорий",
    "👧🏻 Аида", "🔥💪😎 Арсен", "🏋️ Нурэл", "😎 Эльдар", "🦧 Кутман",
    "🏌🏻‍ Максим", "👯 Даниэл", "🎀 Амина", "💇‍♂️ Ырыскелди", "⚽ Алинур",
    "🍣 Айдана", "🎮 Актилек", "🤫 Эмилбек", "👴 Бактилек", "☠️ Розалия",
    "📈 Байдоолот", "🤪 Калэл", "🚬 Руслан", "🍩 Толгонай", "🎴 Эмир",
    "🚲 Бакы", "📏 Саламат"
]

def get_user_name(update):
    user = update.effective_user
    return user.first_name or user.username or str(user.id)

def log_action(update, target, score):
    user_name = get_user_name(update)
    data["history"].insert(0, {
        "user": user_name,
        "target": target,
        "score": score
    })
    save_data()

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
    data_cb = query.data

    if data_cb == "main":
        keyboard = [
            [InlineKeyboardButton("⭐ Оценить", callback_data="rate")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("👑 Админ", callback_data="admin")]
        ]
        await query.message.edit_text("🎓 Анонимный бот колледжа", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb == "rate":
        keyboard = [[InlineKeyboardButton(s, callback_data=f"rate_{s}")] for s in STUDENTS]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main")])
        await query.message.edit_text("👨‍🎓 Выбери одногруппника:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb.startswith("rate_"):
        name = data_cb[5:]
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            keyboard = [
                [InlineKeyboardButton(f"✏️ Изменить ({old})", callback_data=f"change_{name}")],
                [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{name}")],
                [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
            ]
            await query.message.edit_text(f"⚠️ Ты уже оценил {name}: {old}/10", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(1,6)],
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(6,11)],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"⭐ Оцени {name}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb.startswith("score_"):
        _, name, score_str = data_cb.split("_")
        score = int(score_str)

        if name not in data["ratings"]:
            data["ratings"][name] = []
        if name not in data["user_ratings"]:
            data["user_ratings"][name] = {}

        if user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            await query.message.edit_text(f"❌ Ты уже оценил {name}: {old}/10")
            return

        data["ratings"][name].append(score)
        data["user_ratings"][name][user_id] = score
        log_action(update, name, score)
        save_data()

        keyboard = [[InlineKeyboardButton(s, callback_data=f"rate_{s}")] for s in STUDENTS]
        keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main")])
        await query.message.edit_text(f"✅ {name} — {score}/10\n\n👨‍🎓 Выбери следующего:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb.startswith("change_"):
        name = data_cb[7:]
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            if old in data["ratings"][name]:
                data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(1,6)],
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(6,11)],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"✏️ Новая оценка для {name}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb.startswith("delete_"):
        name = data_cb[7:]
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            if old in data["ratings"][name]:
                data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()
            await query.message.edit_text(f"🗑 Оценка для {name} удалена")
        else:
            await query.message.edit_text("❌ Оценка не найдена")

    elif data_cb == "stats":
        stats = []
        for s in STUDENTS:
            scores = data["ratings"].get(s, [])
            if scores:
                avg = sum(scores) / len(scores)
                stats.append((s, avg, len(scores)))

        stats.sort(key=lambda x: (x[1], x[2]), reverse=True)

        if not stats:
            text = "📊 Пока нет оценок"
        else:
            text = "📊 Рейтинг:\n\n"
            for i, (name, avg, cnt) in enumerate(stats, 1):
                text += f"{i}. {name} — {avg:.1f}/10 ({cnt})\n"

        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data_cb == "admin":
        if update.effective_user.id != ADMIN_ID:
            await query.message.edit_text("❌ Нет доступа")
            return
        await show_admin(update, context)

async def show_admin(update, context):
    history = data["history"][:10]

    if not history:
        text = "📜 История пуста"
    else:
        text = "📜 Последние действия:\n\n"
        for h in history:
            text += f"{h['user']} → {h['target']} → {h['score']}/10\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
    await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# 🔥 ГЛАВНОЕ ИСПРАВЛЕНИЕ ТУТ
async def main():
    app = Application.builder().token(TOKEN).build()

    # УБИРАЕТ ОШИБКУ CONFLICT
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Бот запущен!")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())