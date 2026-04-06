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
    "🚬 Максим", "👯 Даниэл", "🎀 Амина", "💇‍♂️ Ырыскелди", "⚽ Алинур",
    "👩🏻‍💼 Айдана", "🎮 Актилек", "🤫 Эмилбек", "👴 Бактилек", "☠️ Розалия",
    "📈 Байдоолот", "🤪 Калэл", "🚬 Руслан", "🍩 Толгонай", "🎴 Эмир",
    "🚲 Бакы", "📏 Саламат"
]

def get_user_name(update):
    user = update.effective_user
    return user.first_name or user.username or str(user.id)

def log_action(update, target, score):
    user_name = get_user_name(update)
    data["history"].append({
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
    
    if query.data == "rate":
        keyboard = [[InlineKeyboardButton(s, callback_data=f"student_{s}")] for s in STUDENTS]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main")])
        await query.message.edit_text("👨‍🎓 Выбери одногруппника:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data.startswith("student_"):
        name = query.data.replace("student_", "")
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            keyboard = [
                [InlineKeyboardButton(f"✏️ Изменить ({old})", callback_data=f"change_{name}")],
                [InlineKeyboardButton("🗑 Удалить", callback_data=f"delete_{name}")],
                [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
            ]
            await query.message.edit_text(f"⚠️ Твоя оценка {name}: {old}/10", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(1,6)],
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(6,11)],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"⭐ Оцени {name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data.startswith("score_"):
        parts = query.data.split("_")
        name = parts[1]
        score = int(parts[2])
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            await query.message.edit_text("❌ Уже оценил")
            return
        if name not in data["ratings"]:
            data["ratings"][name] = []
        if name not in data["user_ratings"]:
            data["user_ratings"][name] = {}
        data["ratings"][name].append(score)
        data["user_ratings"][name][user_id] = score
        log_action(update, name, score)
        save_data()
        keyboard = [
            [InlineKeyboardButton("⭐ Ещё", callback_data="rate")],
            [InlineKeyboardButton("🏠 Главное", callback_data="main")]
        ]
        await query.message.edit_text(f"✅ {name} — {score}/10", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data.startswith("change_"):
        name = query.data.replace("change_", "")
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()
        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(1,6)],
            [InlineKeyboardButton(str(i), callback_data=f"score_{name}_{i}") for i in range(6,11)],
            [InlineKeyboardButton("🔙 Назад", callback_data="rate")]
        ]
        await query.message.edit_text(f"✏️ Новая оценка {name}:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data.startswith("delete_"):
        name = query.data.replace("delete_", "")
        if name in data["user_ratings"] and user_id in data["user_ratings"][name]:
            old = data["user_ratings"][name][user_id]
            data["ratings"][name].remove(old)
            del data["user_ratings"][name][user_id]
            save_data()
            await query.message.edit_text(f"🗑 Оценка {name} удалена")
        else:
            await query.message.edit_text("❌ Ошибка")
    
    elif query.data == "stats":
        stats = []
        for s in STUDENTS:
            scores = data["ratings"].get(s, [])
            if scores:
                avg = sum(scores)/len(scores)
                stats.append((s, avg, len(scores)))
        stats.sort(key=lambda x: (x[1], x[2]), reverse=True)
        if not stats:
            text = "📊 Нет оценок"
        else:
            text = "📊 Рейтинг одногруппников:\n\n"
            for i, (name, avg, cnt) in enumerate(stats, 1):
                medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i, f"{i}.")
                text += f"{medal} {name} — {avg:.1f}/10 ({cnt} оценок)\n"
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "admin":
        if update.effective_user.id != ADMIN_ID:
            await query.message.edit_text("❌ Нет доступа")
            return
        context.user_data["admin_page"] = 0
        await show_admin_page(update, context)
    
    elif query.data.startswith("admin_page_"):
        if update.effective_user.id != ADMIN_ID:
            await query.message.edit_text("❌ Нет доступа")
            return
        page = int(query.data.split("_")[2])
        context.user_data["admin_page"] = page
        await show_admin_page(update, context)
    
    elif query.data == "main":
        keyboard = [
            [InlineKeyboardButton("⭐ Оценить", callback_data="rate")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
            [InlineKeyboardButton("👑 Админ", callback_data="admin")]
        ]
        await query.message.edit_text("🎓 Анонимный бот колледжа", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_admin_page(update, context):
    page = context.user_data.get("admin_page", 0)
    history = data["history"][::-1]  # новые сверху
    total = len(history)
    per_page = 10
    start = page * per_page
    end = start + per_page
    items = history[start:end]
    
    if not items:
        text = "📜 История действий пуста"
    else:
        text = f"📜 Последние действия (страница {page+1}/{(total-1)//per_page + 1})\n\n"
        for h in items:
            text += f"👤 {h['user']} → {h['target']} → {h['score']}/10\n"
    
    keyboard = []
    if start > 0:
        keyboard.append(InlineKeyboardButton("◀️ Назад", callback_data=f"admin_page_{page-1}"))
    if end < total:
        keyboard.append(InlineKeyboardButton("Вперёд ▶️", callback_data=f"admin_page_{page+1}"))
    keyboard.append([InlineKeyboardButton("🔙 Главное меню", callback_data="main")])
    
    await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("✅ Бот с админ-историей запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()