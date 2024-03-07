# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import uuid
from contextlib import suppress
from datetime import datetime

from pyrfc import UnitState

# default dbpath
DBPATH = "./examples/server/tlog.log"


class TLog:
    """Server transaction log implementation example."""

    def __len__(self):
        try:
            with open(self.__fn, "r") as fp:
                return len(fp.readlines())
        except IOError:
            return 0

    def __getitem__(self, tid):
        itm = None
        try:
            with open(self.__fn, "r") as fp:
                for line in fp:
                    if tid in line:
                        itm = self.parse_line(line)
            return itm
        except IOError:
            return None

    def remove(self, tid=None):
        with suppress(IOError):
            if tid is None:
                os.remove(self.__fn)
            else:
                with open(self.__fn, "r") as fp:
                    lines = fp.readlines()
                with open(self.__fn, "w") as fp:
                    for line in lines:
                        if tid not in line[:-1]:
                            fp.write(line)

    def __contains__(self, tid):
        try:
            with open(self.__fn, "r") as fp:
                for line in fp:
                    if tid in line:
                        return True
            return False
        except IOError:
            return False

    def parse_line(self, line):
        try:
            (
                utc_date,
                utc_time,
                tid,
                status,
                *note,
            ) = line.split()
            tid = {
                "utc": f"{utc_date} {utc_time}",
                "tid": tid,
                "status": status,
            }
            if len(note) > 0:
                tid["note"] = note[0]
            return tid
        except Exception:
            raise Exception(f"TLOG line format invalid: '{line}'")

    def getTIDs(self, tids=None):
        if isinstance(tids, str):
            tids = [tids]
        elif tids is None:
            tids = []
        if len(tids) == 0:
            return []
        else:
            TIDs = []
            try:
                with open(self.__fn, "r") as fp:
                    for line in fp:
                        for td in tids:
                            if td in line:
                                TIDs.append(self.parse_line(line))
                return TIDs
            except IOError:
                return []

    def __init__(self, dbpath=DBPATH):
        self.__fn = dbpath

    def write(self, tid, status, note=None):
        if len(tid) != 32:
            raise Exception(f"TID length not 32: '{tid}'")
        if status not in UnitState:
            raise Exception(f"TID status '{status}' not supported for tid '{tid}'")
        note = " " + note if note is not None else ""
        tlog_record = f"{datetime.utcnow()} {tid} {status.name}{note}"
        with open(self.__fn, "a") as file:
            file.write(tlog_record + "\n")
        return self.parse_line(tlog_record)

    def uuid(self):
        return uuid.uuid4().hex.upper()

    def dump(self):
        with suppress(IOError), open(self.__fn, "r") as fp:
            for line in fp:
                print(line[:-1])


if __name__ == "__main__":
    log = TLog()

    Id = "E976E679968945779C095FE7FC56AE97"

    Id = log.uuid()

    log.write(Id, UnitState.created)
    log.write(Id, UnitState.executed, "python_function_module")

    print(Id in log)

    print(log[Id])

    print()

    print(len(log))

    log.dump()

    # log.remove()

    # print(len(log))
