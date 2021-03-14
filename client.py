import requests
import sys
import config

args = sys.argv

if len(args) < 2:
    print('no args')
    sys.exit(1)

if args[1] == 'init':
    r = requests.get(f'http://{config.ip}:{config.manager_port}/init')
    if r.status_code == 200:
        print('Successfully started DHT')
    else:
        print('Failed to start DHT')

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

