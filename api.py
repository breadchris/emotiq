import urllib, base64, requests, json
from textblob import TextBlob

def get_search_results(query):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '9a624ee241da40d09cb6a3c687e261ea',
    }

    params = urllib.urlencode({
        # Request parameters
        'q': query,
        'category': 'stocks',
        'count': '40',
        'offset': '0',
        'mkt': 'en-us',
        'safeSearch': 'Moderate',
    })

    r = requests.get('https://api.cognitive.microsoft.com/bing/v5.0/news/search?%s' % params, headers=headers)
    print r.text
    news_articles = json.loads(r.text)

    article_urls = []
    article_descriptions = []
    for article in news_articles["value"]:
        article_urls.append(article["url"])
        article_descriptions.append(article["description"])

    article_thumbnails = []
    for article in news_articles["value"]:
        if 'image' in article.keys() and len(article_thumbnails) < 8:
            article_thumbnails.append([article["name"], article["url"], article["image"]["thumbnail"]["contentUrl"], article["description"]])
    print article_thumbnails
    # TODO return urls instead... return article_descriptions
    return article_descriptions, article_thumbnails

def get_textblob_sentiment(text_list):
    sentiments = []
    for text in text_list:
        blob = TextBlob(text)
        for sentence in blob.sentences:
            sentiments.append(sentence.sentiment.polarity)

    return sentiments

def get_sentiment_score(text_list):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': '03283dc946e843f3881069b78bd6b20a',
    }

    params = {
        'documents': []
    }

    for n, text in enumerate(text_list):

        text_info = {
            "language": "en",
            "id": str(n),
            "text": text

        }
        params['documents'].append(text_info)

    params = json.dumps(params)
    r = requests.post('https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment', data=params, headers=headers)
    sentiments = json.loads(r.text)["documents"]
    return (sum([x["score"] for x in sentiments]) / len(sentiments)) * 2 - 1
