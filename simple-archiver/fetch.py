from pathlib import Path, PurePosixPath
from urllib.parse import urlparse, urljoin, urlunparse

import requests
from bs4 import BeautifulSoup, Tag

tasks = []
enqueued = set()


def add_task(url: str):
    parsed_url = urlparse(url)
    if parsed_url.path in enqueued:
        return

    if str.lower(PurePosixPath(parsed_url.path).suffix) in ['.css', ]:
        tasks.insert(0, url)
    else:
        tasks.append(url)
    enqueued.add(parsed_url.path)
    print('Created task {}'.format(url))


def process_link_url(url: str, page_url: str):
    url, page_url = urlparse(url), urlparse(page_url)
    if url.scheme not in ['', 'http', 'https']:
        return None
    path = PurePosixPath(url.path)
    if path.suffix not in ['', '.htm', '.html', '.css', '.jpg', '.png', '.gif', '.svg']:
        return None
    if url.netloc == '' or url.netloc == page_url.netloc:
        task_path = urljoin(page_url.path, url.path)
        task_url = urlunparse((page_url.scheme, page_url.netloc, task_path, url.params, url.query, url.fragment))
        add_task(task_url)
        if url.netloc != '':
            return str(('', '', url.path, url.params, url.query, url.fragment))
    return None


def process_element_attr(element: Tag, tag: str, attr: str, page_url: str):
    for i in element.findAll(tag):
        if i.has_attr(attr):
            url = process_link_url(i[attr], page_url)
            if url is not None:
                i[attr] = url


def process_element(element: BeautifulSoup, page_url: str):
    process_element_attr(element, 'a', 'href', page_url)
    process_element_attr(element, 'img', 'src', page_url)
    process_element_attr(element, 'link', 'href', page_url)
    process_element_attr(element, 'script', 'src', page_url)


def process_page(url: str, storage: str):
    r = requests.get(url)
    if r.status_code != 200:
        return

    page = BeautifulSoup(r.text)
    process_element(page, url)

    # extract url path
    path = urlparse(url).path
    while str.startswith(path, '/'):
        path = path[1:]

    # fix undefined index
    path = PurePosixPath(path)
    if path.name == '':
        path = PurePosixPath.joinpath(path, 'index.html')

    # concat with storage directory
    path = Path.joinpath(Path(storage), path)
    Path.mkdir(path.parent, parents=True, exist_ok=True)

    with open(path, 'wb') as f:
        buf = str(page).encode('utf-8')
        f.write(buf)


if __name__ == '__main__':
    tasks.append('https://lxml.de/')

    while len(tasks) != 0:
        task = tasks.pop(0)
        print('Processing {}'.format(task))
        process_page(task, 'storage')
