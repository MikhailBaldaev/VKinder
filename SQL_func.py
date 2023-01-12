
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from prettyprinter import pprint

from modules import Users, Candidates, Photos
from config import DSN


engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()


def insert_user(vk_id, name, age, city, sex):
    if session.query(Users.vk_id).filter(Users.vk_id == str(vk_id)).all():
        pass
    else:
        table_users = Users(vk_id=vk_id, name=name, age=2023-age, city=city, sex=sex)
        session.add(table_users)
    session.commit()


def insert_candidates(vk_id, name, age, city, sex, favorite, user):
    if session.query(Candidates.vk_id).filter(Candidates.vk_id == str(vk_id)).all():
        pass
    else:
        table_candidates = Candidates(vk_id=vk_id, name=name, age=age, city=city, sex=sex, favorite=favorite,
                                      user_id=user)

        session.add(table_candidates)
    session.commit()


def insert_photos(link, likes, candidate_id):
    table_photos = Photos(link=link, likes=likes, candidate_id=candidate_id)
    session.add(table_photos)
    session.commit()


def update_favorite(candidate_vk_id, value):
    session.query(Candidates).filter(Candidates.vk_id == candidate_vk_id).update({"favorite": value})
    session.commit()


def show_favorite(user_id):
    favorite_list = session.query(Candidates.vk_id).join(Users, Users.id == Candidates.user_id).filter(Users.vk_id == user_id).filter(Candidates.favorite == True).all()
    result = ''
    photos = []

    for i in favorite_list:
        candidate_name = session.query(Candidates.name).filter(Candidates.vk_id == i[0]).all()
        photo = session.query(Photos.link).join(Candidates, Candidates.id == Photos.candidate_id).filter(Candidates.vk_id == i[0]).all()
        photos.append(photo)
        result += f'\nName: {candidate_name[0][0]}\nAccount: https://vk.com/id{i[0]};'

    session.commit()
    return result, photos

session.close()
