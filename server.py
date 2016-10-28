"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.orm import joinedload

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    # return a
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def user_info(user_id):
    """Show information about user."""

    user_info = User.query.filter_by(user_id=user_id).options(joinedload('ratings')).first()

    ratings_list = user_info.ratings

    # ratings_list = db.session.query(Rating.rating_id, Rating.score, Rating.movie_id, Movie.title, Rating.user_id).join(Movie).filter(Rating.movie_id == Movie.movie_id).filter(Rating.user_id == user_id).all()

    # ratings_list = movie_list.ratings

    return render_template("user_info.html", user_info=user_info,
                                            ratings_list=ratings_list)

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def movie_info(movie_id):
    """Show information about movie."""
    # if 'login_user_id' in session.keys():
    #     login_user_id = session['login_user_id']
    #     print "session", session.keys()
    #     print login_user_id

    movie_info = Movie.query.filter_by(movie_id=movie_id).options(joinedload('ratings')).first()

    ratings_list = movie_info.ratings

    if 'login_user_id' in session.keys():
        login_user_id = session['login_user_id']

        users_rating = []

        for rating in ratings_list:
            if rating.user.user_id == login_user_id:
                users_rating.append(rating)

        users_rating = users_rating[0]
    else:
        users_rating = None

    return render_template("movie_info.html", movie_info=movie_info,
                                            ratings_list=ratings_list,
                                            users_rating=users_rating)


@app.route('/new_rating', methods=['POST'])
def new_rating():
    """Processes new rating form on movie description page."""

    new_score = request.form.get('new_score') #This will grab the value from dropdown form
    movie_id = request.form.get('movie_id')

    login_user_id = session['login_user_id']

    new_rating = Rating(movie_id=movie_id, user_id=login_user_id, score=new_score)

    db.session.add(new_rating)

    db.session.commit()

    flash("Thank you for rating this movie!")

    return redirect(url_for('movie_info', movie_id=movie_id))


@app.route('/register', methods=['GET'])
def register_form():
    """Show register_form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Processes register_form."""

    username = request.form.get('username')
    password = request.form.get('password')
    age = request.form.get('age')
    zipcode = request.form.get('zipcode')


    search_user = db.session.query(User)

    if search_user.filter_by(email=username).scalar() is None:

        new_user = User(email=username, password=password, age=age, zipcode=zipcode)

        db.session.add(new_user)

        db.session.commit()

        login_user_id = db.session.query(User.user_id).filter_by(email=username, password=password).scalar()

        session['login_user_id'] = login_user_id

        flash("Thank you for signing up! You are logged in.")

    return redirect(url_for('user_info', user_id=login_user_id))


@app.route('/login', methods=['GET'])
def login_form():
    """Show login_form."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Processes register_form."""

    username = request.form.get('username')
    password = request.form.get('password')

    search_user = db.session.query(User)

    if search_user.filter_by(email=username, password=password).scalar() is not None:

        login_user_id = db.session.query(User.user_id).filter_by(email=username, password=password).scalar()

        session['login_user_id'] = login_user_id

        flash("Logged in.")

        return redirect(url_for('user_info', user_id=login_user_id))

    else:

        flash("Your password doesn't match our database!")
        
        return redirect('/')


@app.route('/logout', methods=['GET'])
def logout_process():
    """Processes logging out."""

    del session['login_user_id']

    flash("You have logged out!")

    return redirect('/')



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5003)
