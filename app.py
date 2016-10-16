from flask import Flask, request
from flask import render_template
import json

from goose import Goose
from core.models import *
from newspaper import Article as NewspaperArticle
import sqlalchemy
from sqlalchemy.sql.expression import extract

import ystockquote

from api import get_search_results, get_sentiment_score, get_textblob_sentiment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/sentiment.db'

g = Goose()


@app.route("/getcontent")
def get_content():
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
                    current = NewspaperArticle(article.ArticleURL)
                    current.download()
                    article.ArticleContent = current.text
                    db.session.commit()
                except:
                    print "couldn't parse it"

        article.ArticleScore = (article.ArticleScore + 1) / 2.0
        db.session.commit()
    return "done"

# Example usage: http://localhost:5000/stock/AAPL?startdate=2015-01-01&enddate=2016-10-01
@app.route('/stock/<company>', methods=['GET'])
def get_stock(company):
    start_date = request.args.get("startdate")
    end_date = request.args.get("enddate")

    stock_data = ystockquote.get_historical_prices(company, start_date, end_date)

    return json.dumps([[x, y["Close"]] for x, y in stock_data.iteritems()])

@app.route('/sentiment/<company>', methods=['GET'])
def get_sentiment(company):
    descriptions = get_search_results(company)
    sentiment = get_sentiment_score(descriptions)
    return sentiment


@app.route('/sentiment/graph/<company>', methods=['GET'])
def get_sentiment_graph(company):

    highcharts = [{"data":[]}]
    for x in db.session.execute('''SELECT  date(a.ArticlePublishDate), avg(a.articleScore) from ARTICLE a
     	group by date(a.ArticlePublishDate)
     	order by date(a.ArticlePublishDate) asc
     	'''.format(company)):

        highcharts[0]["data"].append([x[0], x[1]])

    return json.dumps(highcharts)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company = request.form.get("company")
        descriptions = get_search_results(company)
        sentiment = get_sentiment_score(descriptions)

        # text_blob_sentiment = get_textblob_sentiment(descriptions)
        # print sum([x for x in text_blob_sentiment if x != 0]) / len(text_blob_sentiment)

        return render_template("demo.html", company=company, sentiment=sentiment, articles=descriptions)

    return render_template("demo.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
