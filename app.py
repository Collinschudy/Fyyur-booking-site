#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from wtforms import ValidationError
from flask_wtf import Form
import datetime
# from datetime import datetime
import sys
from forms import *
from models import *

from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = []
  latest_time = datetime.datetime.now()
  venue_locations = Venue.query.distinct(Venue.city, Venue.state)

  for location in venue_locations:
    cities_and_states = []
    venues = Venue.query.filter_by(city=location.city).filter_by(state=location.state).all()
    for venue in venues:
      
      cities_and_states.append({
        'id': venue.id,
        'name': venue.name,
        'upcoming_shows_count': len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>latest_time).all())
      })

    data.append({
      'city': location.city,
      'state': location.state,
      'venues':cities_and_states
    })
  
  return render_template('pages/venues.html', areas=data)

 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  latest_time = datetime.datetime.now()
  data = []
  search_term = request.form.get('search_term', '')
  search_venues = Venue.query.filter(Venue.name.ilike('%'+ search_term + '%')).all()

  for venue in search_venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'upcoming_shows_count': len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>latest_time).all())
    })
  response={
    "count": len(search_venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
    return redirect(url_for('index'))

  else:
    shows = venue.shows
    upcoming_shows = []
    past_shows = []
    latest_time = datetime.datetime.now()
    for show in shows:
      show.artist_name = show.arist.name
      show.artist_image_link = show.artist.image_link
      
      if show.start_time > latest_time:
        upcoming_shows.append(show)
        upcoming_shows_count = len(upcoming_shows)
      else:
        past_shows.append(show)
        past_shows_count = len(past_shows)

      venue.upcoming_shows = upcoming_shows
      venue.upcoming_shows_count = upcoming_shows_count
      venue.past_shows = past_shows
      venue.past_shows_count = past_shows_count

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  genres = form.genres.data
  if form.validate():
    try:
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data, 
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        facebook_link = form.facebook_link.data
      )
    


      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + form.name.data + ' was successfully listed!')

    except Exception as e:
      db.session.rollback()
      print(sys.exc_info())
      flash(e)
      print(form.genres.data)
      flash('An error occurred. Venue, ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    print(form.errors)
    flash('oops, An error occurred. Venue ' + form.name.data + ' could not be listed, sorry.')

 
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The Venue was deleted successfully')
  except:
    db.session.rollback()
    flash('oops!, Delete operation failed due to an error.')
  finally:
    db.session.close()
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  latest_time = datetime.datetime.now()
  search_term = request.form.get('search_term', '')
  artists_search = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
 
  response={
    "count": len(artists_search),
    "data": []
  }
  for artist in artists_search:
    upcoming_shows_count = 0
    shows = Show.query.filter_by(artist_id=artist_id).all()
    for show in shows:
      if show.start_time > latest_time:
        upcoming_shows_count += 1
    
    response['data'].append({
      'id': artist.id,
      'name': artist.name,
      'upcoming_shows_count': upcoming_shows_count
    })
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  latest_time = datetime.datetime.now()
  if not artist:
    return render_template('error/404.html')
  else:
    shows = artist.shows
    upcoming_shows = []
    past_shows = []

    for show in shows:
      show.venue_name = show.venue.name
      show.venue_image_link = show.venue.image_link
      if show.start_time > latest_time:
        upcoming_shows.append(show)
      else:
        past_shows.append(show)
 
  artist.upcoming_shows = upcoming_shows
  artist.upcoming_shows_count = len(upcoming_shows)
  artist.past_shows = past_shows
  artist.past_shows_count = len(past_shows)

  return render_template('pages/show_artist.html', artist=artist)

@app.route("/artists/<artist_id>/delete", methods=["GET"])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Artist " + artist.name+ " was deleted successfully!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Delete operation failed.')
    finally:
        db.session.close()

    return redirect(url_for('index'))
 
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      db.session.add(artist)
      db.session.commit()
      flash('Artist, ' + form.name.data + 'was updated successfully!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('oops, update failed.')
    finally:
      db.session.close()
  else:
    flash('update failed. Reason: ' + form.errors)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  
  if form.validate():
    try:
      venue = Venue.query.get(artist_id)
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      db.session.add(venue)
      db.session.commit()
      flash('Venue, ' + form.name.data + 'was updated successfully!')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('oops, update failed.')
    finally:
      db.session.close()
  else:
    flash('update failed. Reason: ' + form.errors)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.validate():
    try:
      new_artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data, 
        seeking_venue = True if form.seeking_venue.data == 'Yes' else False,
        seeking_description = form.seeking_description.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        facebook_link = form.facebook_link.data
      )
    


      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')

    except Exception as e:
      db.session.rollback()
      print(sys.exc_info())
      flash(e)
      flash('An error occurred. Artist, ' + form.name.data + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash('oops, An error occurred. Venue ' + form.name.data + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  shows = Show.query.all()
  for show in shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))
    })

 
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
    
  if form.validate():
    try:
      new_show = Show(
              artist_id=form.artist_id.data,
              venue_id=form.venue_id.data,
              start_time=form.start_time.data
          )
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')

    except Exception as e:
      db.session.rollback()
      print(sys.exc_info())
      flash('Show was not successfully listed.')

    finally:
          db.session.close()
  else:
    print(form.errors)
    flash('Oops, something went wrong!')

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
