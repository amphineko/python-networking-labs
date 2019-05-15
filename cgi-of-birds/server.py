#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from typing import Callable, List, Tuple
from wsgiref.simple_server import make_server


def serve_index(env: dict, data: dict) -> (str, List[Tuple[str, str]], str):
    html = '<!DOCTYPE html><html><body><ul>'
    for key, value in data.items():
        html += '<li><a href="/{}">{}</a></li>'.format(key, key, value['Scientific name'])
    html += '</ul></body></html>'
    return '200 OK', [], html


def serve_item(env, name, data) -> (str, List[Tuple[str, str]], str):
    if name not in data:
        return '404 Not Found', [], ''

    item = data[name]
    html = '<!DOCTYPE html><html><body>'
    html += '<h1>{}</h1>'.format(name)
    html += '<h2>{}</h2>'.format(item['Scientific name'])
    html += '<p>{}</p>'.format(item['Description'])
    html += '</body></html>'
    return '200 OK', [], html


def handle_request(environ: dict, start_fn: Callable, data: dict) -> List[bytes]:
    if environ['PATH_INFO'] == '/':
        status, headers, body = serve_index(environ, data)
        print('Using index handler with status {}'.format(status))
    else:
        status, headers, body = serve_item(environ, name=environ['PATH_INFO'][1:], data=data)
        print('Using item handler with status {}'.format(status))

    start_fn(status, headers)
    return [str.encode(body, 'utf-8'), ]


def main():
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('-a', '--host', default='localhost', required=False, type=str)
    parser.add_argument('-p', '--port', default=8080, required=False, type=int)
    parser.add_argument('-f', '--file', default='animals.json', required=False, type=str)
    args = parser.parse_args()

    # load animal data
    with open(args.file) as f:
        animals = json.load(f)

    # create wsgi server
    server = make_server(args.host, args.port, lambda environ, start_fn: handle_request(environ, start_fn, animals))
    server.serve_forever()


if __name__ == '__main__':
    main()
