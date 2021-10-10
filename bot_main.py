import telebot
from bot_settings import *
import operator
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def check_again_button(uid):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton(TEXT['get_link'], callback_data="change_room"))
    bot.send_message(uid, TEXT['bot_info'], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def change_room_claback(message):
    if message.data == "change_room":
        uid = message.from_user.id
        target_chat = get_target_chat(RELATIVE_CHAT_IDS)
        member = check_membership(uid, RELATIVE_CHAT_IDS)
        if target_chat and target_chat not in member:
            link = bot.create_chat_invite_link(target_chat, member_limit=1).invite_link
            bot.send_message(uid, TEXT['new_room'] % link)
            [bot.unban_chat_member(chat_id, uid) for chat_id in member if member != target_chat]
        else:
            bot.send_message(uid, TEXT['nothing_to_change'])
        bot.answer_callback_query(message.id)
    else:
        bot.answer_callback_query(message.id, "Какие странные у вас кнопочки!?")


@bot.message_handler(commands=['start'])
def start(message):
    try:
        if message.chat.type == 'private':
            check_again_button(message.from_user.id)
    except Exception as ex1:
        logger("unhandled exception, send_text", str(ex1))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    try:
        if message.chat.type != 'private' or len(message.text) <= 0:
            logger(message)
            return
        check_again_button(message.from_user.id)
    except Exception as ex1:
        logger("unhandled exception, send_text", str(ex1))


def get_target_chat(chats=RELATIVE_CHAT_IDS):
    counts = [(i, bot.get_chat_member_count(i)) for i in chats]
    target = round((sum([i[1] for i in counts]) / len(counts)) * 0.99)
    minchat = min(counts, key=operator.itemgetter(1))
    return minchat[0] if minchat[1] <= target else False


def check_membership(userid, chats=RELATIVE_CHAT_IDS):
    member = []
    for id in chats:
        try:
            if bot.get_chat_member(chat_id=id, user_id=userid).status != "left":
                member.append(id)
        except:
            pass
    return member

bot.infinity_polling()
