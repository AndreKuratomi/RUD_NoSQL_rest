import os
import pymongo
from flask import jsonify
from datetime import datetime
from exceptions.exceptions import IncompleteSendError, NotFoundError
from ipdb import set_trace

mongo_uri = os.getenv("MONGO_URI")
client_db = os.getenv("MONGO_CLIENT")

client = pymongo.MongoClient(mongo_uri)
db = client[client_db]


class Post:
    def __init__(self, title: str, author: str, tags: list, content: str) -> None:
        self.id = self.create_id()
        self.title = title
        self.author = author
        self.content = content
        self.tags = tags
        self.created_at = datetime.today().strftime("%d/%m/%Y %H:%M:%S %p")

    def create_id(self):
        arr = list(db.posts.find())
        if arr:
            return arr[-1]['id'] + 1
        else:
            return 1

    @staticmethod
    def show_all():
        try:
            posts_list = db.posts.find()

            if not posts_list:
                raise NotFoundError

            posts = []
            for post in posts_list:
                del post['_id']
                posts.append(post)

            return jsonify(posts), 200

        except NotFoundError as e:
            return e.message, 404

    @staticmethod
    def show_by_id(id):
        try:
            arr = db.posts.find()
            for found in arr:
                if found['id'] == int(id):
                    del found['_id']

                    return jsonify(found), 200
                else:
                    raise NotFoundError

        except NotFoundError as e:
            return e.message, 404

    def register(self):
        db.posts.insert_one(self.__dict__)

    @staticmethod
    def update(id, data):
        to_update1 = db.posts.find_one({'id': int(id)})

        if to_update1:
            del to_update1['_id']
            db.posts.update_one({'id': int(id)}, {'$set': data})

            to_update2 = db.posts.find_one({'id': int(id)})
            del to_update2['_id']

            return to_update2, 200

    @staticmethod
    def delete(id):
        try:
            surv_arr = []
            the_one = db.posts.find_one({'id': int(id)})

            if the_one:
                del the_one['_id']
                surv_arr.append(the_one)
                db.posts.find_one_and_delete(the_one)
                return jsonify(surv_arr)

            else:
                raise NotFoundError

        except NotFoundError as e:
            return e.message, 404
