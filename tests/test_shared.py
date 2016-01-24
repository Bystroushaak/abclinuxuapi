#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import pytest

from abclinuxuapi import shared

# Tests =======================================================================
def test_url_context():
    assert shared.url_context("hello") == "https://www.abclinuxu.cz/hello"


def test_date_to_timestamp():
    assert shared.date_to_timestamp("10.2. 18:59 ") >= 1423591140.0
    assert shared.date_to_timestamp("2.10.2011 18:20") == 1317572400.0


def test_first():
    assert shared.first([1, 2, 3]) == 1
    assert shared.first([1]) == 1

    with pytest.raises(StopIteration):
        assert shared.first([])

    with pytest.raises(TypeError):
        assert shared.first(1)
