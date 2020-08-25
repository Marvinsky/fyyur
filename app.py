#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from util import format_datetime
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify, 
  abort
)
from models import db, Venue, Artist, Show
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  unique_city_state = Venue.query.distinct(Venue.city, Venue.state).all()

  data = [x._get_venues_by_city_state for x in unique_city_state]
  print("data: ",data)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  term = request.form.get('search_term', '')
  search_result = Venue.query.filter(Venue.name.ilike('%'+ term +'%')).all()
  response = {'count': len(search_result),
              'data': [x._get_venues_by_search for x in search_result]
            }
  print("response: ", response)
  return render_template('pages/search_venues.html', results=response, search_term=term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  data = Venue.query.filter(Venue.id == venue_id)[0]._get_venue_with_show_info
  print(data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue_form = VenueForm()

  try:
    new_venue = Venue(
      name = venue_form.name.data,
      genres = ",".join(venue_form.genres.data),
      address = venue_form.address.data,
      city = venue_form.city.data,
      state = venue_form.state.data,
      phone = venue_form.phone.data,
      facebook_link = venue_form.facebook_link.data,
      image_link = venue_form.image_link.data
    )
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue_to_delete = Venue.query.filter(Venue.id==venue_id).one()
    name = venue_to_delete.name
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash("Venue {} has been delete successfully.".format(name))
  except:
    db.session.rollback()
    flash("The delete of {} failed!".format(name))
    abort(404)
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({"success": True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = [x._get_artists_by_id_name for x in Artist.query.all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term', '')
  search_result = Artist.query.filter(Artist.name.ilike('%'+ term +'%')).all()
  response = {'count': len(search_result),
              'data': [x._get_artists_by_search for x in search_result]
            }
  print("response: ", response)
  return render_template('pages/search_artists.html', results=response, search_term=term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  print("artist_id = ", artist_id)
  data = Artist.query.filter(Artist.id == artist_id).one_or_none()._get_artist_with_show_info
  print("data_artist_id: ", data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_form = ArtistForm()
  artist_to_update = Artist.query.filter_by(id=artist_id).one_or_none()
  if artist_to_update is None:
    abort(404)

  artist = artist_to_update.serialize
  form = ArtistForm(data=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_form = ArtistForm(request.form)
  try:
    update_artist = Artist.query.filter(Artist.id==artist_id).one()
    update_artist.name = artist_form.name.data
    update_artist.genres = ",".join(artist_form.genres.data)
    update_artist.city = artist_form.city.data
    update_artist.state = artist_form.state.data
    update_artist.phone = artist_form.phone.data
    update_artist.facebook_link = artist_form.facebook_link.data
    update_artist.image_link = artist_form.image_link.data

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_form = VenueForm()
  venue_update = Venue.query.filter(Venue.id==venue_id).one_or_none()

  if venue_update is None:
    abort(404)

  venue = venue_update.serialize
  form = VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  venue_form = VenueForm(request.form)

  try:
    venue_to_update = Venue.query.filter(Venue.id==venue_id).one()
    venue_to_update.name = venue_form.name.data
    venue_to_update.address = venue_form.address.data
    venue_to_update.genres = ",".join(venue_form.genres.data)
    venue_to_update.city = venue_form.city.data
    venue_to_update.state = venue_form.state.data
    venue_to_update.phone = venue_form.phone.data
    venue_to_update.facebook_link = venue_form.facebook_link.data
    venue_to_update.image_link = venue_form.image_link.data

    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist_form = ArtistForm()

  try:
    new_artist = Artist(
      name = artist_form.name.data,
      genres = artist_form.genres.data,
      city = artist_form.city.data,
      state = artist_form.state.data,
      phone = artist_form.phone.data,
      facebook_link = artist_form.facebook_link.data,
      image_link = artist_form.image_link.data
    )
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [x._get_shows for x in Show.query.all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  new_show = ShowForm()

  try:
    new_show = Show(
      artist_id = new_show.artist_id.data,
      venue_id = new_show.venue_id.data,
      start_time = new_show.start_time.data
    )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
