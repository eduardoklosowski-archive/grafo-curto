#!/usr/bin/env python

import json


HEADERS = [('Content-type', 'application/json')]


def application(environ, start_response):
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 METHOD NOT ALLOWED', HEADERS)
        return [json.dumps({'error': 'Method must be POST'}).encode('utf-8')]

    if environ['CONTENT_TYPE'] != 'application/json':
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'Content-Type must be application/json'}).encode('utf-8')]

    length = int(environ.get('CONTENT_LENGTH', 0))
    if length == 0:
        start_response('411 LENGTH REQUIRED', HEADERS)
        return [json.dumps({'error': 'Content-Length is required'}).encode('utf-8')]

    try:
        content = json.loads(environ['wsgi.input'].read(length).decode('utf-8'))
    except Exception:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'Content is poorly formatted'}).encode('utf-8')]

    if 'graph' not in content:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'graph not found in content'}).encode('utf-8')]
    if 'source' not in content:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'source not found in content'}).encode('utf-8')]
    if 'destination' not in content:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'destination not found in content'}).encode('utf-8')]

    try:
        graph = Graph.from_dict(content['graph'])
        vertexes = {v.id for v in graph.vertexes}
    except Exception:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'Error on graph'}).encode('utf-8')]

    if content['source'] not in vertexes:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'source not in graph'}).encode('utf-8')]
    if content['destination'] not in vertexes:
        start_response('400 BAD REQUEST', HEADERS)
        return [json.dumps({'error': 'destination not in graph'}).encode('utf-8')]

    try:
        result = graph.dijkstra(content['source'], content['destination'])
    except Exception:
        start_response('500 INTERNAL SERVER ERROR', HEADERS)
        return [json.dumps({'error': 'Error on execute Dijkstra'}).encode('utf-8')]

    if result['has_path']:
        status = '200 OK'
    else:
        status = '404 NOT FOUND'
    start_response(status, HEADERS)
    return [json.dumps(result).encode('utf-8')]


class Vertex(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __eq__(self, other):
        try:
            return self.id == other.id
        except Exception:
            return False


class Edge(object):
    def __init__(self, id, source, destination, weight):
        self.id = id
        self.source = source
        self.destination = destination
        self.weight = weight

    def __eq__(self, other):
        try:
            return self.id == other.id
        except Exception:
            return False

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source.id,
            'destination': self.destination.id,
            'weight': self.weight,
        }


class Graph(object):
    def __init__(self, vertexes, edges):
        self.vertexes = vertexes
        self.edges = edges

    @staticmethod
    def from_dict(content):
        vertexes = {attr['id']: Vertex(attr['id'], attr['name'])
                    for attr in content.get('vertexes', [])}
        edges = [Edge(attr['id'], vertexes[attr['source']], vertexes[attr['destination']], attr['weight'])
                 for attr in content.get('edges', [])]
        return Graph(vertexes.values(), edges)

    def dijkstra(self, source, destination):
        has_path = False
        path = []
        cost = None
        vertexes = {v.id: {
            'id': v.id,
            'cost': float('inf'),
            'edge': None,
            'open': True,
        } for v in self.vertexes}
        vertexes[source]['cost'] = 0

        opens = {source: vertexes[source]}
        while opens:
            vertex = min(opens.values(), key=lambda o: o['cost'])
            v = vertex['id']
            vertexes[v]['open'] = False

            if destination == v:
                has_path = True
                break

            for e in self.edges:
                if e.source.id == v:
                    d = e.destination.id
                    c = vertex['cost'] + e.weight
                    if vertexes[d]['open'] and c < vertexes[d]['cost']:
                        vertexes[d]['cost'] = c
                        vertexes[d]['edge'] = e

            opens = {v['id']: v for v in vertexes.values() if v['open'] and v['edge']}

        if has_path:
            v = vertexes[destination]
            cost = v['cost']
            while v['edge']:
                path.append(v['edge'])
                v = vertexes[v['edge'].source.id]

        return {
            'source': source,
            'destination': destination,
            'has_path': has_path,
            'path': [e.to_dict() for e in reversed(path)],
            'cost': cost,
        }


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('', 8000, application)
    print('Serving on port 8000...')
    httpd.serve_forever()
