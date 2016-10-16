from flask import Flask, request
from flask import render_template
import json
import time
import datetime
import requests
from goose import Goose
from core.models import *
from newspaper import Article as NewspaperArticle
import sqlalchemy
from sqlalchemy.sql import func

import ystockquote

from api import get_search_results, get_sentiment_scores, get_textblob_sentiment

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/sentiment.db'

g = Goose()


def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            print x['name']
            return x['name']


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

        article.ArticleScore = (article.ArticleScore * 2.0) - 1
        db.session.commit()
    return "done"


def get_timestamp(date):
    if "T" in date:
        date = date.split("T")[0]
    date_parts = date.split("-")
    day_datetime = (int(date_parts[0], 10), int(date_parts[1], 10), int(date_parts[2], 10), 0, 0, 0, 0, 0, 0)
    return time.mktime(day_datetime)


# Example usage: http://localhost:5000/stock/AAPL?startdate=2015-01-01&enddate=2016-10-01
@app.route('/stock/<company>', methods=['GET'])
def get_stock(company):
    start_date = request.args.get("startdate")
    end_date = request.args.get("enddate")

    stock_data = ystockquote.get_historical_prices(company, start_date, end_date)

    stock_return_data = []
    for date, score in stock_data.iteritems():
        stock_return_data.append([get_timestamp(date), float(score["Close"])])

    stock_return_data = sorted(stock_return_data)
    return json.dumps(stock_return_data)


@app.route('/sentiment/<company>', methods=['GET'])
def get_sentiment(company):
    descriptions, articles_with_images = get_search_results(company)
    sentiments = get_sentiment_scores([x["description"] for x in descriptions])
    sentiment = sum(sentiments) / len(sentiments)
    return sentiment

@app.route('/sentiment/graph/<company>', methods=['GET'])
def get_sentiment_graph(company):
    start_date = request.args.get("startdate")
    end_date = request.args.get("enddate")

    articles, articles_with_images = get_search_results(company)

    descriptions = []
    for article in articles:
        descriptions.append(article["description"])
    sentiments = get_sentiment_scores(descriptions)

    article_parsed = {}
    for n, article in enumerate(articles):
        article_timestamp = get_timestamp(article["datePublished"])
        if article_timestamp not in article_parsed.keys():
            article_parsed[article_timestamp] = []
        article_parsed[article_timestamp].append(sentiments[n])

    highcharts_data = []
    for datetime, scores in article_parsed.iteritems():
        highcharts_data.append([datetime, sum(scores) / len(scores)])

    highcharts_data = sorted(highcharts_data)
    senti_accum_data = []
    accum = 0
    for data in highcharts_data:
        accum = data[1] - 0.5
        senti_accum_data.append([data[0], accum])
    return json.dumps(senti_accum_data)


@app.route('/phrases/<company>', methods=['GET'])
def get_key_phrases(company):
    articles, articles_with_images = get_search_results(company)
    key_phrases = get_text_topics([a["description"] for a in articles])
    return None

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        company = request.form.get("company")
        descriptions,articles_with_images = get_search_results(company)
        sentiments = get_sentiment_scores([x["description"] for x in descriptions])
        sentiment = sum(sentiments) / len(sentiments)

        # text_blob_sentiment = get_textblob_sentiment(descriptions)
        # print sum([x for x in text_blob_sentiment if x != 0]) / len(text_blob_sentiment)

        start_date = "2016-10-02"
        end_date = "2016-10-16"
        return render_template("demo.html", company=company, sentiment=sentiment, imaged_articles=articles_with_images,\
                               startdate=start_date, enddate=end_date)

    descriptions,articles_with_images = get_search_results("AAPL")
    return render_template("demo.html", imaged_articles=articles_with_images)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if len(request.form.get("company")) <= 4:
            topic_name = get_symbol(request.form.get("company").upper())
            company_stock_symbol = request.form.get("company").upper()
            company_stock_price = ystockquote.get_all(request.form.get("company").upper())["price"]
        else: 
        	topic_name = request.form.get("company").title()
        	company_stock_symbol = False
        	company_stock_price = False
        company = request.form.get("company")
        descriptions,articles_with_images = get_search_results(company)
        sentiments = get_sentiment_scores([x["description"] for x in descriptions])
        sentiment = sum(sentiments) / len(sentiments)

        # text_blob_sentiment = get_textblob_sentiment(descriptions)
        # print sum([x for x in text_blob_sentiment if x != 0]) / len(text_blob_sentiment)

        return render_template("index.html", company=company, topic_name=topic_name, symbol=company_stock_symbol, price=company_stock_price, sentiment=sentiment, imaged_articles=articles_with_images)
    company_stock_price = ystockquote.get_all("AAPL")["price"]
    descriptions,articles_with_images = get_search_results("AAPL")
    return render_template("index.html", imaged_articles=articles_with_images, price=company_stock_price)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
