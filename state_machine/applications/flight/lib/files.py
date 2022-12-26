import os

def mkdirp(path):
    """Create a directory and all parent directories if necessary."""
    path = path.split('/')
    path = [p for p in path if p != '']
    sd = False
    if path[0] == 'sd':
        path = path[1:]
        sd = True

    for i in range(len(path)):
        subpath = '/'.join(path[:i + 1])
        if sd:
            subpath = '/sd/' + subpath

        try:
            os.mkdir(subpath)
        except Exception:
            pass
