import os
from collections import Counter

from phabricator import Phabricator


class TagMap:
    tag_map = None

    def __init__(self, tag_map):
        self.tag_map = tag_map

    def tag_phid(self, name):
        return self.tag_map[name]['phid']

    def tag_name(self, phid):
        return next((tag['fields']['name'] for tag in self.tag_map.values() if tag['phid'] == phid), None)

    def __getattr__(self, item):
        return self.tag_map.__getattribute__(item)

    def __getitem__(self, item):
        return self.tag_phid(item)


def resolve_tags(phab):
    return TagMap({
        'has_accepted_diff_tag': phab.project.search(constraints={"name": "Accepted"})['data'][0],
        'has_diff_tag': phab.project.search(constraints={"name": "Diff"})['data'][0],
        'has_landed_diff_tag': phab.project.search(constraints={"name": "Landed"})['data'][0],
        'has_revision_required_diff_tag': phab.project.search(constraints={"name": "Reviewed"})['data'][0],
    })


def on_task_update(phab, task_id=None, phid=None, tag_map=None):
    if task_id:
        constraints = {"ids": [task_id]}
    else:
        constraints = {"phids": [phid]}

    task = phab.maniphest.search(constraints=constraints, attachments={"columns": True, "projects": True})['data'][0]

    edges = phab.edge.search(sourcePHIDs=[task['phid']], types=["task.revision"])['data']
    diff_phids = [edge['destinationPHID'] for edge in edges if edge['edgeType'] == "task.revision"]

    diffs = phab.differential.revision.search(constraints={"phids": diff_phids})['data'] if diff_phids else []
    tags_counter = Counter([diff['fields']['status']['value'] for diff in diffs])

    all_tags = {project for project in task['attachments']['projects']['projectPHIDs']}
    my_tags = all_tags.intersection({tag['phid'] for tag in tag_map.values()})
    new_tags = set()

    if tags_counter['accepted']:
        new_tags.add(tag_map['has_accepted_diff_tag'])

    if tags_counter['needs-revision']:
        new_tags.add(tag_map['has_revision_required_diff_tag'])

    if tags_counter['published']:
        new_tags.add(tag_map['has_landed_diff_tag'])

    if diffs and not new_tags:
        # If neither accepted nor reviewed, at least reveal that there is a diff.
        new_tags.add(tag_map['has_diff_tag'])

    transactions = []

    tags_to_add = new_tags - all_tags
    if tags_to_add:
        print("Tagging T{} with {}.".format(task['id'],  ", ".join(tag_map.tag_name(phid) for phid in tags_to_add)))
        transactions.append({"type": "projects.add", "value": list(tags_to_add)})

    tags_to_remove = my_tags - new_tags
    if tags_to_remove:
        print("Untagging T{} with {}.".format(task['id'],  ", ".join(tag_map.tag_name(phid) for phid in tags_to_remove)))
        transactions.append({"type": "projects.remove", "value": list(tags_to_remove)})

    if transactions:
        phab.maniphest.edit(objectIdentifier=task['phid'], transactions=transactions)


if __name__ == '__main__':
    phab = Phabricator(host=os.environ['PHABRICATOR_API_URL'], token=os.environ.get('PHABRICATOR_API_TOKEN'))
    phab.update_interfaces()

    tags = resolve_tags(phab)

    on_task_update(phab, task_id=2895, tag_map=tags)
