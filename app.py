import json

from flask import Flask
from flask import render_template
from bson import json_util
from goose import Goose
from newspaper import Article
from core.models import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/sentiment.db'

g = Goose()

@app.route("/getcontent")
def getContent():
	articles = Article.query.all()
	for article in articles:
		if article.ArticleContent == '':
			print article.ArticleID
			try:
				current = g.extract(url=article.ArticleURL)
				article.ArticleContent = current.cleaned_text
				db.session.commit()
			except:
				try:
					current = Article(article.ArticleURL)
					current.download()
					article.ArticleContent = current.text
					db.session.commit()
				except:
					print "couldn't parse it"
	return "done"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/donorschoose/projects")
def donorschoose_projects():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS, limit=100000)
    #projects = collection.find(projection=FIELDS)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)