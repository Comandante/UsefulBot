
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from time import localtime, strftime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import requests


def main():
    updater = Updater("384561629:AAEnvY0rHzyyRraqvJmgtrYW_gZr4CMHWMs")

    dp = updater.dispatcher


    text_handler = MessageHandler(Filters.text, echo)
    conv_handler = ConversationHandler(
       entry_points=[CommandHandler('conversation', conversation)],
       states={1: [MessageHandler(Filters.text, first_response, pass_user_data=True)],
               2: [MessageHandler(Filters.text, second_response, pass_user_data=True)],
               3: [MessageHandler(Filters.text, third_response, pass_user_data=True)]
               },
       fallbacks=[CommandHandler('stop', stop)]
     )

    dp.add_handler(text_handler)
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('wiki_search', wiki_search))
    dp.add_handler(CommandHandler('translater', translater))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("time", time))
    dp.add_handler(CommandHandler("date", date))
    dp.add_handler(CommandHandler('geocoder', geocoder))

    updater.start_polling()

    updater.idle()


def echo(bot, updater):
    updater.message.reply_text('Привет!')

def third_response():
    pass
def conversation(bot, updater, user_data):
    updater.message.reply_text("Привет, {}, где ты живешь?".format(updater.message.chat.username))

def stop(bot, update):
    update.message.reply_text(
        "Жаль. А было бы интерсно пообщаться. Всего доброго!")
    return ConversationHandler.END
def start(bot, update):
    update.message.reply_text(
        "Привет. Это полезный бот\n"
        "Бот может многое, например переводить тексты или искать что-то в интернете"
        "Больше можно узнать написав комманду /help \n"
    )
    return 1


def first_response(bot, update, user_data):
    user_data['locality'] = update.message.text
    update.message.reply_text(
        "Здорово, как погода?")
    return 2


def second_response(bot, update, user_data):
    weather = update.message.text
    user_data['weather'] = weather
    update.message.reply_text("Спасибо за участие в опросе! Привет, {0}!".
                              format(user_data['locality']))  # Используем user_data в ответе.
    return 3


def translater(bot, updater):
    accompanying_text = "Переведено сервисом «Яндекс.Переводчик» http://translate.yandex.ru/."
    translator_uri = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    response = requests.get(
            translator_uri,
            params=
            {
                "key":
                    "trnsl.1.1.20180408T134157Z.885b1a4a55bdc3a8.c3685921864e495d051637dc0fa03bee96e0621d",
                "lang": 'ru',
                "text": updater.message.text.split()[1]
            })
    updater.message.reply_text(
            "\n\n".join([response.json()["text"][0], accompanying_text]))


def wiki_search(bot, updater):
    wiki_url = 'https://ru.wikipedia.org/w/api.php'
    headers = {'User-Agent': 'UsefulBot/0.0.1; yack.uk@yandex.ru'}
    try:
        response = requests.get(wiki_url,
                                params={'action': 'opensearch',
                                        'search': updater.message.text.split()[1],
                                        'limit': '1',
                                        'prop': 'info',
                                        'inprop': 'url',
                                        'format': 'json'},
                                headers=headers)
        updater.message.reply_text('Вот что удалось найти по запросу "{}":\n'
                                   '{}\n'
                                   '{}'.format(updater.message.text.split()[1], str(response.json()[2][0]), str(response.json()[-1][0])))
    except Exception as e:
        updater.message.reply_text('По запросу "{}" ничего найти не удалось.\n'
                                   'Измените свой запрос или попытайтесь позже.\n'
                                   'Ошибка: {}'.format(updater.message.text.split()[1], e))


def weather(bot, update):
    find_url = "http://api.openweathermap.org/data/2.5/find"
    city = update.message.text.split()[1]
    response_1 = requests.get(find_url,
                              params={
                                   'q': city,
                                   'type': 'like',
                                   'units': 'metric',
                                   'APPID': '0d6d05789e21f430fa03709e55387150'})
    data_1 = response_1.json()
    city_id = data_1['list'][0]['id']
    try:
        weather_url = "http://api.openweathermap.org/data/2.5/weather"
        response = requests.get(weather_url,
                                params={'id': city_id,
                                        'units': 'metric',
                                        'lang': 'ru',
                                        'APPID': '0d6d05789e21f430fa03709e55387150'})
        data = response.json()
        update.message.reply_text('Сейчас в городе {} {}\n'
                                  'температура: {} по цельсию'.format(city, data['weather'][0]['description'], data['main']['temp']))
    except Exception as e:
        update.message.reply_text(("Произошла ошибка: {}".format(e)))


def geocoder(bot, updater):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    geocode = updater.message.text.split()[1]
    response = requests.get(geocoder_uri, params={
        "format": "json",
        "geocode": geocode
    })

    toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    delta = '0.05'
    ll = ",".join([toponym_longitude, toponym_lattitude])
    spn = ",".join([delta, delta])

    static_api_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l=map".format(ll, spn)

    updater.message.reply_text('{}:'.format(geocode))

    bot.sendPhoto(
        updater.message.chat.id,
        static_api_request
    )


def help(bot, update):
    update.message.reply_text("Это бот-помощник\n"
                              "Команда /weather {Город} показывает погоду в указанном городе\n"
                              "Команда /wiki_search {Запрос} выполняет поиск в википедии по указанному запросу\n"
                              "Комада /date показывает текущую дату\n"
                              "Команда /time показывает текущее время\n"
                              "Команда /translater {Текст} выполняет перевод указанного текста на русский язык\n"
                              )


def time(bot, update):
    time = strftime('%X', localtime())
    update.message.reply_text(time)


def date(bot,update):
    date = strftime('%x', localtime())
    update.message.reply_text(date)


if __name__ == '__main__':
    main()