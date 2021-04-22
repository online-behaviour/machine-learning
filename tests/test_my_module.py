#!/usr/bin/env python

"""Tests for the machine_learning.my_module module.
"""
import pytest
from machine_learning import my_module


def test_something():
    assert True


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise(ValueError)


# Fixture example
@pytest.fixture
def an_object():
    return {}


def test_my_module(an_object):
    assert an_object == {}
