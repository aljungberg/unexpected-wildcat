from unittest.mock import patch, ANY

from boddle import boddle
from nose.tools import eq_

import server
from task_tagger_test import my_vcr


@patch('task_tagger.on_task_update')
@my_vcr.use_cassette('fixtures/vcr_cassettes/init.yaml')
def test_post_hook__with_task_data__should_invoke_task_handler(on_task_update):
    server.init()
    with boddle(json={'triggers': [{'phid': 'PHID-USER-4mhnzzmliamzna2ybxoq'}], 'object': {'phid': 'PHID-TASK-djleagj2aiegvb7kzivn', 'type': 'TASK'}, 'action': {'secure': False, 'silent': False, 'epoch': 1518723688, 'test': True}, 'transactions': [{'phid': 'PHID-XACT-TASK-yw2uq4kcw6xoly3'}, {'phid': 'PHID-XACT-TASK-vur4yo7rbjgav3m'}, {'phid': 'PHID-XACT-TASK-3oreybprcelj4yi'}, {'phid': 'PHID-XACT-TASK-yzncx4yjf4xu27v'}, {'phid': 'PHID-XACT-TASK-gokjdxv26og6fcx'}, {'phid': 'PHID-XACT-TASK-bx5c6o56rcrsqol'}, {'phid': 'PHID-XACT-TASK-4sijbzxe4zwas6v'}, {'phid': 'PHID-XACT-TASK-ma5huuuk4df4fz7'}, {'phid': 'PHID-XACT-TASK-lwscf4bkcmpnrus'}, {'phid': 'PHID-XACT-TASK-4otbxttzngta6pd'}]}):
        server.receive_hook()
        on_task_update.assert_called_once_with(ANY, phid="PHID-TASK-djleagj2aiegvb7kzivn", tag_map=ANY)


@my_vcr.use_cassette('fixtures/vcr_cassettes/init.yaml')
def test_get_root__should_return_200():
    server.init()
    eq_(server.index(), "{}")
