import contextlib
import jsonnet
import json
import os
import sys
import toml
import yaml

import envelope_pb2

MOUNTEBANK_CONFIG_D = '/etc/mountebank/config.d'


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


def parseCommands(cmds: bytearray):
    commands = envelope_pb2.Commands()
    commands.ParseFromString(cmds)
    return commands


# def fixInjections(mb):
#     match mb:
#         case {'egresses': egresses}:
#             for egress in egresses.values():
#                 match egress:
#                     case {'mountebank': {'stubs': stubs}}:
#                         for stub in stubs:
#                             match stub:
#                                 case {'responses': responses}:
#                                     for response in responses:
#                                         match response:
#                                             case {'inject': {'path': path}}:
#                                                 with open(path) as f:
#                                                     data = f.decode('utf-8')
#                                                     response['inject'] = data


class Commands(contextlib.ContextDecorator):
    def __init__(self, out=sys.stdout.buffer):
        self._out = out
        self._cmds = envelope_pb2.Commands()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._out.write(self._cmds.SerializeToString())
        return False

    def activate(self, service: str):
        self._cmds.activations.append(envelope_pb2.Activate(
            service=service
        ))

    def egress(self, service: str, target: str):
        self._cmds.egresses.append(envelope_pb2.Egress(
            service=service,
            target=target,
        ))

    def proxy(self, urlpath: str, target: str):
        self._cmds.proxies.append(envelope_pb2.Proxy(
            urlpath=urlpath,
            target=target,
        ))

    def mountebank(self, service: str, pathOrData: str | object, ext: str = None):
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

        mb = self._cmds.mountebanks.add(service=service)

        isfilename = isinstance(pathOrData, str)
        if isfilename:
            pathOrData = os.path.join('/work', pathOrData.lstrip('/'))
            if not os.path.isfile(pathOrData):
                raise Exception(f"missing mountebank config {pathOrData}")
            os.symlink(pathOrData, destpath)
            mb.path = pathOrData
        else:
            mb.json = json.dumps(pathOrData)

    def watch(self, path: str):
        self._cmds.watches.append(envelope_pb2.Watch(path=path))
