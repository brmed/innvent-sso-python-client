# coding: utf-8
import unittest


class TestBogus(unittest.TestCase):

    def test_assert_equal(self):
        self.assertEqual(2, 1+1)

    def test_assert_true(self):
        self.assertTrue(True)
