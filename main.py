BEGIN = (0, 0)

to_infinity_from = (lambda start: (yield from (lambda y: (yield from (((lambda z: z.append(z[0]+1) or z.pop(0))(y)) for _ in iter(int, 1))))([start])))


class String_CRDT_Cloud:
    def __init__(self):
        self.content = []
        self.uuids = []
        self.version = 1

    def insert(self, sequence_id, actor_id, char, after_uuid):
        index = 0
        uuid = (sequence_id, actor_id)
        if after_uuid!=BEGIN:
            index = self.uuids.index(after_uuid) + 1
        while index < len(self.content) and uuid < self.uuids[index]:
            index+=1
        self.content.insert(index, char)
        self.content.insert(index, uuid)
        self.version += 1
        return self.version
    

class String_CRDT_Server:
    def __init__(self, driver:String_CRDT_Cloud):
        self.new_client_id = to_infinity_from(1)
        self.driver = driver

    def check_sync(self, version):
        if self.driver.version != version:
            return {'ok': False, 'content' :self.driver.content, 'uuids': self.driver.uuids, 'version': self.driver.version}
        else:
            return {'ok': True}

    def get_client_id(self):
        return next(self.new_client_id)

class String_CRDT_Local:
    def __init__(self):
        self.content = []
        self.uuids = []
        self.version = None

    def sync(self):
        res = self.client.check_sync(self.version)
        if not res.ok:
            self.content = res.get('content')
            self.uuids = res.get('uuids')
            self.version = res.get('version')

class String_CRDT_Client:
    def __init__(self, string_crdt: String_CRDT_Local):
        self.string_crdt = string_crdt
        self.client: String_CRDT_Server = None
        self.counter = to_infinity_from(1)
        self.actor_id = self.client.get_client_id()

    def insert(self, after_index, char):
        # simulate request to cloud
        return self.client.insert(next(self.counter), self.actor_id, char, self.string_crdt.uuids[after_index])
