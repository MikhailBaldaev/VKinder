
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from SQL_func import insert_user, insert_candidates, insert_photos, session, Users, Candidates
from config import login, password

vk_session = vk_api.VkApi(login, password)
vk_session.auth()
vk = vk_session.get_api()


my_keyboard_1 = VkKeyboard(one_time=True, inline=False)
buttons = ['Start', 'Finish']
buttons_color = [VkKeyboardColor.PRIMARY, VkKeyboardColor.NEGATIVE]
for i, k in zip(buttons, buttons_color):
    my_keyboard_1.add_button(i, k)

my_keyboard_2 = VkKeyboard(one_time=True, inline=False)
buttons = ['Next', 'Add to Favorite', 'Show Favorites', 'Finish']
buttons_color = [VkKeyboardColor.PRIMARY, VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]
count = 0
for i, k in zip(buttons, buttons_color):
    if count == 2:
        my_keyboard_2.add_line()
    my_keyboard_2.add_button(i, k)
    count += 1

my_keyboard_3 = VkKeyboard(one_time=True, inline=False)
buttons = ['Start', 'Finish']
buttons_color = [VkKeyboardColor.PRIMARY, VkKeyboardColor.NEGATIVE]
for i, k in zip(buttons, buttons_color):
    my_keyboard_3.add_button(i, k)

my_keyboard_4 = VkKeyboard(one_time=True, inline=False)
buttons = ['Show Favorites', 'Hi']
buttons_color = [VkKeyboardColor.PRIMARY, VkKeyboardColor.NEGATIVE]
for i, k in zip(buttons, buttons_color):
    my_keyboard_4.add_button(i, k)


def find_info(user_id):
    search_data = vk.users.get(user_ids=user_id, fields='sex, home_town, bdate')
    user_age = int(search_data[0]['bdate'][-4:])
    user_name = f"{search_data[0]['first_name']} {search_data[0]['last_name']}"
    user_city = search_data[0]['home_town']
    insert_user(vk_id=str(user_id), name=user_name, age=user_age, city=user_city, sex=search_data[0]['sex'])
    inquiry = vk.users.search(age_from=2017-user_age, age_to=2027-user_age, hometown=search_data[0]['home_town'], sex=3-search_data[0]['sex'], has_photo=1, count=25, is_closed=False, can_access_closed=True, deactivated=None)
    candidates = []
    count = 0
    while count < len(inquiry['items']):
        candidate = {key: value for (key, value) in inquiry['items'][count].items() if key in ['id', 'first_name', 'last_name']}
        candidates.append(candidate)
        candidate_vk_id = inquiry['items'][count]['id']
        candidate_name = f"{inquiry['items'][count]['first_name']} {inquiry['items'][count]['last_name']}"
        candidate_age = 2023-(int(vk.users.get(user_ids=candidate_vk_id, fields='bdate')[0]['bdate'][-4:]))
        user = session.query(Users.id).filter(Users.vk_id == str(user_id))[0][0]
        insert_candidates(vk_id=candidate_vk_id, name=candidate_name, age=candidate_age, city=user_city, sex=3-search_data[0]['sex'], favorite=None, user=user)
        count += 1
    result = f'Советуем посмотреть на кандидатов:\n{candidates[0]["first_name"]} {candidates[0]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[0]["id"]}\n{candidates[1]["first_name"]} {candidates[1]["last_name"]}' \
             f'\nid во Вконтакте: {candidates[1]["id"]}'
    return result, candidates


def get_photos(candidate_vk_id):
    candidate_id = session.query(Candidates.id).filter(Candidates.vk_id == str(candidate_vk_id))[0][0]
    response = vk.photos.get(owner_id=candidate_vk_id, extended=1, album_id='profile')
    photos_data = []
    if len(response['items']) > 3:
        likes_dict = {}
        for photo in response['items']:
            likes_dict[photo['likes']['count']] = photo['id']
        likes_dict = dict(sorted(likes_dict.items())[:-4:-1])
        for photo_id in likes_dict.values():
            link = f'photo{candidate_vk_id}_{photo_id}'
            likes = [key for (key, value) in likes_dict.items() if value == photo_id]
            photos_data.append(link)
            insert_photos(link=link, likes=likes[0], candidate_id=candidate_id)
    else:
        for photo in response['items']:
            photo_id = photo['id']
            link = f'photo{candidate_vk_id}_{photo_id}'
            likes = photo['likes']['count']
            photos_data.append(link)
            insert_photos(link=link, likes=likes, candidate_id=candidate_id)
    return photos_data