import contextlib
import jsonnet
import json
import os
import re
import sys
import toml
import yaml

import envelope_pb2

MOUNTEBANK_CONFIG_D = '/etc/mountebank/config.d'

LOCALHOST_RE = re.compile(r'(?<=://)localhost\b')


def dockerExternalURL(url: str):
    return LOCALHOST_RE.sub('host.docker.internal', url)


_SCHEME_RE = re.compile(r'^(\w+)')


def getScheme(url: str):
    return _SCHEME_RE.match(url)[0]


def load(path: str, ext: list[str] = None):
    if ext is None:
        ext = os.path.splitext(path)[1][1:]

    def loadjsonnet(f):
        return jsonnet.load(f, path=path)

    load = {
        'json': json.load,
        'jsonnet': loadjsonnet,
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


def basedir(path):
    return os.path.dirname(path)


def abspath(basedir, path):
    if path.startswith('/'):
        basedir = '/work'

    if basedir is not None:
        return os.path.join(basedir, path.lstrip('/'))

    raise Exception("Can't compute abspath without basedir")


def portAllocator(start=4200, end=None):
    end = end or start

    def allocatePort():
        nonlocal start
        port = start
        start += 1
        if start == end:
            raise Exception("out of ports")
        return port
    return allocatePort


def parseCommands(cmds: bytearray):
    commands = envelope_pb2.Commands()
    commands.ParseFromString(cmds)
    return commands


class Commands(contextlib.ContextDecorator):
    def __init__(self, out=sys.stdout.buffer, basePort=4200):
        self._out = out
        self._cmds = envelope_pb2.Commands(basePort=basePort)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._out.write(self._cmds.SerializeToString())
        return False

    def activate(self, service: str):
        self._cmds.activations.add(
            service=service
        )

    def egress(self, service: str, target: str, port: int = 0):
        self._cmds.egresses.add(
            service=service,
            target=target,
            port=port,
        )

    def proxy(self, target: str, port: int = 0):
        self._cmds.proxies.add(
            target=target,
            port=port,
        )

    def mountebank(self, service: str, pathOrData: str | object, basedir: str, ext: str = None, port: int = 0):
        ce = (pathOrData, ext)
        match ce:
            case (str(), None):
                (_, ext) = os.path.splitext(pathOrData)
            case (_, None):
                ext = '.json'
            case (_, str()):
                if not ext.startswith('.'):
                    ext = f".{ext}"
        destpath = os.path.join(MOUNTEBANK_CONFIG_D, f'{service}{ext}')

        try:
            os.unlink(destpath)
        except:
            pass

        mb = self._cmds.mountebanks.add(
            service=service, basedir=basedir, port=port)

        isfilename = isinstance(pathOrData, str)
        if isfilename:
            pathOrData = abspath(basedir, pathOrData)
            if not os.path.isfile(pathOrData):
                raise Exception(f"missing mountebank config {pathOrData}")
            os.symlink(pathOrData, destpath)
            mb.path = pathOrData
        else:
            mb.json = json.dumps(pathOrData)

    def watch(self, path: str):
        self._cmds.watches.add(path=path)
