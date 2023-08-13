from typing import Any


BEGIN = (0, 0)

to_infinity_from = (lambda start: (yield from (lambda y: (yield from (((lambda z: z.append(z[0]+1) or z.pop(0))(y)) for _ in iter(int, 1))))([start])))


class String_CRDT_Cloud:
    def __init__(self):
        self.content = []
        self.uuids = []
        self.version = 1

    def insert_character(self, sequence_id, actor_id, char, after_uuid):
        index = 0
        uuid = (sequence_id, actor_id)
        if after_uuid!=BEGIN:
            index = self.uuids.index(after_uuid) + 1
        while index < len(self.content) and uuid < self.uuids[index]:
            index+=1
        self.content.insert(index, char)
        self.uuids.insert(index, uuid)
        self.version += 1
        return self.version

    def __str__(self):
        return str(self.content)
    

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

    def insert_character(self, *args, **kwargs):
        self.driver.insert_character(*args, **kwargs)

    def __str__(self):
        return str(self.driver)

class String_CRDT_Local:
    def __init__(self):
        self.content = []
        self.uuids = []
        self.version = None

    def insert_character(self, sequence_id, actor_id, char, after_uuid):
        index = 0
        uuid = (sequence_id, actor_id)
        if after_uuid!=BEGIN:
            index = self.uuids.index(after_uuid) + 1
        while index < len(self.content) and uuid < self.uuids[index]:
            index+=1
        self.content.insert(index, char)
        self.uuids.insert(index, uuid)
    
    def __str__(self):
        return str(self.content)

class String_CRDT_Client:
    def __init__(self, driver: String_CRDT_Local):
        self.driver = driver
        self.client: String_CRDT_Server = None
        self.counter = 1

    def insert_character(self, after_index, char):
        # simulate request to cloud
        uuid = self.driver.uuids[after_index] if after_index>=0 else BEGIN
        self.driver.insert_character(self.counter, self.actor_id, char, uuid)
        version = self.client.insert_character(self.counter, self.actor_id, char, uuid)
        self.counter += 1
        return version
    
    def insert_string(self, after_index, string):
        for offset, char in enumerate(string):
            self.insert_character(after_index+offset, char)

    
    def __str__(self):
        return str(self.driver)

    def connect(self, connection):
        self.client = connection
        self.actor_id = self.client.get_client_id()

    def sync(self):
        res = self.client.check_sync(self.driver.version)
        if not res.ok:
            self.driver.content = res.get('content')
            self.driver.uuids = res.get('uuids')
            self.driver.version = res.get('version')

if __name__ == '__main__':
    driver = String_CRDT_Cloud()
    server = String_CRDT_Server(driver)
    sc1, sc2 = String_CRDT_Local(), String_CRDT_Local()
    cl1, cl2 = String_CRDT_Client(sc1), String_CRDT_Client(sc2)
    cl1.connect(server)
    cl2.connect(server)
    cl2.insert_string(-1, '123')
    for i in range(10000):
        cl1.insert_string(-1, '456')
    cl1.insert_string(2, '789')
    cl1.insert_character(1, '7')
    print(server)
