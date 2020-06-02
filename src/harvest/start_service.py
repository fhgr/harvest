from flask import Flask
from flask import request
import json
import hashlib

from harvest import posts
from harvest.extract import extract_posts


app = Flask('harvest')


@app.route('/extract_from_html', methods=['POST'])
def events():
    data = request.json

    forum = json.load(data)
    post = posts.extract_posts(forum)

    result = {'entities': {}}
    for post in extract_posts(
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

    return result


if __name__ == '__main__':
    app.run(host="'0.0.0.0'", port=5000, debug=True)
