# from mapserv import cmsg_name_request

def job_type(job):
    if (job <= 25 or (job >= 4001 and job <= 4049)):
        return "player"
    elif (job >= 46 and job <= 1000):
        return "npc"
    elif (job > 1000 and job <= 2000):
        return "monster"
    elif (job == 45):
        return "portal"


class Being:
    def __init__(self, being_id, job):
        self.id = being_id
        self._name = ""
        self.x = 0
        self.y = 0
        self.job = job
        self.nearby = True

    @property
    def name(self):
        if len(self._name) > 0:
            return self._name
        return "{{ID:" + str(self.id) + "}}"

    @name.setter
    def name(self, newname):
        self._name = newname

    @property
    def type(self):
        return job_type(self.job)

    def __repr__(self):
        return self.name


class BeingsCache:

    def __init__(self, name_request_func):
        self._beings = {}
        self.__getitem__ = self._beings.__getitem__
        self._name_request_func = name_request_func

    def findId(self, name, type_="player"):
        for id_ in self.keys():
            being = self._beings[id_]
            if being.name == name and being.type == type_:
                return id_
        return -10

    def findName(self, id_):
        if self._beings.has_key(id_):
            return self._beings[id_].name
        

    def add(self, id_, job):
        if id_ in self._beings:
            return
        else:
            self._beings[id_] = Being(id_, job)
            self._name_request_func(id_)
