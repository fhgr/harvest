from flask import Flask
from flask import request
from flask import jsonify
import hashlib

import posts
import extract
from harvest.evaluation.dragnet import get_posts


app = Flask('harvest')


@app.route('/extract_from_html', methods=['POST'])
def events():
    forum = request.json
    post_0 = posts.extract_posts(forum)

    print(forum['html'])

    results = {'entities': {}}
    for post_1 in extract.extract_posts(
            forum['html'],
            forum['url'],
            post_0['xpath_pattern'],
            post_0['url_xpath_pattern'],
            post_0['date_xpath_pattern'],
            post_0['user_xpath_pattern']):

        post_dict = {
            'user': post_1.user,
            'datetime': post_1.date,
            'post_link': post_1.url,
            'post_text': post_1.post
        }

        # print(f"post dict: {post_dict}\n")

        # doc_id = hashlib.md5(forum['url'].encode()).hexdigest()
        doc_id = forum['url']

        results['entities'][doc_id] = results['entities'].get(doc_id, [])
        for item in ['user', 'datetime', 'post_link', 'post_text']:

            result = {
                'doc_id': doc_id,
                'type': item,
                'surface_form': post_dict[item]
            }
            # print(result['type'])
            # print(result['surface_form'])
            # print("\n")

            results['entities'][doc_id].append(result)

    return jsonify(results)


@app.route('/dragnet_extract_from_html', methods=['POST'])
def events_dragnet():
    forum = request.json

    posts = get_posts(forum['html'])
    doc_id = hashlib.md5(forum['url'].encode()).hexdigest()

    result = {'entities': {}}
    result['entities'][doc_id] = result['entities'].get(doc_id, [])
    for post in posts:
        result['entities'][doc_id].append({
            'doc_id': doc_id,
            'type': 'post',
            'surface_form': post
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
