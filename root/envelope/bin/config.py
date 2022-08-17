import jsonnet
import json
import os
import sys
import toml
import yaml

MOUNTEBANK_CONFIG_D = '/etc/mountebank/config.d'

# local


def load(path: str, ext: list[str] = None):
    if ext is None:
        ext = os.path.splitext(path)[1][1:]

    load = {
        'json': json.load,
        'jsonnet': jsonnet.load,
        'yaml': yaml.safe_load,
        'yml': yaml.safe_load,
        'toml': toml.load,
    }[ext]

    with open(path) as f:
        return load(f)

# Example: loadAny('/etc/foobar.{}.in')


def loadAny(pathspec, exts=['json', 'jsonnet', 'toml', 'yaml', 'yml']):
    for ext in exts:
        path = pathspec.format(ext)
        try:
            return (load(path, ext), path)
        except FileNotFoundError as e:
            pass

    exts = ','.join(exts)
    raise Exception(f'no matches for {pathspec.format(f"{{{exts}}}")}')


def portAllocator(base=12000):
    def allocatePort():
        nonlocal base
        port = base
        base += 1
        return port
    return allocatePort


def _cmd(cmd: str, arg):
    print(f'{cmd} {json.dumps(arg)}')


def parseCmd(cmd: str):
    op, args = cmd.split(' ', maxsplit=1)
    return (op, json.loads(args))


class cmd:
    @staticmethod
    def activate(service: str):
        _cmd('ACTIVATE', service)

    @staticmethod
    def egress(service: str, target: str):
        _cmd('EGRESS', {'service': service, 'target': target})

    @staticmethod
    def proxy(urlpath: str, target: str):
        _cmd('PROXY', {'urlpath': urlpath, 'target': target})

    # cfgpath can be a string or a readable stream.
    @staticmethod
    def mountebank(service: str, cfgpath, ext=None):
        if ext is None:
            (_, ext) = os.path.splitext(cfgpath)
        destpath = os.path.join(MOUNTEBANK_CONFIG_D, f'{service}{ext}')

        try:
            os.unlink(destpath)
        except:
            pass

        isfilename = isinstance(cfgpath, str)
        if isfilename:
            cfgpath = os.path.join('/work', cfgpath.lstrip('/'))
            if not os.path.isfile(cfgpath):
                raise Exception(f"missing mountebank config {cfgpath}")
            print(
                f'Symlinking mountebank config {cfgpath} -> {destpath}', file=sys.stderr)
            os.symlink(cfgpath, destpath)
        else:
            print(f'Creating mountebank config {destpath}', file=sys.stderr)
            with open(destpath, 'w') as f:
                f.write(cfgpath.read())

        _cmd('MOUNTEBANK', {
            'service': service,
            'cfgpath': destpath,
            'watch': isfilename,
        })

    @staticmethod
    def watch(path: str):
        _cmd('WATCH', path)
