"""
Simple example of a RESTful PFA scoring engine

Leverages the open source Titus PFA engine:
  https://github.com/opendatagroup/hadrian

Copyright 2017 Alpine Data

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import tornado.ioloop
import tornado.web
import os
import logging
import sys
import tinydb
from titus.genpy import PFAEngine
from time import gmtime, strftime

root = os.path.dirname("web_assets/index.html")


class DbSupport:
    """
    Uses tinydb to retain all info in the scoring system
    For each model retains:
     i) PFA representation,
     ii) creation time,
     iii) update time,
     iv) usage metrics
    """

    # Open DB
    def __init__(self, db_name):
        self.db = tinydb.TinyDB(db_name)

    # Add/Update PFA model
    def add_model(self, model_name, model_pfa):
        model = tinydb.Query()
        db_results = self.db.search(model.name == model_name)
        if db_results:
            logging.debug("model (%s) updated" % model_name)
            self.db.update({'updated': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                            'invoked': 0,
                            'model_pfa': model_pfa}, model.name == model_name)
        else:
            logging.debug("model (%s) created" % model_name)
            self.db.insert({'name': model_name,
                            'created': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                            'updated': '',
                            'invoked': 0,
                            'total_invoked': 0,
                            'model_pfa': model_pfa})

    # Delete PFA model
    def delete_model(self, model_name):
        model = tinydb.Query()
        db_results = self.db.search(model.name == model_name)
        if db_results:
            logging.debug("model (%s) deleted" % model_name)
            self.db.remove(model.name == model_name)
            return True
        else:
            logging.error("model (%s) identified for deletion not found" % model_name)
            return False

    # Retrieve PFA model usage statistics
    def get_stats(self, model_name):
        model = tinydb.Query()
        db_results = self.db.search(model.name == model_name)
        if db_results:
            logging.debug("model (%s) stats retrieved" % model_name)
            return db_results
        else:
            logging.error("model (%s) stats not found" % model_name)
            return None

    # Retrieve PFA model
    def get_model(self, model_name):
        model = tinydb.Query()
        db_results = self.db.search(model.name == model_name)
        if db_results:
            logging.debug("model (%s) retrieved" % model_name)
            return db_results[0]['model_pfa']
        else:
            logging.error("model (%s) stats not found" % model_name)
            return None

    # Retrieve list of all deployed models
    # Newer versions of tinydb support more efficient mechanisms
    def get_models(self):
        models = []
        for model in self.db.all():
            models.append(model["name"])
        return models

    # Update PFA model usage statistics
    def update_usage_stats(self, model_name):
        model = tinydb.Query()
        db_results = self.db.search(model.name == model_name)
        if db_results:
            invoked = db_results[0]['invoked'] + 1
            total_invoked = db_results[0]['total_invoked'] + 1
            self.db.update({'invoked': invoked,
                            'total_invoked': total_invoked}, model.name == model_name)
        else:
            logging.error("model (%s) stats not found" % model_name)


class MainHandler(tornado.web.RequestHandler):
    # Return list of APIs
    def get(self):
        self.render("index.html")


class ScoreModel(tornado.web.RequestHandler):
    # Score model
    def post(self, model_name):
        pfa_model = db.get_model(model_name)
        pfa_engine, = PFAEngine.fromJson(pfa_model)
        data_to_score = tornado.escape.json_decode(self.request.body)
        db.update_usage_stats(model_name)
        self.write(str(pfa_engine.action(data_to_score)))


class DeployModel(tornado.web.RequestHandler):
    # Get model
    def get(self, model_name):
        if model_name == "":
            models = db.get_models()
            self.write(', '.join(models))
        else:
            pfa_model = db.get_model(model_name)
            model_name = 'models/%s.pfa' % model_name
            if pfa_model:
                self.write(pfa_model)
            else:
                self.set_status(404)
                self.write("Model (%s) not found" % model_name)

    # Upload model
    def put(self, model_name):
        db.add_model(model_name, self.request.body)
        self.write("Model (%s) successfully uploaded" % model_name)

    # Delete model
    def delete(self, model_name):
        success = db.delete_model(model_name)
        if success:
            self.write("Model (%s) successfully deleted" % model_name)
        else:
            self.set_status(404)
            self.write("Model (%s) not found" % model_name)


class GetMetrics(tornado.web.RequestHandler):
    # Get model metrics
    def get(self, model_name):
        model_stats = db.get_stats(model_name)
        if model_stats:
            self.write(tornado.escape.json_encode(model_stats))
        else:
            self.set_status(404)
            self.write("Model (%s) not found" % model_name)


def make_app():
    return tornado.web.Application([
        (r"/alpine", MainHandler),
        (r"/alpine/score/([a-zA-Z0-9_]+)", ScoreModel),
        (r"/alpine/metrics/([a-zA-Z0-9_]+)", GetMetrics),
        (r"/alpine/deploy/([a-zA-Z0-9_]*)", DeployModel), ],
        template_path=root,
        static_path=root)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("web_example.py web_port")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    db = DbSupport("alpine.db")
    app = make_app()
    app.listen(sys.argv[1])
    tornado.ioloop.IOLoop.current().start()
