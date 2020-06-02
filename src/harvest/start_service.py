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
    post = posts.extract_posts(forum)

    result = {'entities': {}}
    for post in extract.extract_posts(
            forum['html'],
            forum['url'],
            post['xpath_pattern'],
            post['url_xpath_pattern'],
            post['date_xpath_pattern'],
            post['user_xpath_pattern']):

        post_dict = {
            'user': post.user,
            'date': post.date,
            'url': post.url,
            'post': post.post
        }

        doc_id = hashlib.md5(forum['url'].encode()).hexdigest()

        result['entities'][doc_id] = []
        for item in ['user', 'date', 'url', 'post']:
            result['entities'][doc_id].append({
                'doc_id': doc_id,
                'type': item,
                'surface_form': post_dict[item]
            })
    print(f"Sending response: {result}")
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
