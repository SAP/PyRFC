#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

from pyrfc import reload_ini_file, language_iso_to_sap, language_sap_to_iso

from tests.config import LANGUAGES


class TestRfcSDK:
    def test_reload_ini_file(self):
        reload_ini_file()
        # no errors expected
        assert 1 == 1

    def test_language_iso_sap(self):
        for lang_iso in LANGUAGES:
            lang_sap = language_iso_to_sap(lang_iso)
            assert lang_sap == LANGUAGES[lang_iso]["lang_sap"]
            laiso = language_sap_to_iso(lang_sap)
            assert laiso == lang_iso
