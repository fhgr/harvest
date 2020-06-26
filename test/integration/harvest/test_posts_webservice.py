import os
from json import load, loads

import pytest
from fuzzywuzzy import fuzz

from harvest.webservice import get_flask_app


# @Todo lead post not detected-> test_forum_healthunlocked
# @Todo not recognized because of inscriptis -> test_forum_proxer
# @Todo lead post not detected -> test_forum_shift_ms
# @Todo text not recognized -> test_forum_medhelp
# @Todo text not recognized -> test_forum_medschat
# @Todo text not recognized -> test_forum_msworld
# @Todo text not recognized -> test_forum_musiker_board
# @Todo text not recognized -> test_forum_paradisi

@pytest.fixture
def compare():
    def _compare(gold_annotations, response, ignored_element=[], ratio=95):
        for index, gold_annotation in enumerate(gold_annotations, start=0):
            for element in gold_annotation:
                if element not in ignored_element:
                    if element == 'post_text':
                        assert fuzz.ratio(gold_annotation[element]['surface_form'],
                                          response[index][element]['surface_form']) > ratio
                    else:
                        assert gold_annotation[element]['surface_form'] == response[index][element]['surface_form']

    return _compare


@pytest.fixture
def remove_index():
    def _remove_index(response, indexes_to_remove):
        final_response = []
        for index, response_element in enumerate(response, start=0):
            if index not in indexes_to_remove:
                final_response.append(response_element)
        return final_response

    return _remove_index


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


def test_forum_bpdfamily(load_test_data, test_client, compare):
    forum_test_data = load_test_data("bpdfamily.com.message_board.index.php.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user', 'post_link'])


def test_forum_bitdefender(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "community.bitdefender.com.en.discussion.82059.i-noticed-that-the-bitdefender-process-can-be-easily-killed.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])


def test_forum_kaspersky(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "community.kaspersky.com.kaspersky-security-cloud-11.rootkit-scan-not-executed-6849.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_community_scope(load_test_data, test_client, compare):
    forum_test_data = load_test_data("community.scope.org.uk.discussion.68941.disabled-mum.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])


def test_forum_digitalfernsehen(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.digitalfernsehen.de.threads.df-hilferuf.416785..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_ebaumsworld(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.ebaumsworld.com.viewtopic.php.42095.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_glamour(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.glamour.de.t.designertaschen-laber-laber.18136.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, [])


def test_forum_mein_schoener_garten(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.mein-schoener-garten.de.viewtopic.php.4825193.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_nationstates(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.nationstates.net.viewtopic.php.419.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_openoffice(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.openoffice.org.en.forum.viewtopic.php.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user'])


def test_forum_statcounter(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.statcounter.com.threads.best-android-apps-in-uk-2019.79812..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user', 'post_link'])


def test_forum_ubuntuusers(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.ubuntuusers.de.topic.appimage-programm-in-alle-programme-als-icon-a..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user', 'post_link'], ratio=78)


def test_forum_utorrent(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.utorrent.com.topic.23012-check-on-startup..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_videolan(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.videolan.org.viewtopic.php.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, [])


def test_forum_wordreference(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forum.wordreference.com.threads.attuned-to-the-reiki-symbols.3691417..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user'])


def test_forum_worldofplayers(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "forum.worldofplayers.de.forum.threads.1548322-Welchen-Blog-benutzt-man-in-2020.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_futura_sciences(load_test_data, test_client, compare, remove_index):
    forum_test_data = load_test_data("forums.futura-sciences.com.annonces-officielles.78761-moderateurs.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    # Remove the advertisement slots
    response = remove_index(response, [1, 6, 8, 15, 22, 29])
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_macrumors(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forums.macrumors.com.threads.se-or-11.2231616..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_maladiesraresinfo(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forums.maladiesraresinfo.org.post11011.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])


def test_forum_moneysavingexpert(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "forums.moneysavingexpert.com.discussion.6100693.how-do-0-credit-card-balances-work-when-you-have-borrowed-twice.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])


def test_forum_sherdog(load_test_data, test_client, compare):
    forum_test_data = load_test_data("forums.sherdog.com.threads.all-time-goat-poll.3916359..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_kiwifarms(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "kiwifarms.net.threads.the-twitter-pedo-hunter-loli-crusader-community.64404..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user'])


def test_forum_myparkinsons(load_test_data, test_client, compare, remove_index):
    forum_test_data = load_test_data("myparkinsons.org.cgi-bin.forum.topic_show.pl.5256.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    # Remove header that looks exactly like the posts
    response = remove_index(response, [0, 1])
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'], ratio=90)


def test_forum_skyscraperpage(load_test_data, test_client, compare):
    forum_test_data = load_test_data("skyscraperpage.com.forum.showthread.php.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_collegeconfidential(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "talk.collegeconfidential.com.student-here-ask-me-anything.2183693-got-into-nyu-pre-med-intention-ask-me-anything.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_uhrforum(load_test_data, test_client, compare):
    forum_test_data = load_test_data("uhrforum.de.threads.der-yema-fotothread-und-nicht-nur-das.414009..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user'])


def test_forum_blizzard(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "us.forums.blizzard.com.en.wow.t.can-i-transfer-back-to-locked-server-if-i-have-existing-character.505388.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response)


def test_forum_airliners(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.airliners.net.forum.viewtopic.php.1428699.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'], ratio=85)


def test_forum_amsel(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.amsel.de.multiple-sklerose-forum..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_android_hilfe(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.android-hilfe.de.forum.samsung-allgemein.423.faq-diskussion-zum-kauf-samsung-galaxy-s10-s10e-s10-snapdragon-variante.904645.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['user'])


def test_forum_computerbase(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.computerbase.de.forum.threads.ram-empfehlung-fuer-ryzen.1940441..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'], ratio=85)


def test_forum_drwindows(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.drwindows.de.windows-7-allgemein.16340-zufall-entdeckte-problemlsungen.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user', 'post_link'], ratio=89)


def test_forum_fanfiction(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.fanfiction.net.topic.146535.108548484.1.The-About-the-World-Topic.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user'], ratio=75)


def test_forum_gtplanet(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.gtplanet.net.forum.threads.f1-2018-general-discussion.378195..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_hifi(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.hifi-forum.de.viewthread-84-87.html.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_juraforum(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.juraforum.de.forum.t.fahrtkostenerstattung-bei-falschen-rezepten.675629..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'user', 'post_link'])


def test_forum_med1(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.med1.de.forum.beruf-alltag-und-umwelt.corona-eine-gehypde-apokalypse-972190..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])


def test_forum_msconnection(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.msconnection.org.Discussions.f27.t79421.tp1.Does-this-sound-like-MS.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime'])


def test_forum_mumsnet(load_test_data, test_client, compare):
    forum_test_data = load_test_data(
        "www.mumsnet.com.Talk.pregnancy.3749275-Pregnant-with-a-black-mixed-race-with-black-baby.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response)


def test_forum_nairaland(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.nairaland.com.5812914.akeredolu-rejects-plot-impeach-deputy.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['datetime', 'post_link'])


def test_forum_neowin(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.neowin.net.forum.topic.1391546-hello-im-dion..json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['user'])


def test_forum_pistonheads(load_test_data, test_client, compare):
    forum_test_data = load_test_data("www.pistonheads.com.gassing.topic.asp.1858583.json")
    response = test_client.post('/extract_from_html',
                                json={'html': forum_test_data['html'], 'url': forum_test_data['url'],
                                      'gold_standard_format': True})
    response = loads(response.data)
    compare(forum_test_data['gold_standard_annotation'], response, ['post_link'])
