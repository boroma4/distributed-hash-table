import requests
import sys
import config

args = sys.argv

if len(args) < 2:
    print('no args')
    sys.exit(1)

if args[1] == 'init':
    r = requests.get(f'http://{config.ip}:{config.manager_port}/init')
    print(r.text)

if args[1] == 'list':
    r = requests.get(f'http://{config.ip}:{config.manager_port}/list')
    if r.status_code == 200:
        print(r.text)
    else:
        print('Failed to list nodes')

if args[1] == 'join':
    if len(args) > 2:
        key = args[2]
        if key.isnumeric():
            r = requests.get(f'http://{config.ip}:{config.manager_port}/join?key={key}')
            if r.status_code == 200:
                print(r.text)
            else:
                print('Failed to add a node')
        else:
            print('Key must be a number')
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
                print('Failed to add a node')
            print(r.text)
        else:
            print('Key must be a number')
    else:
        print('Please specify key')


if args[1] == 'shortcut':
    if len(args) > 2:
        fr, to = args[2].split(':')
        r = requests.get(f'http://{config.ip}:{config.manager_port}/shortcut?from={fr}&to={to}')
        if r.status_code == 200:
            print(r.text)
        else:
            print('Failed to add a node')
    else:
        print('Please specify from/to nodes')

