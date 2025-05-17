import wikipedia
import sympy
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging 

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Устанавливаем язык Википедии
wikipedia.set_lang("ru")
logging.info('set language for wiki executed')
# Функция для решения математических выражений
def solve_math(query):
    try:
        query = query.lower().strip()

        # Обработка "корень из X" и "квадратный корень из X"
        if "корень из" in query or "квадратный корень из" in query:
            # Извлекаем часть после ключевой фразы
            for phrase in ["квадратный корень из", "корень из"]:
                if phrase in query:
                    number_str = query.split(phrase, 1)[1].strip()
                    break

            # Проверяем, можно ли превратить в число
            try:
                number = float(number_str)
            except ValueError:
                return f"Не удалось распознать число в запросе: `{number_str}`"

            expr = sympy.sqrt(number)
            return f"Корень из {number} равен: `{expr.evalf()}`"

        # Обычное математическое выражение
        expr = sympy.sympify(query)
        result = expr.evalf()
        logging.info("function solve_math executed")
        return f"Результат: `{result}`"
    except sympy.SympifyError as e:
        logging.error(f'Error : {e}')
        return None

# Основная обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    # Сначала проверяем, не является ли сообщение математическим выражением
    math_response = solve_math(query)
    if math_response:
        await update.message.reply_text(math_response, parse_mode='Markdown')
        return

    # Если нет — ищем в Википедии
    try:
        summary = wikipedia.summary(query)
        page = wikipedia.page(query)
        response = f"{summary}\n\n🔗 [Читать больше]({page.url})"
    except wikipedia.exceptions.DisambiguationError as e:
        response = "Уточните ваш запрос. Найдено несколько вариантов:"
        for option in e.options[:5]:
            response += f"\n- {option}"
    except wikipedia.exceptions.PageError:
        response = "Статья не найдена. Попробуйте изменить запрос."

    await update.message.reply_text(response, parse_mode='Markdown')

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши мне любое слово или математический пример — я помогу!"
    )
    logging.info('Command start has executed')

# Главная функция запуска
def main():
    TOKEN = '7702901883:AAGael0VR9Z0-bW7mNQIVMOa4DHwxganHFw'
    logging.info('constatns has initialized')
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info('Telegramm bot has activated')
    application.run_polling()

if __name__ == '__main__':
    main()