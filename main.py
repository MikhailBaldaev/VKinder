
import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType

from config import token
from models import create_tables, drop_tables, Users, Candidates
from SQL_func import Session, engine, show_favorite, insert_candidates, insert_photos
from vk_func import find_info, get_photos, keyboards, send_msg
#from prettyprinter import pprint

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

vk = vk.get_api()
session_vk = vk_api.VkApi(token=token)

session = Session()

drop_tables(engine)
create_tables(engine)

candidates = [0] #'0' is a workaround to enable reply "First of all, try to say "Hi"" if 'candidates' variable is None
photos = []
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request.lower() == 'hi':
                result_info = find_info(session, event.user_id)

                candidates = result_info[1]

                for i in candidates:
                    result_photo = get_photos(i['id'])
                    photos.append({i['id']: result_photo[0]})
                text = f'Please, press "start" to search for the soulmate.'
                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text,
                         keyboard=keyboards(1),
                         )

            elif request == "Start":
                text = f'Please, meet {candidates[0]["first_name"]} {candidates[0]["last_name"]}\n' \
                       f'This is their account: https://vk.com/id{candidates[0]["id"]}\n' \
                       f'And below you can see their photos: \n'
                instructions = f'\nFor the next candidate press "Next"\n' \
                               f'To add candidate to favorites press "Add to Favorite"' \
                               f'\nTo show all favorites press "Show Favorites".'

                photo_msg = photos[0][candidates[0]["id"]]

                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text + instructions,
                         keyboard=keyboards(2),
                         attachment=','.join(photo_msg),
                         )
                removed_cand = candidates.pop(0)
                removed_photo = photos.pop(0)

            elif request == "Next":
                text = f'Please, meet {candidates[0]["first_name"]} {candidates[0]["last_name"]}\n' \
                       f'This is their account: https://vk.com/id{candidates[0]["id"]}\n' \
                       f'And below you can see their photos: \n '
                instructions = f'\nFor the next candidate press "Next"\n' \
                               f'To add candidate to favorites press "Add to Favorite"'\
                               f'\nTo show all favorites press "Show Favorites".'

                photo_msg = photos[0][candidates[0]["id"]]

                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text + instructions,
                         keyboard=keyboards(2),
                         attachment=','.join(photo_msg),
                         )

                removed_candidate = vk.users.get(user_ids=removed_cand['id'], fields='sex, home_town, bdate')
                user = session.query(Users.id, Users.city).filter(Users.vk_id == str(event.user_id))[0]

                if 'home_town' in removed_candidate[0].keys():
                    insert_candidates(session=session,
                                      vk_id=removed_cand['id'],
                                      name=f'{removed_cand["first_name"]} {removed_cand["last_name"]}',
                                      age=int(removed_candidate[0]['bdate'][-4:]),
                                      city=removed_candidate[0]['home_town'],
                                      sex=removed_candidate[0]['sex'],
                                      favorite=False,
                                      user=user[0],
                                      )
                else:
                    insert_candidates(session=session,
                                      vk_id=removed_cand['id'],
                                      name=f'{removed_cand["first_name"]} {removed_cand ["last_name"]}',
                                      age=int(removed_candidate[0]['bdate'][-4:]),
                                      city=user[1],
                                      sex=removed_candidate[0]['sex'],
                                      favorite=False,
                                      user=user[0],
                                      )

                candidate_vk_id = str(removed_photo[removed_cand['id']][0].split('_')[0][5:])
                candidate_id = session.query(Candidates.id).filter(Candidates.vk_id == candidate_vk_id).all()[0][0]
                insert_photos(session=session,
                              link=removed_photo[removed_cand['id']][0],
                              candidate_id=candidate_id,
                              )

                removed_cand = candidates.pop(0)
                removed_photo = photos.pop(0)

            elif request == "Add to Favorite":
                text = f'We added previous candidate to the favorites list!' \
                       f'\n\nPlease, meet {candidates[0]["first_name"]} {candidates[0]["last_name"]}\n' \
                       f'This is their account: https://vk.com/id{candidates[0]["id"]}\n' \
                       f'And below you can see their photos: \n'
                instructions = f'\nFor the next candidate press "Next"\n' \
                               f'To add candidate to favorites press "Add to Favorite" \n' \
                               f'To show all favorites press "Show Favorites".'

                photo_msg = photos[0][candidates[0]["id"]]

                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text + instructions,
                         keyboard=keyboards(2),
                         attachment=','.join(photo_msg),
                         )

                removed_candidate = vk.users.get(user_ids=removed_cand['id'], fields='sex, home_town, bdate')
                user = session.query(Users.id, Users.city).filter(Users.vk_id == str(event.user_id))[0]

                if 'home_town' in removed_candidate[0].keys():
                    insert_candidates(session=session,
                                      vk_id=removed_cand['id'],
                                      name=f'{removed_cand["first_name"]} {removed_cand["last_name"]}',
                                      age=int(removed_candidate[0]['bdate'][-4:]),
                                      city=removed_candidate[0]['home_town'],
                                      sex=removed_candidate[0]['sex'],
                                      favorite=True,
                                      user=user[0],
                                      )
                else:
                    insert_candidates(session=session,
                                      vk_id=removed_cand['id'],
                                      name=f'{removed_cand["first_name"]} {removed_cand["last_name"]}',
                                      age=int(removed_candidate[0]['bdate'][-4:]),
                                      city=user[1],
                                      sex=removed_candidate[0]['sex'],
                                      favorite=True,
                                      user=user[0],
                                      )

                candidate_vk_id = str(removed_photo[removed_cand['id']][0].split('_')[0][5:])
                candidate_id = session.query(Candidates.id).filter(Candidates.vk_id == candidate_vk_id).all()[0][0]
                insert_photos(session=session,
                              link=removed_photo[removed_cand['id']][0],
                              candidate_id=candidate_id,
                              )

                removed_cand = candidates.pop(0)
                removed_photo = photos.pop(0)

            elif request == "Show Favorites":
                result = show_favorite(session, str(event.user_id))
                instructions = f'\nFor the next candidate press "Next"\n' \
                               f'To add candidate to favorites press "Add to Favorite"\n' \
                               f'To show all favorites press "Show Favorites".'
                text = result[0].split(';')

                for i in result[1]:
                    photos_temp = ','.join(i[0])
                    ind = result[1].index(i)
                    send_msg(session_vk=session_vk,
                             user_id=event.user_id,
                             text=text[ind],
                             keyboard=keyboards(2),
                             attachment=photos_temp,
                             )

            elif request == "Finish":
                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text='See you!',
                         )

            else:
                text = f'First of all, try to say "Hi")'
                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text,
                         )

            if len(candidates) == 0:
                text = f'No more candidates for you! You can try to say "Hi" to see new ones!'
                send_msg(session_vk=session_vk,
                         user_id=event.user_id,
                         text=text,
                         keyboard=keyboards(3),
                         )


session.close()
