import io
import json
import os
import subprocess


def load(stream, path=None, search=None):
    search = search or []
    if path is not None:
        search[:0] = [os.path.dirname(path)]

    cmd = f'jsonnet {" ".join(f"-J {p}" for p in search)} -',
    print(cmd)
    p = subprocess.run(
        cmd,
        shell=True,
        check=True,
        input=bytes(stream.read(), 'utf-8'),
        capture_output=True,
    )
    return json.loads(p.stdout)


def loads(s):
    return load(io.StringIO(s))
