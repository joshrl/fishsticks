from flask import Flask, request, url_for, Response, json, jsonify
from rq import Queue
from rq.job import Job
from worker import conn
import operator
import redis
import uuid
import gevent.pywsgi
import gevent.monkey

gevent.monkey.patch_all()

#################
# configuration #
#################

app = Flask(__name__)
q = Queue(connection=conn)

#################
# helper #
#################

def create_or_update_job(data):
    
    name = data.get("name", str(uuid.uuid4()))
    branch = data.get("branch", "master")
    url = data.get("url")
    recipes = data.get("recipes",[])
    
    job = q.enqueue_call(
        func="job.start_job", args=(name, url, branch, recipes), result_ttl=5000
    )
            
    result = {'job_id':job.get_id(), 'name':name}
    return result


##########
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def job_list_or_create():
    if request.method == 'POST':
        resp = jsonify(create_or_update_job(request.json))
        resp.status_code = 201
        return resp
    return ""
    
@app.route('/console/<name>', methods=['GET'])
def console(name):
    def generate():
        r = redis.Redis()
        pubsub = r.pubsub()
        pubsub.subscribe("%s.console" % name)
        for item in pubsub.listen():
            if item['data'] == "EOF":
                pubsub.unsubscribe()
                yield "Job Finished"
                break
            yield str(item['data'])
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    # use gevent allows "console" to run async
    gevent_server = gevent.pywsgi.WSGIServer(('', 5000), app)
    gevent_server.serve_forever()


