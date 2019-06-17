import logging
import os
import cfapp


'''
sethandle - Set your Codeforces handle
settags - Set a list of tags to filter problems
setminlevel - Set a minimum level for problems
setmaxlevel - Set a maximum level for problems
seeconf - Shows your configuration details
seetags - Shows all the Codeforces tags
getproblem - Get a problem

Todos:
- documentar codigo
- ordenar codigo
- Lista de tags
'''

# from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s'
                    ' - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

token = os.getenv("TOKEN")

HANDLE, TAGS, MIN, MAX = range(4)

ALL_TAGS = ['implementation', 'dp', 'math', 'greedy', 'brute force',
            'data structures', 'constructive algorithms', 'dfs and similar',
            'sortings', 'binary search', 'graphs', 'trees', 'strings',
            'number theory', 'geometry', 'combinatorics', 'two pointers', 'dsu'
            'bitmasks', 'probabilities', 'shortest paths', 'hashing',
            'divide and conquer', 'games', 'matrices', 'flows',
            'string suffix structures', 'expression parsing',
            'graph matchings', 'ternary search', 'meet-in-the-middle',
            'fft', '2-sat', 'chinese remainder theorem', 'schedules']


def check_tags(tags):
    for tag in tags:
        if tag not in ALL_TAGS:
            return (False, tag)
    return (True, None)


def format_tags(tags: list):
    formated_tags = ''
    for tag in tags:
        formated_tags += tag.strip() + ';'
    return formated_tags


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye!')

    return ConversationHandler.END


def start(update, context):
    '''
    Send  a Message when the start command is sent
    '''
    update.message.reply_text(
        'Hi! I am here to improve your skills. '
        'Would you like to send me your Codeforces Handle?')
    return HANDLE


def handle(update, context):
    user = update.message.from_user
    logger.info('Handle of %s: %s', user.first_name, update.message.text)
    context.user_data[HANDLE] = update.message.text
    update.message.reply_text('Great!, Now we must set your preferences. '
                              'What problems tags are you searching?'
                              ' (separate them by a comma)')
    return TAGS


def tags(update, context):
    user = update.message.from_user
    logger.info('Tags of %s: %s', user.first_name, update.message.text)
    context.user_data[TAGS] = format_tags(update.message.text.split(','))
    update.message.reply_text('Nice!, Now tell me your minimum level')
    return MIN


def mini(update, context):
    user = update.message.from_user
    logger.info('Min level of %s: %s', user.first_name, update.message.text)
    context.user_data[MIN] = update.message.text
    update.message.reply_text('And what about your maximum level?')
    return MAX


def maxi(update, context):
    user = update.message.from_user
    logger.info('Max level of %s: %s', user.first_name, update.message.text)
    context.user_data[MAX] = update.message.text
    update.message.reply_text('Your configuration in ready!\n'
                              'Now you can request for a problem with '
                              '/getproblem ')
    return ConversationHandler.END


def see_tags(update, context):
    string_all_tags = 'Codeforces tags are:\n'
    for tag in ALL_TAGS:
        string_all_tags += tag + '\n'
    update.message.reply_text(string_all_tags)


def see_conf(update, context):
    tags = context.user_data[TAGS].split(';')
    string_tags = ''
    for tag in tags:
        string_tags += tag + ', '
    string_tags = string_tags[:len(string_tags)-4]
    update.message.reply_text('Actual configuration:\n'
                              'Handle: {}\n'
                              'Tags: {}\n'
                              'Minimum level: {}\n'
                              'Maximum level: {}\n'.format(
                                                    context.user_data[HANDLE],
                                                    string_tags,
                                                    context.user_data[MIN],
                                                    context.user_data[MAX]))


def change_handle(update, context):
    update.message.reply_text('Send me your Codeforces handle')
    return HANDLE


def set_handle(update, context):
    new_handle = update.message.text
    context.user_data[HANDLE] = new_handle
    update.message.reply_text('Handle changed !')
    return ConversationHandler.END


def change_tags(update, context):
    update.message.reply_text('Send me your new tags')
    return TAGS


def set_tags(update, context):
    new_tags = update.message.text
    context.user_data[TAGS] = format_tags(new_tags.split(','))
    update.message.reply_text('Tags changed !')
    return ConversationHandler.END


def change_min_level(update, context):
    update.message.reply_text('Send me your new minimum level')
    return MIN


def set_min_level(update, context):
    new_min = update.message.text
    context.user_data[MIN] = new_min
    update.message.reply_text('Minimum level changed !')
    return ConversationHandler.END


def change_max_level(update, context):
    update.message.reply_text('Send me your new maximum level')
    return MAX


def set_max_level(update, context):
    new_max = update.message.text
    context.user_data[MAX] = new_max
    update.message.reply_text('Maximum level changed !')
    return ConversationHandler.END


def get_problem(update, context):
    conf = context.user_data
    try:
        cfapp.test_api()
        tags = conf[TAGS].split(';')
        correct, poss_tag = check_tags(tags[:len(tags)-1])
        if(not correct):
            update.message.reply_text('Tag {} do not exist in Codeforces'.
                                      format(poss_tag))
            return
        problems = cfapp.make_query('problemset.problems',
                                    ['tags'], conf[TAGS])
        filtered_problems = cfapp.level_filter(problems, int(conf[MIN]),
                                               int(conf[MAX]))
        ids = cfapp.get_problem(conf[HANDLE], filtered_problems)
        update.message.reply_text('{}'.format(cfapp.generate_url(ids)))
    except Exception as e:
        update.message.reply_text(e.message)


def main():
    pp = PicklePersistence(filename='cf_app')
    updater = Updater(token, persistence=pp, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            HANDLE: [MessageHandler(Filters.text, handle)],

            TAGS: [MessageHandler(Filters.text, tags)],

            MIN: [MessageHandler(Filters.text, mini)],

            MAX: [MessageHandler(Filters.text, maxi)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        name="my_configuration",
        persistent=True
    )

    change_handle_conv = ConversationHandler(
        entry_points=[CommandHandler('sethandle', change_handle)],
        states={
            HANDLE: [MessageHandler(Filters.text, set_handle)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="change_handle",
        persistent=True
    )

    change_tags_conv = ConversationHandler(
        entry_points=[CommandHandler('settags', change_tags)],
        states={
            TAGS: [MessageHandler(Filters.text, set_tags)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="change_tags",
        persistent=True
    )

    change_min_conv = ConversationHandler(
        entry_points=[CommandHandler('setminlevel', change_min_level)],
        states={
            MIN: [MessageHandler(Filters.text, set_min_level)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="change_min_level",
        persistent=True
    )

    change_max_conv = ConversationHandler(
        entry_points=[CommandHandler('setmaxlevel', change_max_level)],
        states={
            MAX: [MessageHandler(Filters.text, set_max_level)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="change_max_level",
        persistent=True
    )

    dp.add_handler(CommandHandler("seeconf", see_conf))
    dp.add_handler(CommandHandler("getproblem", get_problem))
    dp.add_handler(CommandHandler("seetags", see_tags))

    dp.add_handler(conv_handler)
    dp.add_handler(change_handle_conv)
    dp.add_handler(change_tags_conv)
    dp.add_handler(change_min_conv)
    dp.add_handler(change_max_conv)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
