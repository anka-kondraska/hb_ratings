"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User
from model import Rating
from model import Movie

from model import connect_to_db, db
from server import app
from datetime import datetime

import re


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    # pattern = "([[:space:]]\(\d\d\d\d\))"
    
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        row_items = row.split("|")
        
        movie_id = row_items[0]
        
        # title = row_items[1][:-7] #Gets rid of the (YYYY) and extra space at the end of title
        raw_title = row_items[1]
        title = re.sub("(\s\(\d\d\d\d\))", '', raw_title)
        title = title.decode("latin-1")
        # print title
        
        raw_data = row_items[2]
        if raw_data:
            released_at = datetime.strptime(raw_data, '%d-%b-%Y')
            # released_at = released_at.strftime('%m-%d-%Y')
        else:
            released_at = None
        
        imdb_url = row_items[4]
        # print "length of URL: ", len(imdb_url)

        movie = Movie(movie_id=movie_id,
                        title=title,
                        released_at=released_at,
                        imdb_url=imdb_url)

        db.session.add(movie)

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    for row in open("seed_data/u.data"):
        row = row.strip()
        row_items = row.split('\t')

        movie_id = row_items[0]
        user_id = row_items[1]
        score = row_items[2]

        rating = Rating(movie_id=movie_id, user_id=user_id, score=score)

        db.session.add(rating)

    db.session.commit()




def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
