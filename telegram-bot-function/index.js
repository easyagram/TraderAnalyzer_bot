const { Telegraf } = require('telegraf');
const axios = require('axios'); // Добавим axios для запросов к API

const bot = new Telegraf(process.env.BOT_TOKEN);

// --- Обработчики команд ---
bot.start((ctx) => ctx.reply(`Привет! Я бот для анализа рынка акций Московской биржи.\n` +
    `Доступные команды:\n` +
    `/anomalous_volumes [ticker] - Аномальные объемы\n` +
    `/anomalous_limits [ticker] - Аномальные лимитки\n` +
    `/net_flow [ticker] - Индикатор чистых покупок и продаж\n` +
    `/short_squeeze [ticker] - Индикатор шорт-сквиза\n` +
    `/help - Список команд`));

bot.help((ctx) => ctx.reply(`Доступные команды:\n` +
    `/anomalous_volumes [ticker] - Аномальные объемы\n` +
    `/anomalous_limits [ticker] - Аномальные лимитки\n` +
    `/net_flow [ticker] - Индикатор чистых покупок и продаж\n` +
    `/short_squeeze [ticker] - Индикатор шорт-сквиза`));

// --- Обработчик команды /anomalous_volumes ---
bot.command('anomalous_volumes', async (ctx) => {
    const ticker = ctx.message.text.split(' ')[1];
    if (!ticker) {
        return ctx.reply('Пожалуйста, укажите тикер после команды /anomalous_volumes');
    }

    try {
        const apiUrl = `${process.env.API_URL}/anomalous_volumes?ticker=${ticker}`; // Раскомментируем
        const response = await axios.get(apiUrl);
        const data = response.data;
        ctx.reply(`Аномальные объемы для ${ticker}: ${JSON.stringify(data)}`);
    } catch (error) {
        console.error('Ошибка при получении данных об аномальных объемах:', error);
        ctx.reply('Не удалось получить данные об аномальных объемах. Попробуйте позже.');
    }
});

// --- Обработчик команды /anomalous_limits ---
bot.command('anomalous_limits', async (ctx) => {
    const ticker = ctx.message.text.split(' ')[1];
    if (!ticker) {
        return ctx.reply('Пожалуйста, укажите тикер после команды /anomalous_limits');
    }

    try {
        const apiUrl = `${process.env.API_URL}/anomalous_limits?ticker=${ticker}`; // Раскомментируем
        const response = await axios.get(apiUrl);
        const data = response.data;
        ctx.reply(`Аномальные лимитки для ${ticker}: ${JSON.stringify(data)}`);
    } catch (error) {
        console.error('Ошибка при получении данных об аномальных лимитках:', error);
        ctx.reply('Не удалось получить данные об аномальных лимитках. Попробуйте позже.');
    }
});

// --- Обработчик команды /net_flow ---
bot.command('net_flow', async (ctx) => {
    const ticker = ctx.message.text.split(' ')[1];
    if (!ticker) {
        return ctx.reply('Пожалуйста, укажите тикер после команды /net_flow');
    }

    try {
        const apiUrl = `${process.env.API_URL}/net_flow?ticker=${ticker}`; // Раскомментируем
        const response = await axios.get(apiUrl);
        const data = response.data;
        ctx.reply(`Индикатор чистого потока для ${ticker}: ${JSON.stringify(data)}`);
    } catch (error) {
        console.error('Ошибка при получении данных о чистом потоке:', error);
        ctx.reply('Не удалось получить данные об индикаторе чистого потока. Попробуйте позже.');
    }
});

// --- Обработчик команды /short_squeeze ---
bot.command('short_squeeze', async (ctx) => {
    const ticker = ctx.message.text.split(' ')[1];
    if (!ticker) {
        return ctx.reply('Пожалуйста, укажите тикер после команды /short_squeeze');
    }

    try {
        const apiUrl = `${process.env.API_URL}/short_squeeze?ticker=${ticker}`; // Раскомментируем
        const response = await axios.get(apiUrl);
        const data = response.data;
        ctx.reply(`Индикатор шорт-сквиза для ${ticker}: ${JSON.stringify(data)}`);
    } catch (error) {
        console.error('Ошибка при получении данных о шорт-сквизе:', error);
        ctx.reply('Не удалось получить данные об индикаторе шорт-сквиза. Попробуйте позже.');
    }
});

// --- Обработчик текстовых сообщений ---
bot.on('text', (ctx) => {
    ctx.replyWithPhoto({url: 'https://d5dmrfea16lrot6rrndr.qsvaa8tq.apigw.yandexcloud.net/sayhello.png'});
    ctx.reply(`Привет, ${ctx.message.from.username}`);
});

// --- Yandex Cloud Functions Handler ---
module.exports.handler = async function (event, context) {
    try {
        console.log("Получено событие:", JSON.stringify(event)); // Логируем событие
        const message = JSON.parse(event.body);
        console.log("Сообщение:", JSON.stringify(message)); // Логируем сообщение
        await bot.handleUpdate(message);
        return {
            statusCode: 200,
            body: '',
        };
    } catch (error) {
        console.error("Ошибка при обработке события:", error);
        return {
            statusCode: 500,
            body: '',
        };
    }
};
