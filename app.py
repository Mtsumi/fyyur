#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.String)
    seeking_description = db.Column(db.String)
    artists = db.relationship("Show", backref="venue", lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


db.create_all()

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.String)
    seeking_description = db.Column(db.String)
    venue = db.relationship("Show", backref="artist", lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'
db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show (db.Model):
        __tablename__ = 'Show'
        id = db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
        artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),primary_key=True,nullable=False)
        venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),primary_key=True,nullable=False)
        start_time = db.Column(db.Date,nullable=False)

        def __repr__(self):
          return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'
db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  current_time = datetime.now().strftime('%m/%d/%Y')
  
  venue_data=Venue.query.all()
  data =[]
  for venue in venue_data:
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.start_time>current_time).all()),
      }]
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  search_res = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data =[]

  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  
  for results in search_res:
   
    data.append({
     "id":results.id,
     "name":results.name,
     "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == results.id).filter(Show.start_time > datetime.now()).all()),

    })
  count = len(search_res)
  response = {
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_time = datetime.now().strftime('%m/%d/%Y')
  venquery = Venue.query.get(venue_id)
  
  if not venquery: 
      return render_template('errors/404.html')
  data=[]
  past_shows=[]
  upcoming_shows=[]
  
  past_shows_query= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<current_time).all()
  
  upcoming_shows_query= db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>current_time).all()
  
  for show in past_shows_query:
    artist = db.session.query(Artist).get(show.venue_id)
    past_shows.append({
     "artist_id":artist.id,
     "artist_name": artist.name,
     "artist_image_link": artist.image_link,
     "start_time": show.start_time.strftime('%m/%d/%Y')
    })
  for show in upcoming_shows_query:
    artist = db.session.query(Artist).get(show.venue_id)
    upcoming_shows.append({
     "artist_id":artist.id,
     "artist_name": artist.name,
     "artist_image_link": artist.image_link,
     "start_time": show.start_time.strftime('%m/%d/%Y')
    })
  data.append({
    "id": venquery.id,
    "name": venquery.name,
    "genres": venquery.genres,
    "address": venquery.address,
    "city": venquery.city,
    "state": venquery.state,
    "phone": venquery.phone,
    "website_link": venquery.website,
    "facebook_link": venquery.facebook_link,
    "seeking_talent": venquery.seeking_talent,
    "seeking_description": venquery.seeking_description,
    "image_link": venquery.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  })

  data = list(filter(lambda d: d['id'] == venue_id,data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  
  if form.validate():
      
    data ={
      "name":request.form.get("name"),
      "city":request.form.get("city"),
      "state":request.form.get("state"),
      "address":request.form.get("address"),
      "phone":request.form.get("phone"),
      "image_link":request.form.get("image_link"),
      "facebook_link":request.form.get("facebook_link"),
      "genres":request.form.getlist("genres"),
      "website":request.form.get("website_link"),
      "seeking_talent":request.form.get("seeking_talent"),
      "seeking_description":request.form.get("seeking_description")
    }
    new_venue=Venue(
        name=data["name"],
        city=data["city"],
        state=data["state"],
        address=data["address"],
        phone=data["phone"],
        genres=data["genres"],
        image_link=data["image_link"],
        facebook_link=data["facebook_link"],
        website=data["website"],
        seeking_talent=data["seeking_talent"],
        seeking_description=data["seeking_description"])


  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as err:
      print(err)
      db.session.rollback()
      flash('Venue ' + request.form['name'] + ' was not successfully listed!')
  finally:
      db.session.close()

  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:

    venue = Venue.query.filter(venue_id == venue_id).all()
    db.session.delete(venue)
    db.session.commit()
    flash("Venue has been deleted successfully".format(
            venue[0]['name']))
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist_data = Artist.query.all()
  data = []
  for artist in artist_data:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  # TODO: replace with real data returned from querying the database

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_res = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []

  

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  for result in search_res:
    
    data.append({
      "id": result.id,
      "name": result.name,
    })
  count = len(search_res)
  response = {
    "count": count,
    "data": data
  }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artquery = Artist.query.get(artist_id)
  data = []
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now().strftime('%m/%d/%Y')
  past_shows_query = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time <= current_time).all()
  upcoming_shows_query = Show.query.filter_by(artist_id=artist_id).filter(Show.start_time > current_time).all()

  for show in past_shows_query:
    venue = Venue.query.get(show.artist_id)
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })
  for show in upcoming_shows_query:
    venue = Venue.query.get(show.artist_id)
    upcoming_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_image_link": venue.image_link,
      "start_time": show.start_time.strftime('%m/%d/%Y')
    })
  data.append({
    "id": artquery.id,
    "name": artquery.name,
    "genres": artquery.genres,
    "city": artquery.city,
    "state": artquery.state,
    "phone": artquery.phone,
    "website": artquery.website,
    "facebook_link": artquery.facebook_link,
    "seeking_description": artquery.seeking_description,
    "image_link": artquery.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  })


  data_list = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data_list)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = db.session.query(Artist).get(artist_id)
  
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Artist was successfully updated!')

  except Exception as err:
    print(err)
    flash('An error occurred. Artist could not be changed.')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))
 
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).get(venue_id)
  if venue: 
      form.name.data = venue.name
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.address.data = venue.address
      form.genres.data = venue.genres
      form.facebook_link.data = venue.facebook_link
      form.image_link.data = venue.image_link
      form.website_link.data = venue.website
      form.seeking_talent.data = venue.seeking_talent
      form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  venue = db.session.query(Venue).get(venue_id)
  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_venue = True if 'seeking_venue' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Venue' + request.form['name'] + 'was successfully updated!')

  except Exception as err:
    print(err)
    flash('An error occurred. Venue' + request.form['name'] + 'could not be changed.')
    db.session.rollback()
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  if form.validate():
  
    data = {
      "name": request.form.get("name"),
      "city": request.form.get("city"),
      "state": request.form.get("state"),
      "phone": request.form.get("phone"),
      "genres": request.form.getlist("genres"),
      "facebook_link": request.form.get("facebook_link"),
      "image_link": request.form.get("image_link"),
      "website": request.form.get("website_link"),
      "seeking_venue":"seeking_venue" in request.form,
      "seeking_description": request.form.get("seeking_description")
    }
    artist = Artist(
        name=data["name"],
        city=data["city"],
        state=data["state"],
        phone=data["phone"],
        genres=data["genres"],
        facebook_link=data["facebook_link"],
        image_link=data["image_link"],
        website=data["website"],
        seeking_venue=data["seeking_venue"],
        seeking_description=data["seeking_description"])
  
  try:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as err:
      print(err)
      db.session.rollback()
      flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')
  finally:
     db.session.close()
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shwquery = Show.query.all()
  response =[]
  for shows in shwquery:
      data = {
            "artist_id": shows.artist_id,
            "artist_name": shows.artist.name,
            "venue_id": shows.venue_id,
            "venue_name": shows.venue.name,
            "artist_image_link": shows.artist.image_link,
            "start_time": shows.start_time.strftime('%Y-%m-%d %H:%I')
        }
      response.append(data)
  return render_template('pages/shows.html', shows=response)
 

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # inserting form data as a new Show record in the db
  try:
    data = {
      "artist_id": request.form.get("artist_id"),
      "venue_id": request.form.get("venue_id"),
      "start_time": request.form.get("start_time")

    }
    show = Show(artist_id=data["artist_id"], venue_id=data["venue_id"], start_time=data["start_time"])
  # on successful db insert, flash success
  
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show was unsuccessfully listed!')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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