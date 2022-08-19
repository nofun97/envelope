import collections
import re


def _walk(obj, tree):
    def descend(parent, key, obj, node):
        match node:
            case dict():
                for (field, subnode) in node.items():
                    if field in obj:
                        yield from descend(obj, field, obj[field], subnode)
            case [subnode]:
                for (i, value) in enumerate(obj):
                    yield from descend(obj, i, value, subnode)
            case _:
                def put(value):
                    parent[key] = value
                yield from node(obj, put)

    yield from descend([obj], 0, obj, tree)


def walkFileRefs(obj, f):
    yield from _walk(obj, {
        'key': f,
        'cert': f,
        'stubs': [{
            'responses': [{
                'inject': f,
                'is': {'body': f},
                'behaviours': [{
                    'decorate': f,
                }],
                'proxy': {
                    'key': f,
                    'cert': f,
                    'predicateGenerators': f,
                },
            }],
        }],
    })
