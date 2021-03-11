def parse_input(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    keys = None
    key_space = None
    shortcuts = {}

    for i, line in enumerate(lines):
        if '#key-space' in line:
            key_space = [int(x.strip()) for x in lines[i + 1].split(', ')]
        if '#nodes' in line:
            keys = [int(x.strip()) for x in lines[i + 1].split(', ')]
        if '#shortcuts' in line:
            cuts = [x.strip() for x in lines[i + 1].split(', ')]
            for sc in cuts:
                fr, to = sc.split(':')
                shortcuts[fr] = shortcuts.get(fr, [])
                shortcuts[fr].append(to)

    return keys, key_space, shortcuts


def format_node_data(data):
    links = ''
    if 'links' in data.connections:
        links = ','.join(val['key'] for val in data.connections['links'])

    successor = data.connections['successor']['key']
    next_successor = data.connections['next_successor']['key']
    return f'{data.key}:{links}, S-{successor}, NS-{next_successor}\n'
