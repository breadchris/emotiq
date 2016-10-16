import datetime
from sqlalchemy.dialects.mysql import *
from flask.ext.sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class Article(db.Model):
	__tablename__ = 'articles'
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.Text)
	content = db.Column(db.Text)
	sentiment = db.Column(db.Float)
	title = db.Column(db.Text)

	def __init__(self, url, title, content, sentiment):
		self.url = url
		self.title = title
		self.content = content
		self.sentiment = sentiment

	def __repr__(self):
		return self.title + ", " + self.url + " @ " + self.sentiment