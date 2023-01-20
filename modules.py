
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    name = sq.Column(sq.String(length=60), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)


class Candidates(Base):
    __tablename__ = "candidates"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)
    name = sq.Column(sq.String(length=60), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.Integer, nullable=False)
    favorite = sq.Column(sq.Boolean)

    user = relationship(Users, backref="candidates")


class Photos(Base):
    __tablename__ = "photos"

    id = sq.Column(sq.Integer, primary_key=True)
    link = sq.Column(sq.String(length=60), nullable=False)
    candidate_id = sq.Column(sq.Integer, sq.ForeignKey("candidates.id"), nullable=False)


def create_tables(engine):
    Base.metadata.create_all(engine)
