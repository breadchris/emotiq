import httplib, urllib, base64

def get_search_results(query):
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '9a624ee241da40d09cb6a3c687e261ea',
    }

    params = urllib.urlencode({
        # Request parameters
        'q': query,
        'count': '10',
        'offset': '0',
        'mkt': 'en-us',
        'safeSearch': 'Moderate',
    })

    try:
        conn = httplib.HTTPSConnection('api.cognitive.microsoft.com')
        conn.request("GET", "/bing/v5.0/news/search?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
