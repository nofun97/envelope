import io
import json
import subprocess

def load(stream):
    p = subprocess.run(
        f'jsonnet -',
        shell=True,
        check=True,
        input=bytes(stream.read(), 'utf-8'),
        capture_output=True,
    )
    return json.loads(p.stdout)

def loads(s):
    return load(io.StringIO(s))
