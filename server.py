import json
import os

from bottle import post, run
import bottle
from phabricator import Phabricator

import task_tagger

phab = None
tag_map = None


def init():
    global phab, tag_map

    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    phab.update_interfaces()

    tag_map = task_tagger.resolve_tags(phab)


@post('/hook')
def receive_hook():
    detail = bottle.request.json

    if detail['object']['type'] == 'TASK':
        try:
            task_tagger.on_task_update(phab, phid=detail['object']['phid'], tag_map=tag_map)
        except:
            print("Failed to process hook:\n{}".format(detail))
            raise


if __name__ == '__main__':
    init()
    run(host='0.0.0.0', port=8080)