import os
import uuid
from datetime import datetime
from pyrfc import TIDStatus

# default dbpath
DBPATH = "./examples/server/tlog.log"

class TLog:

    def __len__(self):
        try:
            with open(self.__fn, 'r') as fp:
                return len(fp.readlines())
        except IOError:
            return 0

    def __getitem__(self, tid):
        item = None
        try:
            with open(self.__fn, 'r') as fp:
                for line in fp:
                    if tid in line:
                        item = self.parse_line(line)
            return item
        except IOError:
            return None

    def clear(self):
        try:
            os.remove(self.__fn)
        except IOError:
            pass

    def __contains__(self, tid):
        try:
            with open(self.__fn, 'r') as fp:
                for line in fp:
                    if tid in line:
                        return True
            return False
        except IOError:
            return False

    def parse_line(self, line):
        try:
            utc_date, utc_time, tid, status, *note = line.split()
            tid = {
                "utc": f"{utc_date} {utc_time}",
                "tid": tid,
                "status": status
            }
            if len(note) > 0:
                tid["note"] = note[0]
            return tid
        except Exception:
            raise Exception(f"TLOG line format invalid: '{line}'")

    def getTIDs(self, tids=[]):
        if type(tids) == str:
            tids = []
        if len(tids) == 0:
            return []
        else:
            TIDs = []
            try:
                with open(self.__fn, 'r') as fp:
                    for line in fp:
                        for id in tids:
                            if id in line:
                                TIDs.append(self.parse_line(line))
                return TIDs
            except IOError:
                return []

    def __init__(self, dbpath=DBPATH):
        self.__fn = dbpath

    def write(self, tid, status, note=None):
        if len(tid) != 32:
            raise Exception(f"TID length not 32: '{tid}'")
        if status not in TIDStatus:
            raise Exception(f"TID status '{status}' not supported for tid '{tid}'")
        note = note = ' ' + note if note is not None else ''
        tlog_record = f"{datetime.utcnow()} {tid} {status.name}{note}"
        with open(self.__fn, "a") as f:
            f.write(tlog_record + "\n")
        return self.parse_line(tlog_record)

    def uuid(self):
        return uuid.uuid4().hex.upper()

    def dump(self):
        try:
            with open(self.__fn, 'r') as fp:
                for line in fp:
                    print(line[:-1])
        except IOError:
            pass

if __name__ == "__main__":

    log = TLog()

    id = "E976E679968945779C095FE7FC56AE97"

    id = log.uuid()

    log.write(id, TIDStatus.created)
    log.write(id, TIDStatus.executed, "python_function_module")

    print(id in log)

    print(log[id])

    print(len(log))

    # log.clear()

    # print(len(log))
