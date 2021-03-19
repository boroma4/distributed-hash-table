import flask
import sys
import requests
import utils
import config
from flask import request


class Data:
    key = ''
    port = ''
    connections = {}

    def __str__(self):
        return f'Key: {self.key}, Port: {self.port}, Connections: {self.connections}'


app = flask.Flask(__name__)
data = Data()


@app.route('/', methods=['GET'])
def home():
    return str(data)


@app.route('/info', methods=['GET'])
def node_info():
    return data.connections


@app.route('/join', methods=['GET'])
def join():
    new_node_key = request.args.get('key')  # key to add
    new_node_port = config.node_port_prefix + int(new_node_key)
    successor_key = data.connections['successor']['key']
    next_successor_key = data.connections['next_successor']['key']
    successor_port = data.connections['successor']['port']

    # 1-node case
    if data.connections['successor']['key'] == data.key:
        requests.get(f'http://{config.ip}:{new_node_port}/setsuccessor?key={data.key}&port={data.port}')
        requests.get(f'http://{config.ip}:{new_node_port}/setnextsuccessor?key={new_node_key}&port={new_node_port}')
        data.connections['successor'] = {'key': new_node_key, 'port': new_node_port}
        return 'Success'

    # 2-node case
    if data.connections['next_successor']['key'] == data.key:
        # data.key is the smallest in the DHT

        # must become first
        if int(new_node_key) < int(data.key):
            requests.get(f'http://{config.ip}:{new_node_port}/setsuccessor?key={data.key}&port={data.port}')
            requests.get(
                f'http://{config.ip}:{new_node_port}/setnextsuccessor?key={successor_key}&port={successor_port}')
            requests.get(f'http://{config.ip}:{successor_port}/setsuccessor?key={new_node_key}&port={new_node_port}')
            requests.get(f'http://{config.ip}:{successor_port}/setnextsuccessor?key={data.key}&port={data.port}')
            data.connections['next_successor'] = {'key': new_node_key, 'port': new_node_port}

        # insert in the middle
        if int(data.key) < int(new_node_key) < int(successor_key):
            requests.get(f'http://{config.ip}:{new_node_port}/setsuccessor?key={successor_key}&port={successor_port}')
            requests.get(
                f'http://{config.ip}:{new_node_port}/setnextsuccessor?key={data.key}&port={data.port}')

            requests.get(
                f'http://{config.ip}:{successor_port}/setnextsuccessor?key={new_node_key}&port={new_node_port}')

            data.connections['successor'] = {'key': new_node_key, 'port': new_node_port}
            data.connections['next_successor'] = {'key': successor_key, 'port': successor_port}

        # insert last
        if int(successor_key) < int(new_node_key):
            requests.get(f'http://{config.ip}:{new_node_port}/setsuccessor?key={data.key}&port={data.port}')
            requests.get(
                f'http://{config.ip}:{new_node_port}/setnextsuccessor?key={successor_key}&port={successor_port}')
            requests.get(
                f'http://{config.ip}:{successor_port}/setsuccessor?key={new_node_key}&port={new_node_port}')
            requests.get(
                f'http://{config.ip}:{successor_port}/setnextsuccessor?key={data.key}&port={data.port}')
            data.connections['next_successor'] = {'key': new_node_key, 'port': new_node_port}

        return 'Success'

    # general join case
    if successor_key < new_node_key < next_successor_key \
            or (next_successor_key < new_node_key > successor_key > next_successor_key):

        # set current nodes next successor
        data.connections['next_successor'] = {'key': new_node_key, 'port': new_node_port}

        old_successor_successor = requests.get(f'http://{config.ip}:{successor_port}/getsuccessor').json()
        old_successor_next_successor = requests.get(f'http://{config.ip}:{successor_port}/getnextsuccessor').json()

        # update the successor of the successor to be the new node :D
        requests.get(f'http://{config.ip}:{successor_port}/setsuccessor?key={new_node_key}&port={new_node_port}')

        # update the next successor of the successor to be the old successor :DDD
        _key, _port = old_successor_successor['key'], old_successor_successor['port']
        requests.get(f'http://{config.ip}:{successor_port}/setnextsuccessor?key={_key}&port={_port}')

        # finally give references to the new node
        requests.get(f'http://{config.ip}:{new_node_port}/setsuccessor?key={_key}&port={_port}')

        _key, _port = old_successor_next_successor['key'], old_successor_next_successor['port']
        requests.get(f'http://{config.ip}:{new_node_port}/setnextsuccessor?key={_key}&port={_port}')

        return 'Success'

    # try next node
    else:
        return requests.get(f'http://{config.ip}:{successor_port}/join?key={new_node_key}').text


@app.route('/leave', methods=['GET'])
def leave():
    node_to_leave_key = request.args.get('key')  # key to delete
    node_to_leave_port = config.node_port_prefix + int(node_to_leave_key)
    successor_port = data.connections['successor']['port']

    # general removal case
    if data.connections['next_successor']['key'] == node_to_leave_key:
        node_to_leave_successor = requests.get(f'http://{config.ip}:{node_to_leave_port}/getsuccessor').json()
        node_to_leave_next_successor = requests.get(f'http://{config.ip}:{node_to_leave_port}/getnextsuccessor').json()

        node_to_leave_successor_key = node_to_leave_successor['key']
        node_to_leave_successor_port = node_to_leave_successor['port']
        node_to_leave_next_successor_key = node_to_leave_next_successor['key']
        node_to_leave_next_successor_port = node_to_leave_next_successor['port']

        # update references

        # only 2 nodes left
        if data.key == node_to_leave_key:
            # make the last node point to itself
            requests.get(
                f'http://{config.ip}:{successor_port}/setsuccessor?key={node_to_leave_successor_key}&port={node_to_leave_successor_port}')
            requests.get(
                f'http://{config.ip}:{successor_port}/setnextsuccessor?key={node_to_leave_successor_key}&port={node_to_leave_successor_port}')
        else:
            requests.get(
                f'http://{config.ip}:{successor_port}/setsuccessor?key={node_to_leave_successor_key}&port={node_to_leave_successor_port}')
            requests.get(
                f'http://{config.ip}:{successor_port}/setnextsuccessor?key={node_to_leave_next_successor_key}&port={node_to_leave_next_successor_port}')
            data.connections['next_successor'] = node_to_leave_successor

        return f'Updated successors links to node {node_to_leave_key}'
    else:
        return requests.get(f'http://{config.ip}:{successor_port}/leave?key={node_to_leave_key}').text


@app.route('/rmshortcut', methods=['GET'])
def remove_shortcuts():
    fr = request.args.get('from')
    to_remove = request.args.get('key')
    successor_port = data.connections['successor']['port']

    # valid case
    if fr is None or int(data.key) < int(fr):
        if 'links' in data.connections is not None and to_remove in data.connections['links']:
            data.connections['links'].remove(to_remove)
        return requests.get(f'http://{config.ip}:{successor_port}/rmshortcut?key={to_remove}&from={data.key}').text
    # prevent infinite circle
    else:
        return f'Deleted all shortcuts to {to_remove}'


@app.route('/list', methods=['GET'])
def list_nodes():
    requester_key = request.args.get('requester')

    # break the cycle, basically the base case of the "recursion"
    if requester_key is not None and int(requester_key) >= int(data.key):
        return ''

    current_node_str = utils.format_node_data(data)
    next_port = data.connections['successor']['port']
    next_nodes_data = requests.get(f'http://{config.ip}:{next_port}/list?requester={data.key}').text

    return current_node_str + next_nodes_data


@app.route('/addlink', methods=['GET'])
def add_link():
    key = request.args.get('key')
    port = request.args.get('port')
    link = {'key': key, 'port': port}
    data.connections['links'] = data.connections.get('links', [])

    if link in data.connections['links']:
        return 'Shortcut already exists'

    data.connections['links'].append(link)
    return f'Added a link from {data.key} to {key}'


@app.route('/getsuccessor', methods=['GET'])
def get_next_sucessor():
    return data.connections['successor']


@app.route('/getnextsuccessor', methods=['GET'])
def get_sucessor_port():
    return data.connections['next_successor']


@app.route('/setsuccessor', methods=['GET'])
def set_successor():
    key = request.args.get('key')
    port = request.args.get('port')
    data.connections['successor'] = {'key': key, 'port': port}
    return f'Added successor to node {data.key}'


@app.route('/setnextsuccessor', methods=['GET'])
def set_next_successor():
    key = request.args.get('key')
    port = request.args.get('port')
    data.connections['next_successor'] = {'key': key, 'port': port}
    return f'Added next successor to node {data.key}'


@app.route('/alive', methods=['GET'])
def is_alive():
    return 'True'


# Use when deleting node and stuff
@app.route('/kill', methods=['GET'])
def shutdown():
    flask.request.environ.get('werkzeug.server.shutdown')()
    return f'Node {data.key} died'


def main():
    args = sys.argv
    if len(args) < 2:
        print('No key specified')
        return

    key = args[1]
    if not key.isnumeric():
        print('key must be a number')

    port = config.node_port_prefix + int(key)
    data.key = key
    data.port = port

    app.run(host=config.ip, port=port)


if __name__ == '__main__':
    main()
