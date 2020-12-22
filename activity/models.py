"""Database models."""
from flask_login import UserMixin
from . import db
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

# define utcnow function for postgreSQL


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'users'

    user_id = db.Column(db.Integer,
                        primary_key=True)

    user_name = db.Column(db.String(100),
                          nullable=False,
                          unique=False)

    user_hash = db.Column(db.String(200),
                          primary_key=False,
                          unique=False,
                          nullable=False)

    created_on = db.Column(db.DateTime,
                           server_default=utcnow(),
                           index=False,
                           unique=False,
                           nullable=False)

    last_login = db.Column(db.DateTime(timezone=True),
                           onupdate=utcnow(),
                           server_default=utcnow(),
                           index=False,
                           unique=False,
                           nullable=False)

    log_update = db.Column(db.Boolean,
                           unique=False,
                           default=False)

    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        return '<User {}>'.format(self.user_name)


class Activity(db.Model):
    """Acictivity model."""

    __tablename__ = "activities"

    act_id = db.Column(db.Integer,
                       primary_key=True)

    act_name = db.Column(db.Text(),
                         nullable=False)

    act_score = db.Column(db.Integer,
                          nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)

    def __repr__(self):
        return '<Activity: {}>'.format(self.act_name)


class Scores(db.Model):
    """Score storage model."""

    __tablename__ = "scores"

    score_id = db.Column(db.Integer,
                         primary_key=True)

    score_name = db.Column(db.Text(),
                           nullable=False)

    score_value = db.Column(db.Integer(),
                            nullable=False,
                            default=0)

    score_time = db.Column(db.DateTime,
                           server_default=utcnow(),
                           onupdate=utcnow(),
                           index=False,
                           unique=False,
                           nullable=False)

    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)

    act_id = db.Column(db.Integer,
                       db.ForeignKey("activities.act_id"),
                       nullable=False)

    def __repr__(self):
        return '<Scores: {}>'.format(self.score_name)
