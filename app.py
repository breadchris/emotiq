from flask import Flask, request
from flask import render_template

from goose import Goose
from core.models import *
from newspaper import Article as NewspaperArticle
import sqlalchemy
from sqlalchemy.sql.expression import extract

from api import get_search_results, get_sentiment, get_textblob_sentiment

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


@app.route('/sentiment/<company>', methods=['GET'])
def get_sentiment(company):
    descriptions = get_search_results(company)
    sentiment = get_sentiment(descriptions)
    return sentiment


@app.route('/sentiment/graph/<company>', methods=['GET'])
def get_sentiment_graph(company):
    article_groups = Article.query.group_by(extract("day", Article.ArticlePublishDate)).all()
    for articles in article_groups:
        print articles

        """
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
    """
    """
    articles = Article.
    for article in articles:
        thistime = article.ArticlePublishDate
        rowsdict[Product.query.get(row['product_id']).title][int(time.mktime(thistime.timetuple())) * 1000] = row[
            'count']
        # hack for rows with 0 calls, initalize the previous and next hour if it doesn't exist
        # we are abusing the beautiful defaultdict here.
        # dont let the feminists know.
        rowsdict[Product.query.get(row['product_id']).title][
            int(time.mktime((thistime - timedelta(days=1)).timetuple())) * 1000]
        if not (thistime + timedelta(hours=1)) > datetime.now():  # no time travel allowed
            rowsdict[Product.query.get(row['product_id']).title][
                int(time.mktime((thistime + timedelta(days=1)).timetuple())) * 1000]
    # extend the graph to now with null values
    # highcharts wants sorted data
    rowsdict = OrderedDict(sorted(rowsdict.items(), key=lambda x: x[0]))
    series = []
    for prod, datapoints in rowsdict.iteritems():
        series.append({'name': prod, 'data': sorted(datapoints.items(), key=lambda x: x[0])})
    return json.dumps(series)
    """
    return render_template("demo.html")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company = request.form.get("company")
        descriptions = get_search_results(company)
        sentiment = get_sentiment(descriptions)

        # text_blob_sentiment = get_textblob_sentiment(descriptions)
        # print sum([x for x in text_blob_sentiment if x != 0]) / len(text_blob_sentiment)

        return render_template("demo.html", company=company, sentiment=sentiment, articles=descriptions)

    return render_template("demo.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
