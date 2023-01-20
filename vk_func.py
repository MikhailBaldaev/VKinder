
import vk_api
import datetime

from vk_api.utils import get_random_id

from config import login, password
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from SQL_func import insert_user


vk_session = vk_api.VkApi(login, password)
vk_session.auth()
vk = vk_session.get_api()


def find_info(session, user_id):
    search_data = vk.users.get(user_ids=user_id, fields='sex, home_town, bdate')
    user_age = int(search_data[0]['bdate'][-4:])
    user_name = f"{search_data[0]['first_name']} {search_data[0]['last_name']}"
    user_city = search_data[0]['home_town']
    insert_user(session=session, vk_id=str(user_id), name=user_name, age=user_age, city=user_city, sex=search_data[0]['sex'])
    inquiry = vk.users.search(age_from=(datetime.datetime.now().year-5)-user_age, age_to=(datetime.datetime.now().year+5)-user_age, hometown=search_data[0]['home_town'], sex=3-search_data[0]['sex'], has_photo=1, count=25, is_closed=False, can_access_closed=True, deactivated=None)
    candidates = []

    for item in inquiry['items']:
        candidate = {key: value for (key, value) in item.items() if
                     key in ['id', 'first_name', 'last_name'] and not item['is_closed']}

        if candidate:
            candidates.append(candidate)
        else:
            continue

    result = f'Советуем посмотреть на кандидатов:\n{candidates[0]["first_name"]} {candidates[0]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[0]["id"]}\n{candidates[1]["first_name"]} {candidates[1]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[1]["id"]}'

    return result, candidates


def get_photos(candidate_vk_id):
    response = vk.photos.get(owner_id=candidate_vk_id, extended=1, album_id='profile')
    photos_data = []

    likes_dict = {}

    for photo in response['items']:
        likes_dict[photo['likes']['count']] = photo['id']
    likes_dict = dict(sorted(likes_dict.items())[:-4:-1])

    for photo_id in likes_dict.values():
        link = f'photo{candidate_vk_id}_{photo_id}'
        photos_data.append(link)

    return photos_data, likes_dict


def send_msg(session_vk, user_id, text, keyboard=None, attachment=None):
    if keyboard:
        session_vk.method("messages.send", {
            "user_id": user_id,
            "random_id": get_random_id(),
            "message": text,
            "keyboard": keyboard.get_keyboard(),
            "attachment": attachment,
        }
                          )
    else:
        session_vk.method("messages.send", {
            "user_id": user_id,
            "random_id": get_random_id(),
            "message": text,
            "attachment": attachment,
        }
                          )


def keyboards(num):
    my_keyboard = VkKeyboard(one_time=True, inline=False)
    buttons_list = {
        1: {'buttons': ('Start', 'Finish'), 'buttons_color': (VkKeyboardColor.PRIMARY, VkKeyboardColor.NEGATIVE)},
        2: {'buttons': ('Next', 'Add to Favorite', 'Show Favorites', 'Finish'), 'buttons_color': (VkKeyboardColor.PRIMARY, VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE)},
        3: {'buttons': ('Show Favorites', 'Hi'), 'buttons_color': (VkKeyboardColor.PRIMARY, VkKeyboardColor.NEGATIVE)},
    }

    if num == 1:

        for i, k in zip(buttons_list[1]['buttons'], buttons_list[1]['buttons_color']):
            my_keyboard.add_button(i, k)

        return my_keyboard

    elif num == 2:
        count = 0

        for i, k in zip(buttons_list[2]['buttons'], buttons_list[2]['buttons_color']):
            if count == 2:
                my_keyboard.add_line()
            my_keyboard.add_button(i, k)
            count += 1

        return my_keyboard

    elif num == 3:

        for i, k in zip(buttons_list[3]['buttons'], buttons_list[3]['buttons_color']):
            my_keyboard.add_button(i, k)

        return my_keyboard
