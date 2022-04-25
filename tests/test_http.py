from simplehttp.SimpleHttpClient import SimpleHttpClient


def test_client():
    client = SimpleHttpClient()
    query = client.get_request(url = "http://www.google.com")
    print(query)
    assert query is not None
