from flask import Flask
from flask_moment import Moment
# import sqlalchemy.types as types
from flask_migrate import Migrate
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)





class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres =  db.Column("genres", db.ARRAY(db.String(500)))

    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))

    shows = db.relationship('Show', lazy=True, backref='venue', cascade="all, delete-orphan")



    def __repr__(self):
        return f'<Venue: {self.id} {self.name}>'



class Genre(db.Model):
  __tablename__ = 'genre'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String(500)))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))

    shows = db.relationship('Show', backref='artist', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Artist: {self.id} {self.name}>'





class Show(db.Model):
  __tablename__= 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now(datetime.timezone.utc))    



  def __repr__(self):
      return f'<Show: {self.id} start_time={self.start_time}, artist_id{self.artist_id}, venue_id{self.venue_id}>'