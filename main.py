import wikipedia
import sympy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
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
            for phrase in ["квадратный корень из", "корень из"]:
                if phrase in query:
                    number_str = query.split(phrase, 1)[1].strip()
                    break

            try:
                number = float(number_str)
            except ValueError:
                return f"Не удалось распознать число в запросе: `{number_str}`"

            expr = sympy.sqrt(number)
            return f"Корень из {number} равен: `{expr.evalf()}`"

        # Проверяем, содержит ли запрос математические операторы
        if not any(op in query for op in ['+', '-', '*', '/', '^', 'sqrt']):
            # Если нет операторов, это не математическое выражение
            return None

        # Обычное математическое выражение
        expr = sympy.sympify(query)
        result = expr.evalf()
        logging.info("function solve_math executed")
        return f"Результат: `{result}`"

    except sympy.SympifyError as e:
        logging.error(f'Error : {e}')
        return None

# Обработчик кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_option = query.data
    await query.answer()

    try:
        summary = wikipedia.summary(selected_option)
        page = wikipedia.page(selected_option)
        response = f"{summary}\n\n🔗 [Читать больше]({page.url})"
        await query.edit_message_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка при выборе варианта: {e}")
        await query.edit_message_text("Произошла ошибка при обработке выбора. Попробуйте ещё раз.")

# Основная обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    logger.info(f"Получен запрос: {query}")

    if not query:
        await update.message.reply_text("Сообщение пустое.")
        return

    try:
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
            # Если запрос неоднозначный
            options = e.options[:5]
            response = "Уточните ваш запрос. Найдено несколько вариантов:\n"
            for i, option in enumerate(options, start=1):
                response += f"\n{i}. {option}"
            # Создаем кнопки
            keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(response, reply_markup=reply_markup)
            return
        except wikipedia.exceptions.PageError:
            response = "Статья не найдена в Википедии. Попробуйте изменить запрос."
        except Exception as e:
            logger.error(f"Ошибка при работе с Wikipedia: {e}")
            response = "Произошла ошибка при поиске информации. Попробуйте позже."

        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
        await update.message.reply_text("Произошла внутренняя ошибка. Попробуйте ещё раз.")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши мне любое слово или математический пример — я помогу!"
    )
    logging.info('Command start has executed')

# Главная функция запуска
def main():
    TOKEN = '7702901883:AAGael0VR9Z0-bW7mNQIVMOa4DHwxganHFw'
    logging.info('constants has initialized')
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))  # <-- После всех остальных

    logging.info('Telegram bot has activated')
    application.run_polling()

if __name__ == '__main__':
    main()