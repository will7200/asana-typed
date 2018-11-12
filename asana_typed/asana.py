from datetime import datetime
from typing import Any, List, TypeVar, Callable, Type, cast, Optional

import dateutil.parser

T = TypeVar("T")


class MissingKey(Exception):
    pass


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except MissingKey as ms:
            raise ms
        except Exception as e:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    if x is None:
        return datetime.min
    return dateutil.parser.parse(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class BaseRep(object):
    id: int

    def __repr__(self):
        return f"{self.__class__.__name__} id:{self.id}"


resource_required_keys = {'id', 'gid', 'name', 'resource_type'}


class Resource(BaseRep):
    id: int
    gid: str
    name: str
    resource_type: str

    def __init__(self, id: int, gid: str, name: str, resource_type: str) -> None:
        self.id = id
        self.gid = gid
        self.name = name
        self.resource_type = resource_type

    @staticmethod
    def from_dict(obj: Any) -> 'Resource':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        name = from_str(obj.get("name"))
        resource_type = from_str(obj.get("resource_type"))
        return Resource(id, gid, name, resource_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["name"] = from_str(self.name)
        result["resource_type"] = from_str(self.resource_type)
        return result

    def fetch(self, client):
        try:
            return getattr(self, "__fetch__{}__".format(self.resource_type))(client)
        except AttributeError:
            print('Make Fetching method for {}'.format(self.resource_type))
            t = getattr(client, self.resource_type + 's')
            if t is not None:
                return t.find_by_id(self.id)
        raise Exception("Unknown Resource Type " + self.resource_type)

    def __fetch__follower__(self, client):
        return self.__fetch__user__(client)

    def __fetch__user__(self, client):
        return User.from_dict(client.users.find_by_id(self.id))

    def __fetch__workspace__(self, client):
        return WorkSpace.from_dict(client.workspaces.find_by_id(self.id))

    def __fetch__tag__(self, client):
        return Tag.from_dict(client.tags.find_by_id(self.id))

    def __fetch__project__(self, client):
        return Project.from_dict(client.projects.find_by_id(self.id))

    def __fetch__task__(self, client):
        return Task.from_dict(client.tasks.find_by_id(self.id))


workspace_required_keys = {'id', 'gid', 'email_domains', 'is_organization', 'name', 'resource_type'}


class WorkSpace(BaseRep):
    id: int
    gid: str
    email_domains: List[str]
    is_organization: bool
    name: str
    resource_type: str

    def __init__(self, id: int, gid: str, email_domains: List[str], is_organization: bool, name: str,
                 resource_type: str) -> None:
        self.id = id
        self.gid = gid
        self.email_domains = email_domains
        self.is_organization = is_organization
        self.name = name
        self.resource_type = resource_type

    @staticmethod
    def from_dict(obj: Any) -> 'WorkSpace':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        email_domains = from_list(from_str, obj.get("email_domains"))
        is_organization = from_bool(obj.get("is_organization"))
        name = from_str(obj.get("name"))
        resource_type = from_str(obj.get("resource_type"))
        return WorkSpace(id, gid, email_domains, is_organization, name, resource_type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["email_domains"] = from_list(from_str, self.email_domains)
        result["is_organization"] = from_bool(self.is_organization)
        result["name"] = from_str(self.name)
        result["resource_type"] = from_str(self.resource_type)
        return result


class Photo:
    image_21_x21: str
    image_27_x27: str
    image_36_x36: str
    image_60_x60: str
    image_128_x128: str

    def __init__(self, image_21_x21: str, image_27_x27: str, image_36_x36: str, image_60_x60: str,
                 image_128_x128: str) -> None:
        self.image_21_x21 = image_21_x21
        self.image_27_x27 = image_27_x27
        self.image_36_x36 = image_36_x36
        self.image_60_x60 = image_60_x60
        self.image_128_x128 = image_128_x128

    @staticmethod
    def from_dict(obj: Any) -> 'Photo':
        assert isinstance(obj, dict)
        image_21_x21 = from_str(obj.get("image_21x21"))
        image_27_x27 = from_str(obj.get("image_27x27"))
        image_36_x36 = from_str(obj.get("image_36x36"))
        image_60_x60 = from_str(obj.get("image_60x60"))
        image_128_x128 = from_str(obj.get("image_128x128"))
        return Photo(image_21_x21, image_27_x27, image_36_x36, image_60_x60, image_128_x128)

    def to_dict(self) -> dict:
        result: dict = {}
        result["image_21x21"] = from_str(self.image_21_x21)
        result["image_27x27"] = from_str(self.image_27_x27)
        result["image_36x36"] = from_str(self.image_36_x36)
        result["image_60x60"] = from_str(self.image_60_x60)
        result["image_128x128"] = from_str(self.image_128_x128)
        return result


user_required_keys = {'id', 'gid', 'email', 'name', 'photo', 'resource_type', 'workspaces'}


class User(BaseRep):
    id: int
    gid: str
    email: str
    name: str
    photo: Photo
    resource_type: str
    workspaces: List[Resource]

    def __init__(self, id: int, gid: str, email: str, name: str, photo: Photo, resource_type: str,
                 workspaces: List[Resource]) -> None:
        self.id = id
        self.gid = gid
        self.email = email
        self.name = name
        self.photo = photo
        self.resource_type = resource_type
        self.workspaces = workspaces

    @staticmethod
    def from_dict(obj: Any) -> 'User':
        assert isinstance(obj, dict)
        set_keys = user_required_keys.difference(set(obj.keys()))
        if len(set_keys) > 0:
            raise MissingKey(
                f"Following keys are missing:\n{', '.join(list(set_keys))}")
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        email = from_str(obj.get("email"))
        name = from_str(obj.get("name"))
        photo = Photo.from_dict(obj.get("photo"))
        resource_type = from_str(obj.get("resource_type"))
        workspaces = from_list(Resource.from_dict, obj.get("workspaces"))
        return User(id, gid, email, name, photo, resource_type, workspaces)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["email"] = from_str(self.email)
        result["name"] = from_str(self.name)
        result["photo"] = to_class(Photo, self.photo)
        result["resource_type"] = from_str(self.resource_type)
        result["workspaces"] = from_list(lambda x: to_class(Resource, x), self.workspaces)
        return result


def user_from_dict(s: Any) -> User:
    return User.from_dict(s)


def user_to_dict(x: User) -> Any:
    return to_class(User, x)


tag_required_keys = {'id', 'gid', 'color', 'created_at', 'followers', 'name', 'notes', 'resource_type', 'workspace'}


class Tag(BaseRep):
    id: int
    gid: str
    color: str
    created_at: datetime
    followers: List[Resource]
    name: str
    notes: str
    resource_type: str
    workspace: Resource

    def __init__(self, id: int, gid: str, color: str, created_at: datetime, followers: List[Resource], name: str,
                 notes: str,
                 resource_type: str, workspace: Resource) -> None:
        self.id = id
        self.gid = gid
        self.color = color
        self.created_at = created_at
        self.followers = followers
        self.name = name
        self.notes = notes
        self.resource_type = resource_type
        self.workspace = workspace

    @staticmethod
    def from_dict(obj: Any) -> 'Tag':
        assert isinstance(obj, dict)
        set_keys = tag_required_keys.difference(set(obj.keys()))
        if len(set_keys) > 0:
            raise MissingKey(
                f"Following keys are missing:\n{', '.join(list(set_keys))}")
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        color = from_str(obj.get("color"))
        created_at = from_datetime(obj.get("created_at"))
        followers = from_list(lambda x: x, obj.get("followers"))
        name = from_str(obj.get("name"))
        notes = from_str(obj.get("notes"))
        resource_type = from_str(obj.get("resource_type"))
        workspace = Resource.from_dict(obj.get("workspace"))
        return Tag(id, gid, color, created_at, followers, name, notes, resource_type, workspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["color"] = from_str(self.color)
        result["created_at"] = self.created_at.isoformat()
        result["followers"] = from_list(lambda x: x, self.followers)
        result["name"] = from_str(self.name)
        result["notes"] = from_str(self.notes)
        result["resource_type"] = from_str(self.resource_type)
        result["workspace"] = to_class(Resource, self.workspace)
        return result


class Membership:
    project: Optional[Resource]
    section: Optional[Resource]

    def __init__(self, project: Optional[Resource], section: Optional[Resource]) -> None:
        self.project = project
        self.section = section

    @staticmethod
    def from_dict(obj: Any) -> 'Membership':
        assert isinstance(obj, dict)
        project = from_union([Resource.from_dict, from_none], obj.get("project"))
        section = from_union([Resource.from_dict, from_none], obj.get("section"))
        return Membership(project, section)

    def to_dict(self) -> dict:
        result: dict = {}
        result["project"] = from_union([lambda x: to_class(Resource, x), from_none], self.project)
        result["section"] = from_union([lambda x: to_class(Resource, x), from_none], self.section)
        return result


task_required_keys = {'id', 'gid', 'assignee', 'assignee_status', 'completed', 'completed_at', 'created_at', 'due_at',
                      'due_on', 'followers', 'hearted', 'hearts', 'liked', 'likes', 'memberships', 'modified_at',
                      'name', 'notes', 'num_hearts', 'num_likes', 'parent', 'projects', 'resource_type', 'start_on',
                      'tags', 'resource_subtype', 'workspace'}


class Task(BaseRep):
    id: int
    gid: str
    assignee: Resource
    assignee_status: str
    completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    due_at: Optional[datetime]
    due_on: Optional[datetime]
    followers: List[Resource]
    hearted: bool
    hearts: List[Any]
    liked: bool
    likes: List[Any]
    memberships: List[Membership]
    modified_at: datetime
    name: str
    notes: str
    num_hearts: int
    num_likes: int
    parent: Resource
    projects: List[Resource]
    resource_type: str
    start_on: Optional[datetime]
    tags: List[Resource]
    resource_subtype: str
    workspace: Resource

    def __init__(self, id: int, gid: str, assignee: Resource, assignee_status: str, completed: bool,
                 completed_at: datetime, created_at: datetime, due_at: None, due_on: None, followers: List[Resource],
                 hearted: bool, hearts: List[Any], liked: bool, likes: List[Any], memberships: List[Membership],
                 modified_at: datetime, name: str, notes: str, num_hearts: int, num_likes: int, parent: Resource,
                 projects: List[Resource], resource_type: str, start_on: None, tags: List[Resource],
                 resource_subtype: str,
                 workspace: Resource) -> None:
        self.id = id
        self.gid = gid
        self.assignee = assignee
        self.assignee_status = assignee_status
        self.completed = completed
        self.completed_at = completed_at
        self.created_at = created_at
        self.due_at = due_at
        self.due_on = due_on
        self.followers = followers
        self.hearted = hearted
        self.hearts = hearts
        self.liked = liked
        self.likes = likes
        self.memberships = memberships
        self.modified_at = modified_at
        self.name = name
        self.notes = notes
        self.num_hearts = num_hearts
        self.num_likes = num_likes
        self.parent = parent
        self.projects = projects
        self.resource_type = resource_type
        self.start_on = start_on
        self.tags = tags
        self.resource_subtype = resource_subtype
        self.workspace = workspace

    @staticmethod
    def from_dict(obj: Any) -> 'Task':
        assert isinstance(obj, dict)
        set_keys = task_required_keys.difference(set(obj.keys()))
        if len(set_keys) > 0:
            raise MissingKey(
                f"Following keys are missing:\n{', '.join(list(set_keys))}")
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        assignee = Resource.from_dict(obj.get("assignee"))
        assignee_status = from_str(obj.get("assignee_status"))
        completed = from_bool(obj.get("completed"))
        completed_at = from_union([from_datetime, from_none], obj.get("completed_at"))
        created_at = from_datetime(obj.get("created_at"))
        due_at = from_union([from_datetime, from_none], obj.get("due_at"))
        due_on = from_union([from_datetime, from_none], obj.get("due_on"))
        followers = from_list(Resource.from_dict, obj.get("followers"))
        hearted = from_bool(obj.get("hearted"))
        hearts = from_list(lambda x: x, obj.get("hearts"))
        liked = from_bool(obj.get("liked"))
        likes = from_list(lambda x: x, obj.get("likes"))
        memberships = from_list(lambda x: Membership.from_dict(x), obj.get("memberships"))
        modified_at = from_datetime(obj.get("modified_at"))
        name = from_str(obj.get("name"))
        notes = from_str(obj.get("notes"))
        num_hearts = from_int(obj.get("num_hearts"))
        num_likes = from_int(obj.get("num_likes"))
        parent = from_union([Resource.from_dict, from_none], obj.get("parent"))
        projects = from_list(lambda x: Resource.from_dict(x), obj.get("projects"))
        resource_type = from_str(obj.get("resource_type"))
        start_on = from_none(obj.get("start_on"))
        tags = from_list(lambda x: Resource.from_dict(x), obj.get("tags"))
        resource_subtype = from_str(obj.get("resource_subtype"))
        workspace = Resource.from_dict(obj.get("workspace"))
        return Task(id, gid, assignee, assignee_status, completed, completed_at, created_at, due_at, due_on, followers,
                    hearted, hearts, liked, likes, memberships, modified_at, name, notes, num_hearts, num_likes, parent,
                    projects, resource_type, start_on, tags, resource_subtype, workspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["assignee"] = to_class(Resource, self.assignee)
        result["assignee_status"] = from_str(self.assignee_status)
        result["completed"] = from_bool(self.completed)
        result["completed_at"] = from_union([lambda x: x.isoformat(), from_none], self.completed_at)
        result["created_at"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["due_at"] = from_union([lambda x: x.isoformat(), from_none], self.due_at)
        result["due_on"] = from_union([lambda x: x.isoformat(), from_none], self.due_on)
        result["followers"] = from_list(lambda x: to_class(Resource, x), self.followers)
        result["hearted"] = from_bool(self.hearted)
        result["hearts"] = from_list(lambda x: x, self.hearts)
        result["liked"] = from_bool(self.liked)
        result["likes"] = from_list(lambda x: x, self.likes)
        result["memberships"] = from_list(lambda x: to_class(Membership, x), self.memberships)
        result["modified_at"] = self.modified_at.isoformat()
        result["name"] = from_str(self.name)
        result["notes"] = from_str(self.notes)
        result["num_hearts"] = from_int(self.num_hearts)
        result["num_likes"] = from_int(self.num_likes)
        result["parent"] = from_union([lambda x: to_class(Resource, x), from_none], self.parent)
        result["projects"] = from_union([lambda x: from_list(lambda y: to_class(Resource, y), x), from_none],
                                        self.projects)
        result["resource_type"] = from_str(self.resource_type)
        result["start_on"] = from_none(self.start_on)
        result["tags"] = from_union([lambda x: from_list(lambda y: to_class(Resource, y), x), from_none], self.tags)
        result["resource_subtype"] = from_str(self.resource_subtype)
        result["workspace"] = to_class(Resource, self.workspace)
        return result


def task_from_dict(s: Any) -> Task:
    return Task.from_dict(s)


def task_to_dict(x: Task) -> Any:
    return to_class(Task, x)


project_status_required_keys = {'id', 'gid', 'author', 'color', 'created_at', 'created_by', 'modified_at',
                                'resource_type', 'text'}


class ProjectStatus:
    id: int
    gid: str
    author: Resource
    color: str
    created_at: datetime
    created_by: Resource
    modified_at: datetime
    resource_type: str
    text: str

    def __init__(self, id: int, gid: str, author: Resource, color: str, created_at: datetime, created_by: Resource,
                 modified_at: datetime, resource_type: str, text: str) -> None:
        self.id = id
        self.gid = gid
        self.author = author
        self.color = color
        self.created_at = created_at
        self.created_by = created_by
        self.modified_at = modified_at
        self.resource_type = resource_type
        self.text = text

    @staticmethod
    def from_dict(obj: Any) -> 'ProjectStatus':
        assert isinstance(obj, dict)
        if project_status_required_keys.difference(set(obj.keys())).__len__() > 0:
            print('raising')
            raise MissingKey(
                f"Following keys are missing:\n{','.join(list(project_status_required_keys.difference(set(obj.keys()))))}")
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        author = Resource.from_dict(obj.get("author"))
        color = from_str(obj.get("color"))
        created_at = from_datetime(obj.get("created_at"))
        created_by = Resource.from_dict(obj.get("created_by"))
        modified_at = from_datetime(obj.get("modified_at"))
        resource_type = from_str(obj.get("resource_type"))
        text = from_str(obj.get("text"))
        return ProjectStatus(id, gid, author, color, created_at, created_by, modified_at, resource_type, text)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["author"] = to_class(Resource, self.author)
        result["color"] = from_str(self.color)
        result["created_at"] = self.created_at.isoformat()
        result["created_by"] = to_class(Resource, self.created_by)
        result["modified_at"] = self.modified_at.isoformat()
        result["resource_type"] = from_str(self.resource_type)
        result["text"] = from_str(self.text)
        return result


def project_status_from_dict(s: Any) -> ProjectStatus:
    return ProjectStatus.from_dict(s)


def project_status_to_dict(x: ProjectStatus) -> Any:
    return to_class(ProjectStatus, x)


class Project(BaseRep):
    id: int
    gid: str
    archived: bool
    color: Optional[str]
    created_at: datetime
    current_status: Optional[ProjectStatus]
    due_date: Optional[datetime]
    followers: Optional[List[Resource]]
    layout: Optional[str]
    members: Optional[List[Resource]]
    modified_at: Optional[datetime]
    name: str
    notes: str
    owner: Optional[Resource]
    public: bool
    resource_type: Optional[str]
    start_on: Optional[datetime]
    team: Optional[Resource]
    workspace: Optional[Resource]

    def __init__(self, id: int, gid: str, archived: bool, color: Optional[str],
                 created_at: datetime, current_status: Optional[ProjectStatus], due_date: Optional[datetime],
                 followers: Optional[List[Resource]],
                 layout: Optional[str], members: Optional[List[Resource]], modified_at: datetime,
                 name: str, notes: str, owner: Optional[Resource], public: bool,
                 resource_type: Optional[str], start_on: Optional[datetime], team: Optional[Resource],
                 workspace: Optional[Resource]) -> None:
        self.id = id
        self.gid = gid
        self.archived = archived
        self.color = color
        self.created_at = created_at
        self.current_status = current_status
        self.due_date = due_date
        self.followers = followers
        self.layout = layout
        self.members = members
        self.modified_at = modified_at
        self.name = name
        self.notes = notes
        self.owner = owner
        self.public = public
        self.resource_type = resource_type
        self.start_on = start_on
        self.team = team
        self.workspace = workspace

    @staticmethod
    def from_dict(obj: Any) -> 'Project':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        gid = from_str(obj.get("gid"))
        archived = from_bool(obj.get("archived"))
        color = from_union([from_str, from_none], obj.get("color"))
        created_at = from_datetime(obj.get("created_at"))
        current_status = from_union([ProjectStatus.from_dict, from_none], obj.get("current_status"))
        due_date = from_union([from_datetime, from_none], obj.get("due_date"))
        followers = from_union([lambda x: from_list(Resource.from_dict, x), from_none], obj.get("followers"))
        layout = from_union([from_str, from_none], obj.get("layout"))
        members = from_union([lambda x: from_list(Resource.from_dict, x), from_none], obj.get("members"))
        modified_at = from_datetime(obj.get("modified_at"))
        name = from_str(obj.get("name"))
        notes = from_str(obj.get("notes"))
        owner = from_union([Resource.from_dict, from_none], obj.get("owner"))
        public = from_bool(obj.get("public"))
        resource_type = from_union([from_str, from_none], obj.get("resource_type"))
        start_on = from_union([from_datetime, from_none], obj.get("start_on"))
        team = from_union([Resource.from_dict, from_none], obj.get("team"))
        workspace = from_union([Resource.from_dict, from_none], obj.get("workspace"))
        return Project(id, gid, archived, color, created_at, current_status, due_date, followers, layout, members,
                       modified_at, name, notes, owner, public, resource_type, start_on, team, workspace)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["gid"] = from_str(self.gid)
        result["archived"] = from_bool(self.archived)
        result["color"] = from_union([from_str, from_none], self.color)
        result["created_at"] = from_union([lambda x: x.isoformat(), from_none], self.created_at)
        result["current_status"] = from_none(self.current_status)
        result["due_date"] = from_union([lambda x: x.isoformat(), from_none], self.due_date)
        result["followers"] = from_union([lambda x: from_list(lambda x: to_class(Resource, x), x), from_none],
                                         self.followers)
        result["layout"] = from_union([from_str, from_none], self.layout)
        result["members"] = from_union([lambda x: from_list(lambda x: to_class(Resource, x), x), from_none],
                                       self.members)
        result["modified_at"] = from_union([lambda x: x.isoformat(), from_none], self.modified_at)
        result["name"] = from_str(self.name)
        result["notes"] = from_str(self.notes)
        result["owner"] = from_union([lambda x: to_class(Resource, x), from_none], self.owner)
        result["public"] = from_bool(self.public)
        result["resource_type"] = from_union([from_str, from_none], self.resource_type)
        result["start_on"] = from_union([lambda x: x.isoformat(), from_none], self.start_on)
        result["team"] = from_union([lambda x: to_class(Resource, x), from_none], self.team)
        result["workspace"] = from_union([lambda x: to_class(Resource, x), from_none], self.workspace)
        return result


def project_from_dict(s: Any) -> Project:
    return Project.from_dict(s)


def project_to_dict(x: Project) -> Any:
    return to_class(Project, x)
