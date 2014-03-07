#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import pyrfc
from pyrfc.pool import create_engine, engine_from_config
from .config import user_engine as user, \
                    params_engine as params, \
                    passwd_engine as passwd, \
                    config_engine as config

class EngineTest(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.engine = create_engine(
            poolsize=30, precreate=1, reset_on_return=True, **params)

    @classmethod
    def tearDown(cls):
        cls.engine.disconnect()

    def test_engine_from_config(self):
        conf_engine = engine_from_config(config)
        self.assertIsInstance(conf_engine, type(self.engine))

    def test_get_user_connection(self):
        c = self.engine.get_user_connection(user, passwd)
        c.ping()

    def test_get_user_conn_again_without_pw(self):
        c = self.engine.get_user_connection(user, passwd)
        c.ping()
        c = self.engine[user]
        c.ping()

    def test_collect(self):
        self.engine.get_user_connection(user, passwd)
        poolsize_pre = self.engine._size
        normal_conn = pyrfc.Connection(user=user, passwd=passwd, **params)
        self.engine.collect(user, normal_conn)
        self.assertEqual(poolsize_pre+1, self.engine._size)

    def test_detach(self):
        conn = self.engine.get_user_connection(user, passwd)
        detached = conn.detach()
        self.assertIsInstance(detached, pyrfc.Connection)

    def test_disconnect(self):
        c = self.engine.get_user_connection(user, passwd)
        self.engine.disconnect(user)
        self.assertNotIn(user, self.engine._pool)


if __name__ == '__main__':
    unittest.main()
