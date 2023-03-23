from sqlitedict import SqliteDict
from pyrfc import TIDStatus, StatusRC

class ServerDB:

    def __len__(self):
        return len(self.__db)

    def __setitem__(self, tid, item):
        self.__db[tid] = item

    def __getitem__(self, tid):
        if tid in self.__db:
            return self.__db[tid]
        else:
            return None

    def __repr__(self):
        return repr(self.__db)

    def __delitem__(self, tid):
        del self.__db[id]

    def clear(self):
        return self.__db.clear()

    def keys(self):
        return self.__db.keys()

    def values(self):
        return self.__db.values()

    def items(self):
        return self.__db.items()

    def pop(self, *args):
        return self.__db.pop(*args)

    def __contains__(self, item):
        return item in self.__db

    def __iter__(self):
        return iter(self.__db)

    def getTIDs(self, tids=[]):
        if len(tids) == 0:
            return self.__db
        else:
            TIDS = {}
            for id, tid in self.__db.items():
                if id in tids:
                    TIDS[id] = tid
            return TIDS

    def __init__(self, dbpath="./examples/server/serverdb.sqlite"):
        self.__db = SqliteDict(dbpath, autocommit=True)

    def close(self):
        self.__db.close()

if __name__ == "__main__":
    db = ServerDB()

    for k, v in db.items():
        print(k, v)
