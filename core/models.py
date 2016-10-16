import datetime
from sqlalchemy.dialects.mysql import *
from app import app
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)

class Article(db.Model):
	__tablename__ = 'ARTICLE'
	ArticleID = db.Column(db.Integer, primary_key=True)
	ArticleURL = db.Column(db.Text)
	ArticleContent = db.Column(db.Text)
	ArticleScore = db.Column(db.Float)
	ArticleTitle = db.Column(db.Text)
	ArticlePublishDate = db.Column(db.DateTime)

	def __init__(self, ArticleURL, ArticleTitle, ArticleScore, ArticlePublishDate):
		self.ArticleURL = ArticleURL
		self.ArticleTitle = ArticleTitle
		self.ArticleScore = ArticleScore
		self.ArticlePublishDate = ArticlePublishDate

	def __repr__(self):
		return "<" + self.ArticleURL + " @ " + self.ArticleScore + ">"