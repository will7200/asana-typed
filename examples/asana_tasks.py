import calendar
import os
import textwrap
from datetime import datetime, timedelta
from email.utils import parsedate, formatdate
from typing import List

import asana
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from cachecontrol.heuristics import BaseHeuristic

from asana_typed import Project, Query
from asana_typed import Task
from asana_typed.asana import Story
from examples.tree_node import Tree
import pytz

utc = pytz.UTC


class OneWeekHeuristic(BaseHeuristic):

    def update_headers(self, response):
        date = parsedate(response.headers['date'])
        expires = datetime(*date[:6]) + timedelta(weeks=1)
        return {
            'expires': formatdate(calendar.timegm(expires.timetuple())),
            'cache-control': 'public',
        }

    def warning(self, response):
        msg = 'Automatically cached! Response is Stale.'
        return '110 - "%s"' % msg


token = os.getenv('ASANA_APP_TOKEN', "")
auth = asana.Client.access_token(token).session
sess = CacheControl(auth, cache=FileCache('.webcache'), heuristic=OneWeekHeuristic())

client = asana.Client(sess)

me = client.users.me()
workspace = me['workspaces'][0]
print("Hello " + me['name'])
week_end = datetime(2019, 1, 5)
tasks = list(
    client.tasks.find_all({'workspace': workspace['id'], 'assignee': 'me', 'completed_since': f'{week_end:%Y-%m-%d}'}))

tasks_details: List[Task] = []
issues: List[Story] = []

parents = {}
for task in tasks[:]:
    ptask = client.tasks.find_by_id(task.get('id'))
    ptask = Task.from_dict(ptask)
    tasks_details.append(ptask)
    stories = list(ptask.fetch_stories(client))
    if len(stories) > 0:
        query = Query(stories)
        sublist = query.equals('type_', 'comment').contains('text', 'ISSUE', case=False).get_list()
        if len(sublist) > 0:
            issues = issues + sublist
    if ptask.parent:
        parent = ptask.parent.__fetch__task__(client)
        if ptask.due_on == datetime.min:
            ptask.due_on = parent.due_on

data = Query(tasks_details)
completed_last_week: List[Task] = data.is_true('completed').sort_by('due_on').sort_by('completed_at', False).get_list()
planned_for_next_week: List[Task] = set(tasks_details).difference(set(completed_last_week))
planned_for_last_week: List[Task] = data.less_than('created_at', utc.localize(week_end)).greater_than(
    'due_on',
    week_end).get_list()

all_items = []


def ct(task_list):
    tree = Tree()
    tree.create_node("Root", "Root")
    for ptask in task_list:
        node_parent = "Root"
        if len(ptask.projects) > 0:
            project = ptask.projects[0].__fetch__project__(client)
            if tree.find_index(project.gid) is None:
                all_items.append(project)
                tree.create_node(project.name, project.gid, node_parent)
            node_parent = project.gid
        if ptask.parent:
            parent = ptask.parent.__fetch__task__(client)
            if len(parent.projects) > 0:
                parent_project = parent.projects[0].__fetch__project__(client)
                if tree.find_index(parent_project.gid) is None:
                    all_items.append(parent_project)
                    tree.create_node(parent_project.name, parent_project.gid, node_parent)
                node_parent = parent_project.gid
            if tree.find_index(parent.gid) is None:
                all_items.append(parent)
                tree.create_node(parent.name, parent.gid, parent=node_parent)
            node_parent = parent.gid
        if tree.find_index(ptask.gid) is None:
            all_items.append(ptask)
            node = tree.create_node(ptask.name, ptask.gid, parent=node_parent)
    return tree


clw = ct(completed_last_week)
pflw = ct(planned_for_last_week)
pfnw = ct(planned_for_next_week)


def format_identifier(asana_type):
    if isinstance(asana_type, Project):
        return asana_type.name
    elif isinstance(asana_type, Task):
        return asana_type.name


def fetch_from_list(gid):
    return format_identifier(list(filter(lambda x: x.gid == gid, all_items))[0])


md_pflw = ["{0} {1}  ".format(("\t" * (level - 1)) + '+', fetch_from_list(identifier)) for identifier, level in
           pflw.fake_show("Root", skip_root=True)]

md_clw = ["{0} {1}  ".format(("\t" * (level - 1)) + '+', fetch_from_list(identifier)) for identifier, level in
          clw.fake_show("Root", skip_root=True)]

md_pfnw = ["{0} {1}  ".format(("\t" * (level - 1)) + '+', fetch_from_list(identifier)) for identifier, level in
           pfnw.fake_show("Root", skip_root=True)]

qq = Query(issues)


def group_by_issue_text(x):
    try:
        return x.text.split('\n')[0].split('-')[1]
    except IndexError:
        return "Unknown"


grouped_issues = qq.sort_by('created_at').group_by(lambda x: group_by_issue_text(x))
issues_updates = []
for key in grouped_issues.keys():
    first_story = grouped_issues[key][0]
    issues_updates.append("{0} {1}  ".format(("\t" * 0) + '+', key))
    for issue in grouped_issues[key][:]:
        try:
            status = issue.text.split('\n')[0].split('-')[2]
        except IndexError:
            status = ''
        text = ' '.join(issue.text.split('\n')[1:])
        issues_updates.append("{0} [{1}] {2} ".format(("\t" * 1) + '+', status, text))

nl = '\n\n'
t = textwrap.dedent(f"""Planned for Last Week:  \n
{nl.join(md_pflw)}

Completed Last Week:  \n
{nl.join(md_clw)}

Planned for Next Week:  \n
{nl.join(md_pfnw)}

New Issues:  \n
{nl.join(issues_updates)}
 
Old Issues:  \n
+ None  

""")

from markdown2 import Markdown

markdowner = Markdown()

html = markdowner.convert(t)
with open('markdown.md', 'w') as f:
    f.write(t)
with open('message.html', 'w') as f:
    f.write(html)

from asana_typed import Query

q = Query(tasks_details)
q.is_set('completed').get_list()
