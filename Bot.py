from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
import pandas as pd
import numpy as np
import asyncio

# Стани для ConversationHandler
REGISTER, WAIT_FOR_NAME, RATINGS = range(3)

# Зберігання даних
experts_data = {}
OBJECTS = ["Об'єкт 1", "Об'єкт 2", "Об'єкт 3", "Об'єкт 4", "Об'єкт 5"]

# Автоматичні дані для підставлення
your_data = {
    "Експерт 1": [5, 4, 1, 3, 4],
    "Експерт 2": [4, 6, 5, 2, 5],
    "Експерт 3": [1, 5, 2, 5, 4],
    "Експерт 4": [5, 4, 5, 1, 6],
    "Експерт 5": [4, 1, 4, 6, 5],
    "Експерт 6": [5, 5, 4, 5, 1],
}



# Оновлені дані з оцінками 1-5 (змінені значення)
your_data_raiting = {
    "Експерт 1": [4, 3, 5, 4, 4],
    "Експерт 2": [3, 4, 5, 3, 5],
    "Експерт 3": [5, 4, 4, 5, 3],
    "Експерт 4": [4, 5, 3, 4, 5],
    "Експерт 5": [3, 5, 4, 5, 4],
    "Експерт 6": [5, 4, 5, 3, 4],
}

async def start(update: Update, context: CallbackContext):
    """Початок взаємодії з ботом."""
    keyboard = [["Підставити мої дані"], ["Ввести вручну"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Вітаємо! Цей бот допоможе провести експертне оцінювання.\n"
        "Виберіть дію:",
        reply_markup=reply_markup
    )
    return REGISTER

async def handle_user_choice(update: Update, context: CallbackContext):
    """Обробляє вибір: підставити дані або ввести вручну."""
    user_choice = update.message.text

    if user_choice == "Підставити мої дані":
        context.user_data['experts_data'] = your_data 
        context.user_data['raiting_data'] = your_data_raiting
        await update.message.reply_text(
            "Ваші дані підставлено! Ви можете переглянути результати за допомогою команди /results.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    elif user_choice == "Ввести вручну":
        await update.message.reply_text("Введіть своє ім'я для реєстрації:", reply_markup=ReplyKeyboardRemove())
        return WAIT_FOR_NAME  

    else:
        # Якщо невідома команда, пропонуємо вибір знову
        keyboard = [["Підставити мої дані"], ["Ввести вручну"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Будь ласка, виберіть одну з доступних опцій:",
            reply_markup=reply_markup
        )
        return REGISTER

async def register_expert(update: Update, context: CallbackContext):
    """Функція для реєстрації експерта та початку введення оцінок."""
    expert_name = update.message.text
    
    # Ініціалізуємо словник даних, якщо його ще немає
    if 'experts_data' not in context.user_data or 'raiting_data' not in context.user_data:
        context.user_data['experts_data'] = {}
        context.user_data['raiting_data'] = {}
    
    # Перевіряємо, чи експерт вже існує
    if expert_name in context.user_data['experts_data'] or expert_name in context.user_data['raiting_data']:
        await update.message.reply_text(
            f"Експерт *{expert_name}* вже зареєстрований. Введіть унікальне ім'я:",
            parse_mode="Markdown"
        )
        return WAIT_FOR_NAME
    
    # Додаємо нового експерта
    context.user_data['current_expert'] = expert_name
    context.user_data['current_object'] = 0
    context.user_data['current_ratings'] = []  # Тимчасове зберігання оцінок

    await update.message.reply_text(
        f"Експерт *{expert_name}* зареєстрований.\n"
        f"Введіть оцінку для {OBJECTS[0]}:",
        parse_mode="Markdown"
    )
    return RATINGS

async def collect_ratings(update: Update, context: CallbackContext):
    """Збір оцінок експерта"""
    i = 0
    data = ["experts_data","raiting_data"]
    while i>2:
        try:
            rating = float(update.message.text)
        except ValueError:
            await update.message.reply_text("Будь ласка, введіть числову оцінку.")
            return RATINGS

        current_index = context.user_data[data[i]]
        context.user_data['current_ratings'].append(rating)

        if current_index + 1 < len(OBJECTS):
            context.user_data[data[i]] += 1
            await update.message.reply_text(
                f"Введіть оцінку для *{OBJECTS[context.user_data[data[i]]]}*:",
                parse_mode="Markdown"
            )
            return RATINGS
        if current_index + 1 < len(OBJECTS):
            context.user_data[data[i]] += 1
            await update.message.reply_text(
                f"Введіть оцінку для *{OBJECTS[context.user_data[data[i]]]}*:",
                parse_mode="Markdown"
            )
            return RATINGS
        else:
            expert_name = context.user_data['current_expert']
            context.user_data[data[i]][expert_name] = context.user_data['current_ratings']
        
            experts_list = "\n".join(context.user_data[data[i]].keys())
            await update.message.reply_text(
                f"Дякуємо! Оцінки для експерта *{expert_name}* збережено.\n"
                f"Зареєстровані експерти:\n{experts_list}\n\n"
                "Ви можете:\n"
                "1. Додати нового експерта (/start)\n"
                "2. Переглянути результати (/results)",
                parse_mode="Markdown"
            )
            i += 1

    return ConversationHandler.END

async def calculate_results(update: Update, context: CallbackContext):
    """Розрахунок та відображення результатів."""
    if 'experts_data' not in context.user_data or not context.user_data['experts_data']:
        await update.message.reply_text("Немає даних для обробки.")
        return

    experts_data = context.user_data['experts_data']
    raiting_data = context.user_data['raiting_data']
    objects = [f"Матеріал {i+1}" for i in range(len(experts_data[next(iter(experts_data))]))]

    # Перевірка на повноту даних
    incomplete = []
    for expert, ratings in experts_data.items():
        if len(ratings) != len(OBJECTS):
            incomplete.append(expert)
    
    if incomplete:
        await update.message.reply_text(
            f"У цих експертів недостатньо оцінок: {', '.join(incomplete)}\n"
            "Будь ласка, завершіть введення оцінок."
        )
        return

    # Перша таблиця: Кількісна оцінка та розраховані значення
    df = pd.DataFrame.from_dict(experts_data, orient='index', columns=objects)
    df.loc['Sum'] = df.sum(axis=0)
    df.loc['Mean'] = df.iloc[:-1].mean(axis=0).round(2)
    total_sum = df.loc['Sum'].sum()
    df.loc['Normalized'] = (df.loc['Sum'] / total_sum).round(2)

    results_table = df.to_string(justify="center")
    await update.message.reply_text(
        f"*Кількісна оцінка та розраховані значення:*\n```\n{results_table}\n```",
        parse_mode="Markdown"
    )

    # Друга таблиця: Рангові оцінки
    objects = [f"Матеріал {i+1}" for i in range(len(raiting_data[next(iter(raiting_data))]))]
    experts = list(raiting_data.keys())

    df_ranks = pd.DataFrame.from_dict(raiting_data, orient='index', columns=objects)
    df_ranks.loc['Sum'] = df_ranks.sum(axis=0)
    sum_scores = df_ranks.loc['Sum']

    def most_frequent_value(column):
        mode_values = column.mode()  # Отримуємо моду (може бути кілька значень)
        return mode_values.iloc[0] if not mode_values.empty else None

    # Додаємо суму повторень для кожного матеріалу
    df_ranks.loc['Найчастіше число'] = df_ranks.apply(most_frequent_value, axis=0)

    # Виведення результатів
    results_ranks = df_ranks.to_string(justify="center")
    await update.message.reply_text(
        f"*Приклад рангової оцінки та розрахованих сумарного та результуючого рангу зразків матеріалів за результатами експертного опитування:*\n```\n{results_ranks}\n```",
        parse_mode="Markdown"
    )

    # Третя таблиця: статистичні показники та довірчий інтервал
    df_stats = pd.DataFrame.from_dict(experts_data, orient='index', columns=objects)
    J = df_stats.shape[0]  # Кількість експертів
    I = df_stats.shape[1]
    means = np.mean(df_stats, axis=0)  
    xmax = np.max(df_stats, axis=0)  
    xmin = np.min(df_stats, axis=0)  

    Var = xmax - xmin 
    print(f"Var: {Var}")

    D = np.zeros(I)
    for i in range(I):
        sum_squares = np.sum((df_stats.iloc[:, i] - means[i])**2) 
        D[i] = sum_squares / (J - 1)  

    sigma = np.sqrt(D)

    V = (D / means) * 100  

    confidence_multiplier = 2.23  
    CI_lower = means - confidence_multiplier * (D / np.sqrt(J))  
    CI_upper = means + confidence_multiplier * (D / np.sqrt(J))  

    for i in range(I):
        df_stats.loc['Var', objects[i]] = Var[i].round(2)
        df_stats.loc['Mean', objects[i]] = means[i].round(2)
        df_stats.loc['D', objects[i]] = D[i].round(2)
        df_stats.loc['σ', objects[i]] = sigma[i].round(2)
        df_stats.loc['V', objects[i]] = f"{V[i].round(0)}%"

    df_stats.loc['Довірчий інтервал'] = "[" + CI_lower.round(2).astype(str) + " ... " + CI_upper.round(2).astype(str) + "]"
    df_stats = df_stats.round(2)

    stats_table_str = df_stats.to_string(index=True, header=True, justify="center")

    await update.message.reply_text(
        f"*Результати експертів та статистичні показники:*\n```\n{stats_table_str}\n```",
        parse_mode="Markdown"
    )

    # Четверта таблиця: Рангова оцінка та коефіцієнти кореляції
    objects = [f"Матеріал {i+1}" for i in range(len(raiting_data[next(iter(raiting_data))]))]
    experts = list(raiting_data.keys())
    J = len(experts)
    I = len(objects)

    df_scores = pd.DataFrame.from_dict(raiting_data, orient='index', columns=objects)

    # Покращена функція для розрахунку кореляції Спірмена
    def calculate_spearman_simple(ranks1, ranks2):
        d_squared = (ranks1 - ranks2) ** 2
        sum_d_squared = np.sum(d_squared)
        n = len(ranks1)
        return 1 - ((6 * sum_d_squared) / (n * (n**2 - 1)))
    
    # Підготовка таблиці для виводу
    result_table = "```\n"
    result_table += f"{'':<10}" + "".join([f"{obj:<12}" for obj in objects]) + "ρ\n"
    result_table += "-" * (10 + 12 * len(objects)) + "\n"

    # Додавання оцінок експертів
    for i, expert in enumerate(experts, 1):
        scores = df_scores.loc[expert].tolist()
        result_table += f"Експерт {i:<3}" + "".join([f"{score:<12}" for score in scores]) + "\n"

    result_table += "-" * (10 + 12 * len(objects)) + "\n"

    # Розрахунок кореляцій для всіх пар
    correlations = []
    for j in range(J):
        for j_prime in range(j + 1, J):
            expert1 = experts[j]
            expert2 = experts[j_prime]
    
            expert1_num = j + 1  # Нумерація експертів з 1
            expert2_num = j_prime + 1

            # Отримуємо ранги для пари експертів
            ranks1 = df_ranks.loc[expert1].astype(float)
            ranks2 = df_ranks.loc[expert2].astype(float)
        
            # Різниця сирих оцінок (для таблиці)
            score_diff = (df_scores.iloc[j] - df_scores.iloc[j_prime]).tolist()
        
            # Розрахунок ρ з використанням рангів
            rho = calculate_spearman_simple(ranks1, ranks2)
            rho = round(rho, 2)
        
            correlations.append({
                'pair': f"a{expert1_num},{expert2_num}",
                'diff': score_diff,
                'rho': rho
            })

    # Додавання результатів кореляції до таблиці
    for corr in correlations:
        diff_str = "".join([f"{val:<12}" for val in corr['diff']])
        result_table += f"{corr['pair']:<10}{diff_str}{corr['rho']:.2f}\n"

    result_table += "```"

    # Відправка результату
    await update.message.reply_text(f"*Рангові оцінки та розрахункові значення рангової кореляції між думками експертів:* {result_table}", parse_mode="Markdown")

    def calculate_concordance(df_ranks):
        J = df_ranks.shape[0]  
        I = df_ranks.shape[1]  
        
        
        S_j = df_ranks.sum(axis=0)
        
        
        S_mean = 0.5 * J * (I + 1)
        
        numerator = 12 * ((S_j - S_mean)**2).sum()
        
        denominator_strict = J**2 * (I**3 - I)
        
        tie_correction = 0
        for expert in df_ranks.index:
            ranks = df_ranks.loc[expert]
            value_counts = ranks.value_counts()
            groups = value_counts[value_counts > 1]
            for count in groups:
                tie_correction += (count**3 - count)
        
        denominator = denominator_strict - J * tie_correction
        
        W = numerator / denominator
        return W

    W = calculate_concordance(df_ranks)
    W_interpretation = "низька" if W < 0.3 else "середня" if W < 0.7 else "висока"

    # Додаємо інтерпретацію результатів
    interpretation_text = f"""
    *Коефіцієнт конкордації W: {W:.3f}* ({W_interpretation} узгодженість)

    *Інтерпретація:*
    - W < 0.3: низька узгодженість думок
    - 0.3 ≤ W < 0.7: середня узгодженість
    - W ≥ 0.7: висока узгодженість

    *Можливі причини {W_interpretation}ої узгодженості:*
    {'- Низькі знання експертів в даній галузі\n - Нечітке розуміння мети оцінки' if W < 0.3 else 
    '- Середній рівень знань експертів\n - Часткове розуміння проблеми' if W < 0.7 else 
    '- Високі знання всіх експертів\n    - Чітке розуміння проблеми'}
    """

    await update.message.reply_text(
        interpretation_text,
        parse_mode="Markdown"
    )


async def cancel(update: Update, context: CallbackContext):
    """Скасування процесу оцінювання"""
    await update.message.reply_text("Операцію скасовано.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def main():
    application = Application.builder().token("******************************************").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGISTER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_choice),
            ],
            WAIT_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register_expert),
            ],
            RATINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_ratings)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("results", calculate_results))
    application.add_handler(CommandHandler("cancel", cancel))

    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())