from flask_sqlalchemy import SQLAlchemy
from util import format_datetime
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))

    def __repr__(self):
      return f'\n<Show: id: {self.id},\nstart_time: {self.start_time},\nvenue_id: {self.venue_id},\nartist_id: {self.artist_id}>\n'

    @property
    def _get_shows(self):
      return {'venue_id' : self.venue_id,
              'venue_name': self.venue.name,
              'artist_id': self.artist_id,
              'artist_name' : self.artist.name,
              'artist_image_link': self.artist.image_link,
              'start_time': format_datetime(str(self.start_time), format='full')
              }

    @property
    def _get_show_artist_time(self):
      return {'artist_id': self.artist_id,
              'artist_name': self.artist.name,
              'artist_image_link': self.artist.image_link,
              'start_time': format_datetime(str(self.start_time), format='full')
              }

    @property
    def _get_show_venue_time(self):
      return {'venue_id': self.venue_id,
              'venue_name': self.venue.name,
              'venue_image_link': self.venue.image_link,
              'start_time': format_datetime(str(self.start_time), format='full')
              }
          

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))

    def __repr__(self):
      return f'\n<Venue: id: {self.id},\nname: {self.name},\ngenres: {self.genres},\naddress: {self.address},\ncity: {self.city},\nstate: {self.state},\nphone: {self.phone},\nwebsite: {self.website},\nfacebook_link: {self.facebook_link},\nseeking_talent: {self.seeking_talent},\nseeking_description: {self.seeking_description},\nimage_link: {self.image_link}>\n'

    @property
    def serialize(self):
        return {'id': self.id,
              'name': self.name,
              'genres': self.genres.split(','),
              'address': self.address,
              'city': self.city,
              'state': self.state,
              'phone': self.phone,
              'website': self.website,
              'facebook_link': self.facebook_link,
              'seeking_talent': self.seeking_talent,
              'seeking_description': self.seeking_description,
              'image_link' : self.image_link
              }

    @property
    def _get_venues_by_search(self):
      return {"id": self.id,
              "name": self.name,
              "num_upcoming_shows": Show.query.filter(
                Show.start_time > datetime.now(),
                Show.venue_id == self.id
              ).count()
            }

    @property
    def _get_venue_with_show_info(self):
      return {'id': self.id,
              'name': self.name,
              'genres': self.genres,
              'address': self.address,
              'city': self.city,
              'state': self.city,
              'phone': self.phone,
              'website': self.website,
              'facebook_link': self.facebook_link,
              'seeking_talent': self.seeking_talent,
              'seeking_description': self.seeking_description,
              'image_link' : self.image_link,
              'past_shows' : [x._get_show_artist_time for x in Show.query.filter(
                Show.venue_id==self.id,
                Show.start_time < datetime.now()
              ).all()],
              'upcoming_shows': [x._get_show_artist_time for x in Show.query.filter(
                Show.venue_id==self.id,
                Show.start_time > datetime.now()
              ).all()],
              'past_shows_count': Show.query.filter(
                Show.start_time < datetime.now(),
                Show.venue_id == self.id
              ).count(),
              'upcoming_shows_count': Show.query.filter(
                Show.start_time > datetime.now(),
                Show.venue_id == self.id
              ).count()
            }

    @property
    def _get_upcoming_shows_count(self):
      return {'id': self.id,
              'name': self.name,
              'num_upcoming_shows': Show.query.filter(
                Show.start_time > datetime.now(),
                Show.venue_id == self.id
              ).count()
            }

    @property
    def _get_venues_by_city_state(self):
      return {'city' : self.city,
              'state' : self.state,
              'venues' : [x._get_upcoming_shows_count 
                            for x in Venue.query.filter(Venue.city == self.city, Venue.state == self.state)
                          .all()]
              }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))

    def __repr__(self):
      return f'\n<Artist: id: {self.id},\nname: {self.name},\ngenres: {self.genres},\ncity: {self.city},\nstate: {self.state},\nphone: {self.phone},\nwebsite: {self.website},\nfacebook_link: {self.facebook_link},\nseeking_venue: {self.seeking_venue},\nseeking_description: {self.seeking_description},\nimage_link: {self.image_link}>\n'

    @property
    def serialize(self):
        return {'id': self.id,
              'name': self.name,
              'genres': self.genres.split(','),
              'city': self.city,
              'state': self.state,
              'phone': self.phone,
              'website': self.website,
              'facebook_link': self.facebook_link,
              'seeking_venue': self.seeking_venue,
              'seeking_description': self.seeking_description,
              'image_link' : self.image_link
              }

    @property
    def _get_artists_by_id_name(self):
      return {'id': self.id,
              'name': self.name
              }

    @property
    def _get_artists_by_search(self):
      return {"id": self.id,
              "name": self.name,
              "num_upcoming_shows": Show.query.filter(
                Show.start_time > datetime.now(),
                Show.artist_id == self.id
              ).count()
            }

    @property
    def _get_artist_with_show_info(self):
      return {'id': self.id,
              'name': self.name,
              'genres': self.genres,
              'city': self.city,
              'state': self.city,
              'phone': self.phone,
              'website': self.website,
              'facebook_link': self.facebook_link,
              'seeking_venue': self.seeking_venue,
              'seeking_description': self.seeking_description,
              'image_link' : self.image_link,
              'past_shows' : [x._get_show_venue_time for x in Show.query.filter(
                Show.artist_id==self.id,
                Show.start_time < datetime.now()
              ).all()],
              'upcoming_shows': [x._get_show_venue_time for x in Show.query.filter(
                Show.artist_id==self.id,
                Show.start_time > datetime.now()
              ).all()],
              'past_shows_count': Show.query.filter(
                Show.start_time < datetime.now(),
                Show.artist_id == self.id
              ).count(),
              'upcoming_shows_count': Show.query.filter(
                Show.start_time > datetime.now(),
                Show.artist_id == self.id
              ).count()
            }
