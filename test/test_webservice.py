import requests
import json


def query():
    service_url = 'http://localhost:5000/dragnet_extract_from_html'

    with open('./goldDocumentsFinal/blog.angelman-asa.org.read.php.json') as gold_document:
        data = json.load(gold_document)
        test_url = data['url']
        test_html = data['html']

        data = {'url': test_url, 'html': test_html}

        try:
            response = requests.post(service_url, json=data)
        except Exception as exception:
            print(f"Query failed: {exception}")
            response = None

        response_dict = json.loads(response.text)
        print(f"Response: {response_dict['entities']}")
        return response_dict


if __name__ == '__main__':
    query()
