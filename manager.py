import requests
import subprocess
import flask
import time
import utils
import config
from flask import request

app = flask.Flask(__name__)

# node with smallest key
entry_node_port = None
key_space = []
is_initialized = False


@app.route('/list', methods=['GET'])
def list_nodes():
    return requests.get(f'http://{config.ip}:{entry_node_port}/list').text


@app.route('/shortcut')
def add_shortcut():
    global is_initialized

    key = request.args.get('from')
    to_key = request.args.get('to')
    port = int(key) + config.node_port_prefix
    to_port = int(to_key) + config.node_port_prefix

    if not is_initialized:
        return 'DHT not initialized'

    try:
        requests.get(f'http://{config.ip}:{port}/alive', timeout=0.5)
        requests.get(f'http://{config.ip}:{to_port}/alive', timeout=0.5)
    except requests.exceptions.ConnectTimeout:
        return 'Nodes might not exist'

    return requests.get(f'http://{config.ip}:{port}/addlink?key={to_key}&port={to_port}').text


# TODO: actually might not work when there are 1-2 nodes
@app.route('/join', methods=['GET'])
def join_node():
    global entry_node_port, is_initialized

    key = request.args.get('key')
    port = int(key) + config.node_port_prefix

    if not is_initialized:
        return 'DHT not initialized'

    if not key_space[0] <= int(key) <= key_space[1]:
        return 'Key outside of keyspace'

    try:
        requests.get(f'http://{config.ip}:{port}/alive', timeout=0.5)
        return 'Node already exists'
    except requests.exceptions.ConnectTimeout:
        pass

    # as always, assume nothing crashes
    subprocess.Popen(f'python node.py {key}')
    time.sleep(1)
    r = requests.get(f'http://{config.ip}:{entry_node_port}/join?key={key}')

    if r.status_code != 200:
        return 'Something went wrong'

    if port < entry_node_port:
        entry_node_port = port

    return f'Successfully added node {key}'


@app.route('/init', methods=['GET'])
def init():
    global is_initialized, entry_node_port, key_space

    if is_initialized:
        return 'DHT already initialized'

    # read the file
    keys, key_space, shortcuts = utils.parse_input('input.txt')

    keys = [key for key in sorted(keys) if key_space[0] <= key <= key_space[1]]

    # assume list not empty, need to do it properly here I guess
    entry_node_port = config.node_port_prefix + keys[0]
    is_initialized = True

    # launch nodes, assume all of them started successfully
    for key in keys:
        subprocess.Popen(f'python node.py {key}')

    time.sleep(1)
    # send successor links to nodes
    for i in range(len(keys)):
        current_node_port = config.node_port_prefix + keys[i]
        successor_idx = (i + 1) % (len(keys))
        next_successor_idx = (i + 2) % (len(keys))
        successor_key = keys[successor_idx]
        successor_port = config.node_port_prefix + keys[successor_idx]
        next_successor_key = keys[next_successor_idx]
        next_successor_port = config.node_port_prefix + keys[next_successor_idx]

        # assume it works here too
        requests.get(f'http://{config.ip}:{current_node_port}/setsuccessor?'
                     f'key={successor_key}&port={successor_port}')
        requests.get(f'http://{config.ip}:{current_node_port}/setnextsuccessor?'
                     f'key={next_successor_key}&port={next_successor_port}')

    # send shortcuts to nodes
    for fr, to_list in shortcuts.items():
        current_node_port = config.node_port_prefix + int(fr)
        for destination in to_list:
            destination_port = config.node_port_prefix + int(destination)
            requests.get(f'http://{config.ip}:{current_node_port}/addlink?'
                         f'key={destination}&port={destination_port}')

    return 'Successfully initialized DHT'


if __name__ == '__main__':
    app.run(host=config.ip, port=config.manager_port)
