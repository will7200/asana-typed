from asana_typed.query import Query
from asana_typed.asana import Resource, WorkSpace, Photo, User, \
    Tag, Membership, Task, ProjectStatus, Project

from asana_typed.asana import task_from_dict

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
