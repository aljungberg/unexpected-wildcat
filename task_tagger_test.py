import re
import os

import vcr
from nose.tools import eq_, ok_
from phabricator import Phabricator

from task_tagger import resolve_tags, on_task_update


def before_record_cb(request):
    # Don't save the real token used when recording the VCR cassette. Tokens are in the format 'cli-...'
    # or 'api-...'.
    request.body = re.sub(r'(cli|api)-[\w\d]+', '123', request.body.decode('utf-8')).encode('utf-8')
    return request


def before_record_response(response):
    if 'Set-Cookie' in response['headers']:
        del response['headers']['Set-Cookie']
    return response


my_vcr = vcr.VCR(
    before_record_request=before_record_cb,
    before_record_response=before_record_response,
)

@my_vcr.use_cassette('fixtures/vcr_cassettes/resolve_tags.yaml')
def test_resolve_tags__should_find_standard_tags():
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    eq_(tag_map['has_revision_required_diff_tag'], "PHID-PROJ-kx4rkibaeu6rt72oupll")
    eq_(tag_map['has_diff_tag'], "PHID-PROJ-segawqxql2j3qedl7cqc")
    eq_(tag_map['has_accepted_diff_tag'], "PHID-PROJ-72kxzxxqoak5bp2llx3m")


@my_vcr.use_cassette('fixtures/vcr_cassettes/on_update_task_2895.yaml', inject_cassette=True)
def test_on_task_update__for_task_with_needs_changes_diff__should_tag_with_reviewed_tag(cassette):
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    on_task_update(phab, 2895, tag_map=tag_map)

    eq_(cassette.requests[-1].url, "https://truecode.trueship.com/api/maniphest.edit")
    eq_(cassette.requests[-1].body, b"output=json&params=%7B%22__conduit__%22%3A+%7B%22token%22%3A+%22123%22%7D%2C+%22objectIdentifier%22%3A+%22PHID-TASK-bdaz2w2ue4nlotls6wqn%22%2C+%22transactions%22%3A+%5B%7B%22type%22%3A+%22projects.add%22%2C+%22value%22%3A+%5B%22PHID-PROJ-kx4rkibaeu6rt72oupll%22%5D%7D%5D%7D")


@my_vcr.use_cassette('fixtures/vcr_cassettes/on_update_task_3070.yaml', inject_cassette=True)
def test_on_task_update__for_task_with_accepted_diff__should_tag_with_accepted_tag(cassette):
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    on_task_update(phab, 3070, tag_map=tag_map)

    eq_(cassette.requests[-1].url, "https://truecode.trueship.com/api/maniphest.edit")
    eq_(cassette.requests[-1].body, b"params=%7B%22objectIdentifier%22%3A+%22PHID-TASK-djleagj2aiegvb7kzivn%22%2C+%22__conduit__%22%3A+%7B%22token%22%3A+%22123%22%7D%2C+%22transactions%22%3A+%5B%7B%22value%22%3A+%5B%22PHID-PROJ-72kxzxxqoak5bp2llx3m%22%5D%2C+%22type%22%3A+%22projects.add%22%7D%5D%7D&output=json")


@my_vcr.use_cassette('fixtures/vcr_cassettes/on_update_task_3109.yaml', inject_cassette=True)
def test_on_task_update__for_task_with_unreviewed_diff__should_tag_with_diff_tag(cassette):
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    on_task_update(phab, 3109, tag_map=tag_map)

    eq_(cassette.requests[-1].url, "https://truecode.trueship.com/api/maniphest.edit")
    eq_(cassette.requests[-1].body, b"params=%7B%22transactions%22%3A+%5B%7B%22value%22%3A+%5B%22PHID-PROJ-segawqxql2j3qedl7cqc%22%5D%2C+%22type%22%3A+%22projects.add%22%7D%5D%2C+%22objectIdentifier%22%3A+%22PHID-TASK-s3scdbecgvk23b4uwsfp%22%2C+%22__conduit__%22%3A+%7B%22token%22%3A+%22123%22%7D%7D&output=json")


@my_vcr.use_cassette('fixtures/vcr_cassettes/on_update_task_2895_extra_tags.yaml', inject_cassette=True)
def test_on_task_update__for_task_with_needs_changes_diff__should_remove_undesired_tags(cassette):
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    on_task_update(phab, 2895, tag_map=tag_map)

    eq_(cassette.requests[-1].url, "https://truecode.trueship.com/api/maniphest.edit")
    eq_(cassette.requests[-1].body, b"params=%7B%22objectIdentifier%22%3A+%22PHID-TASK-bdaz2w2ue4nlotls6wqn%22%2C+%22transactions%22%3A+%5B%7B%22value%22%3A+%5B%22PHID-PROJ-kx4rkibaeu6rt72oupll%22%5D%2C+%22type%22%3A+%22projects.add%22%7D%2C+%7B%22value%22%3A+%5B%22PHID-PROJ-segawqxql2j3qedl7cqc%22%2C+%22PHID-PROJ-72kxzxxqoak5bp2llx3m%22%5D%2C+%22type%22%3A+%22projects.remove%22%7D%5D%2C+%22__conduit__%22%3A+%7B%22token%22%3A+%22123%22%7D%7D&output=json")


@my_vcr.use_cassette('fixtures/vcr_cassettes/on_update_task_3073_no_diffs.yaml', inject_cassette=True)
def test_on_task_update__for_task_with_no_diff__should_remove_diff_tag(cassette):
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    tag_map = resolve_tags(phab)

    on_task_update(phab, 3073, tag_map=tag_map)

    eq_(cassette.requests[-1].url, "https://truecode.trueship.com/api/maniphest.edit")
    eq_(cassette.requests[-1].body, b"output=json&params=%7B%22objectIdentifier%22%3A+%22PHID-TASK-6mh4up4avtz2wjr2a2sd%22%2C+%22transactions%22%3A+%5B%7B%22type%22%3A+%22projects.remove%22%2C+%22value%22%3A+%5B%22PHID-PROJ-segawqxql2j3qedl7cqc%22%5D%7D%5D%2C+%22__conduit__%22%3A+%7B%22token%22%3A+%22123%22%7D%7D")
