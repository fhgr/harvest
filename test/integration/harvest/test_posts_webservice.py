import pytest
import os
from json import load, loads
from fuzzywuzzy import fuzz

from harvest.webservice import get_flask_app


@pytest.fixture
def compare():
    def _compare(gold_annotations, response, ignored_element=[]):
        for index, gold_annotation in enumerate(gold_annotations, start=0):
            for element in gold_annotation:
                if element not in ignored_element:
                    if element == 'post_text':
                        assert fuzz.ratio(gold_annotation[element]['surface_form'],
                                          response[index][element]['surface_form']) > 98
                    else:
                        assert gold_annotation[element]['surface_form'] == response[index][element]['surface_form']

    return _compare


@pytest.fixture
def load_test_data():
    def _load_test_data(file_name):
        file_path = os.path.join(os.path.dirname(__file__), '../../../goldDocumentsFinal', file_name)
        with open(file_path) as f:
            return load(f)

    return _load_test_data


@pytest.fixture(scope='module')
def test_client():
    app = get_flask_app()
    app.config['TESTING'] = True

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


def test_forum_angelman(load_test_data, test_client, compare):
    forum_test_data = load_test_data("blog.angelman-asa.org.read.php.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])
