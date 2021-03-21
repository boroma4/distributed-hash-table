import requests
import sys
import config

args = sys.argv

if len(args) < 2:
    print('no args')
    sys.exit(1)

if args[1] == 'init':
    r = requests.get(f'http://{config.ip}:{config.manager_port}/init')
    print('\n' + r.text + '\n')



if args[1] == 'list':
    r = requests.get(f'http://{config.ip}:{config.manager_port}/list')
    if r.status_code == 200:
        print('\n' + r.text)
    else:
        print('Failed to list nodes')

if args[1] == 'join':
    if len(args) > 2:
        key = args[2]
        if key.isnumeric():
            r = requests.get(f'http://{config.ip}:{config.manager_port}/join?key={key}')
            if r.status_code == 200:
                print('\n' + r.text + '\n')
            else:
                print('Failed to add a node')
        else:
            print('Key must be a number')
    else:
        print('Please specify key')

if args[1] == 'lookup':
    if len(args) > 2:
        key_node = args[2].split(':')
        key = key_node[0]
        if key.isnumeric():
            if len(key_node) > 1:
                r = requests.get(f'http://{config.ip}:{config.manager_port}/lookup?key={key}&node={key_node[1]}')
            else:
                r = requests.get(f'http://{config.ip}:{config.manager_port}/lookup?key={key}')
            if r.status_code == 200:
                print('\n' + r.text)
            else:
                print('The specified key was not found')
        else:
            print('Key/node must be a number')
    else:
        print('Please specify key')



if args[1] == 'leave':
    if len(args) > 2:
        key = args[2]
        if key.isnumeric():
            r = requests.get(f'http://{config.ip}:{config.manager_port}/leave?key={key}')
            if r.status_code == 200:
                pass
            else:
                print('Failed to remove a node\n')
            print('\n' + r.text + '\n')
        else:
            print('Key must be a number')
    else:
        print('Please specify key')


if args[1] == 'shortcut':
    if len(args) > 2:
        fr, to = args[2].split(':')
        r = requests.get(f'http://{config.ip}:{config.manager_port}/shortcut?from={fr}&to={to}')
        if r.status_code == 200:
            print('\n' + r.text + '\n')
        else:
            print('Failed to add a node')
    else:
        print('Please specify from/to nodes')

