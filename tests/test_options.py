# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from pyrfc import Connection

from tests.config import CONNECTION_DEST as params


class TestOptions:
    def setup_method(self):
        self.conn = Connection(**params)
        assert self.conn.alive

    def teardown_method(self):
        self.conn.close()
        assert not self.conn.alive

    def test_pass_when_not_requested(self):
        PLNTY = "A"
        PLNNR = "00100000"
        NOT_REQUESTED = [
            "ET_COMPONENTS",
            "ET_HDR_HIERARCHY",
            "ET_MPACKAGES",
            "ET_OPERATIONS",
            "ET_OPR_HIERARCHY",
            "ET_PRTS",
            "ET_RELATIONS",
        ]
        res = self.conn.call(
            "EAM_TASKLIST_GET_DETAIL",
            {"not_requested": NOT_REQUESTED},
            IV_PLNTY=PLNTY,
            IV_PLNNR=PLNNR,
        )
        assert len(res["ET_RETURN"]) == 0

    def test_error_when_all_requested(self):
        PLNTY = "A"
        PLNNR = "00100000"
        res = self.conn.call(
            "EAM_TASKLIST_GET_DETAIL",
            IV_PLNTY=PLNTY,
            IV_PLNNR=PLNNR,
        )
        assert len(res["ET_RETURN"]) == 1
        assert res["ET_RETURN"][0] == {
            "TYPE": "E",
            "ID": "DIWP1",
            "NUMBER": "212",
            "MESSAGE": "Task list A 00100000  is not hierarchical",
            "LOG_NO": "",
            "LOG_MSG_NO": "000000",
            "MESSAGE_V1": "A",
            "MESSAGE_V2": "00100000",
            "MESSAGE_V3": "",
            "MESSAGE_V4": "",
            "PARAMETER": "HIERARCHY",
            "ROW": 0,
            "FIELD": "",
            "SYSTEM": "MMECLNT620",
        }
