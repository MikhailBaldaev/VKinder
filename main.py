
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from vk_func import find_info, get_photos, my_keyboard_1, my_keyboard_2, my_keyboard_3, my_keyboard_4
from SQL_func import engine, session, Users, Candidates, Photos, update_favorite, show_favorite
from modules import create_tables
from config import token

from prettyprinter import pprint


vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

vk = vk.get_api()
session_vk = vk_api.VkApi(token=token)

create_tables(engine)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() == 'hi':
                result_info = find_info(event.user_id)
                for i in range(len(result_info[1])):
                    result_photo = get_photos(result_info[1][i]['id'])
                candidates = session.query(Candidates.vk_id, Candidates.name).join(Users,
                                                                                   Users.id == Candidates.user_id).filter(
                    Users.vk_id == str(event.user_id)).filter(Candidates.favorite == None).all()
                pprint(candidates)
                text = f'Please, press "start" to search for the soulmate.'
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text,
                    "keyboard": my_keyboard_1.get_keyboard()
                }
                               )
            elif request == "Start":
                text = f'Please, meet {candidates[0][1]}\nThis is their account: https://vk.com/id{candidates[0][0]}\nAnd below you can see their photos: \n'
                instructions = f'\nFor the next candidate press "Next"\nTo add candidate to favorites press "Add to Favorite"' \
                       f'\nTo show all favorites press "Show Favorites".'
                photos = session.query(Photos.link).join(Candidates, Candidates.id == Photos.candidate_id).filter(Candidates.vk_id == str(candidates[0][0])).all()
                for i in range(len(photos)):
                    photos[i] = photos[i][0]
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text + instructions,
                    "keyboard": my_keyboard_2.get_keyboard(),
                    "attachment": ','.join(photos)
                }
                               )
                removed = candidates.pop(0)
            elif request == "Next":
                text = f'Please, meet {candidates[0][1]}\nThis is their account: https://vk.com/id{candidates[0][0]}\nAnd below you can see their photos: \n '
                instructions = f'\nFor the next candidate press "Next"\nTo add candidate to favorites press "Add to Favorite"' \
                       f'\nTo show all favorites press "Show Favorites".'
                photos = session.query(Photos.link).join(Candidates, Candidates.id == Photos.candidate_id).filter(Candidates.vk_id == str(candidates[0][0])).all()
                for i in range(len(photos)):
                    photos[i] = photos[i][0]
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text + instructions,
                    "keyboard": my_keyboard_2.get_keyboard(),
                    "attachment": ','.join(photos)
                }
                               )
                update_favorite(removed[0], False)
                removed = candidates.pop(0)
            elif request == "Add to Favorite":
                text = f'We added previous candidate to the favorites list!\n\nPlease, meet {candidates[0][1]}\nThis is their account: https://vk.com/id{candidates[0][0]}\nAnd below you can see their photos: \n'
                instructions = f'\nFor the next candidate press "Next"\nTo add candidate to favorites press "Add to Favorite"' \
                       f'\nTo show all favorites press "Show Favorites".'
                photos = session.query(Photos.link).join(Candidates, Candidates.id == Photos.candidate_id).filter(Candidates.vk_id == str(candidates[0][0])).all()
                for i in range(len(photos)):
                    photos[i] = photos[i][0]

                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text + instructions,
                    "keyboard": my_keyboard_2.get_keyboard(),
                    "attachment": ','.join(photos)
                }
                               )
                update_favorite(removed[0], True)
                removed = candidates.pop(0)
            elif request == "Show Favorites":
                result = show_favorite(str(event.user_id))
                instructions = f'\nFor the next candidate press "Next"\nTo add candidate to favorites press "Add to Favorite"' \
                               f'\nTo show all favorites press "Show Favorites".'
                text = result[0].split(';')
                count = 0
                for i in text:

                    if i:

                        if len(result[1][count]) > 0:
                            photos_temp = ','.join(result[1][count][0])
                            session_vk.method("messages.send", {
                                "user_id": event.user_id,
                                "random_id": get_random_id(),
                                "message": text[count],
                                "keyboard": my_keyboard_3.get_keyboard(),
                                "attachment": photos_temp
                            }
                                              )
                            count += 1
                        else:
                            session_vk.method("messages.send", {
                                "user_id": event.user_id,
                                "random_id": get_random_id(),
                                "message": text[count],
                                "keyboard": my_keyboard_3.get_keyboard()
                            }
                                              )
                            count += 1

                    else:
                        continue

            elif request == "Finish":
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": 'See you!'
                }
                               )
            else:
                text = f'First of all, try to say "Hi")'
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text,
                }
                                  )
            if len(candidates) == 0:
                print(candidates)
                text = f'No more candidates for you! You can try to say "Hi" to see new ones!'
                session_vk.method("messages.send", {
                    "user_id": event.user_id,
                    "random_id": get_random_id(),
                    "message": text,
                    "keyboard": my_keyboard_4.get_keyboard()
                }
                                 )