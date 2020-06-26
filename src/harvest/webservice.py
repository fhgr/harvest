from flask import Flask
from flask import request
from flask import jsonify
import hashlib

import harvest.posts as posts
import harvest.extract as extract
from harvest.evaluation.dragnet import get_posts
from harvest.evaluation.goldstandard.calculate_position import get_start_end_for_post

app = Flask('harvest')


@app.route('/extract_from_html', methods=['POST'])
def events():
    forum = request.json
    post_0 = posts.extract_posts(forum)

    if 'gold_standard_format' in forum and forum['gold_standard_format']:
        results = []
    else:
        results = {'entities': {}}
    if post_0['text_xpath_pattern']:
        search_start_index = 0
        for post_1 in extract.extract_posts(
                forum['html'],
                forum['url'],
                post_0['text_xpath_pattern'],
                post_0['url_xpath_pattern'],
                post_0['date_xpath_pattern'],
                post_0['user_xpath_pattern'], result_as_datetime=False):

            post_dict = {
                'user': {'surface_form': post_1.user},
                'datetime': {'surface_form': post_1.date},
                'post_link': {'surface_form': post_1.url},
                'post_text': {'surface_form': post_1.post}
            }

            # doc_id = hashlib.md5(forum['url'].encode()).hexdigest()
            doc_id = forum['url']

            if 'gold_standard_format' in forum and forum['gold_standard_format']:
                results.append(post_dict)
            else:
                if 'text' in forum:
                    new_search_start_index = get_start_end_for_post(post_dict, forum['text'], search_start_index,
                                                                    fuzzy_search=True)
                    if new_search_start_index > 0:
                        search_start_index = new_search_start_index

                results['entities'][doc_id] = results['entities'].get(doc_id, [])
                for item in ['user', 'datetime', 'post_link', 'post_text']:
                    result = {
                        'doc_id': doc_id,
                        'type': item,
                        'surface_form': post_dict[item]['surface_form']
                    }
                    if 'start' in post_dict[item] and 'end' in post_dict[item]:
                        result['start'] = post_dict[item]['start']
                        result['end'] = post_dict[item]['end']

                    results['entities'][doc_id].append(result)

    return jsonify(results)


@app.route('/dragnet_extract_from_html', methods=['POST'])
def events_dragnet():
    forum = request.json

    posts = get_posts(forum['html'])
    # doc_id = hashlib.md5(forum['url'].encode()).hexdigest()
    doc_id = forum['url']

    result = {'entities': {}}
    result['entities'][doc_id] = result['entities'].get(doc_id, [])
    for post in posts:
        result['entities'][doc_id].append({
            'doc_id': doc_id,
            'type': 'post_text',
            'surface_form': post
        })

    return jsonify(result)


def get_flask_app():
    return app


if __name__ == '__main__':
    app.run(port=5000, debug=True)
