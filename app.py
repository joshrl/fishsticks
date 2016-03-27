from flask import Flask, request, url_for, Response, json, jsonify, render_template
from rq import Queue
from rq.job import Job
from worker import conn
import operator
import redis
import uuid
from flask.ext.socketio import SocketIO, emit
from flask_socketio import join_room, leave_room
import eventlet

eventlet.monkey_patch()

#################
# configuration #
#################

app = Flask(__name__)
q = Queue(connection=conn)
socketio = SocketIO(app)

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
def root():
    if request.method == 'POST':
        resp = jsonify(create_or_update_job(request.json))
        resp.status_code = 201
        return resp
    return ""

@app.route('/console/<name>', methods=['GET'])
def console(name):
    return render_template('console.html')

@socketio.on('subscribe', namespace='/console')
def console_subscribe(job):   
    channel = job['name'] + '.console'
    join_room(channel)
    emit('log', {'message': 'Subscribed to channel: ' + channel})

@socketio.on('connect', namespace='/console')
def console_connect():
    request.namespace
    emit('log', {'message': 'Connected'})

@socketio.on('disconnect', namespace='/console')
def console_disconnect():
    print('Client disconnected')

# Long running task that subscribes to all console messages
def console_listener():    
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.psubscribe("*.console")
    for item in pubsub.listen():
        channel = item["channel"]
        log_item = str(item["data"])
        socketio.emit('log', {'message': log_item}, namespace='/console', room=channel)
        print "%s: %s" % (channel, log_item)

if __name__ == '__main__':
    eventlet.spawn_n(console_listener)
    socketio.run(app)


