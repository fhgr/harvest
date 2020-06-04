from flask import Flask
from flask import request
from flask import jsonify
import json
import hashlib

import posts
import extract


app = Flask('harvest')


@app.route('/extract_from_html', methods=['POST'])
def events():
    # data = request
    forum = request.json

    # forum = json.load(data)
    post_0 = posts.extract_posts(forum)
    # print(post_0)

    result = {'entities': {}}
    for post_1 in extract.extract_posts(
            forum['html'],
            forum['url'],
            post_0['xpath_pattern'],
            post_0['url_xpath_pattern'],
            post_0['date_xpath_pattern'],
            post_0['user_xpath_pattern']):

        post_dict = {
            'user': post_1.user,
            'date': post_1.date,
            'url': post_1.url,
            'post': post_1.post
        }

        doc_id = hashlib.md5(forum['url'].encode()).hexdigest()

        result['entities'][doc_id] = result['entities'].get(doc_id, [])
        for item in ['user', 'date', 'url', 'post']:
            result['entities'][doc_id].append({
                'doc_id': doc_id,
                'type': item,
                'surface_form': post_dict[item]
            })

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
