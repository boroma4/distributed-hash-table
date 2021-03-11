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


@app.route('/list', methods=['GET'])
def list_nodes():
    requester_key = request.args.get('requester')

    # break the cycle, basically the base case of the "recursion"
    if requester_key is not None and int(requester_key) > int(data.key):
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
    data.connections['links'].append(link)

    return f'Added a link from {data.key} to {link}'


@app.route('/addsuccessors', methods=['GET'])
def add_successors():
    sskey = request.args.get('sskey')
    ssport = request.args.get('ssport')
    nsskey = request.args.get('nsskey')
    nssport = request.args.get('nssport')

    data.connections['successor'] = {'key': sskey, 'port': ssport}
    data.connections['next_successor'] = {'key': nsskey, 'port': nssport}

    return f'Added successor and next successor to node {data.key}'


# TO BE REPLACED by delete node (with updating links and stuff)
@app.route('/kill', methods=['GET'])
def shutdown():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    func()
    return "Quitting..."


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
