Я бот для Telegram, который отвечает на сообщения, содержащие ключевые слова из заданного списка. Ответы бота основаны на моделях текстового обучения от OpenAI. Бот использует библиотеку python-telegram-bot для взаимодействия с Telegram API.

Код открыт для всех: https://github.com/KlimDos/tg_bot_gpt.git

 - Для того чтобы посмотреть список слов на которые реагирует бот, напишите боту или в чате `/help`
 - Для того чтобы прочитать readme.md напишите боту или в чате `/bot`
 - Если вы не хотите чтобы бот реагировал на ваши сообщения, напишите боту или в чате `/stop`

# Run

```
docker run -e TG_API_TOKEN="***" -e GPT_API_TOKEN="***" klimdos/gpt-bot:0.0.1-manual
```

# Manual Build

`git clone`
`docker build -t klimdos/gpt-bot:0.0.1-manual . `

# GitHub action
#TBD
