"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import Cache


class Test_Cache(TestCase):

    def setUp(self):
        self.__d = {'a': 1, 'b': 2}

    def test_add_with_id(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        self.assertDictEqual(
            Cache.get('d'),
            self.__d
        )

    def test_add_wo_id(self):
        Cache.clean()
        Cache.add(self.__d)
        self.assertEqual(
            Cache.get('d'),
            None
        )

    def test_copy(self):
        Cache.clean()
        id = 'd'
        new_id = 'new_' + id
        Cache.add(self.__d, id)
        Cache.copy(id, new_id)
        self.assertDictEqual(
            Cache.get(new_id),
            self.__d
        )

    def test_copy_non_existent(self):
        Cache.clean()
        id = 'd'
        new_id = 'new_' + id
        Cache.copy(id, new_id)
        self.assertFalse(
            new_id in Cache.get_list_of_objects()
        )

    def test_log_level(self):
        Cache.clean()
        level = 40
        Cache.set_log_level(level)
        self.assertEqual(
            Cache.get_log_level(),
            level
        )

    def test_remove(self):
        Cache.clean()
        self.assertEqual(
            Cache.remove('d'),
            None
        )

    def test_remove_none(self):
        Cache.clean()
        self.assertEqual(
            Cache.remove(None),
            None
        )

    def test_rename(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        Cache.rename('d', 'd1')
        self.assertDictEqual(
            Cache.get('d1'),
            self.__d
        )
        self.assertEqual(
            Cache.get('d'),
            None
        )

    def test_rename_wrong_id(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        Cache.rename('d2', 'd1')
        self.assertEqual(
            Cache.get('d1'),
            None
        )
        self.assertDictEqual(
            Cache.get('d'),
            self.__d
        )

    def test_remove_object_by_id(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        Cache.remove_object_by_id('d')
        self.assertEqual(
            Cache.get('d'),
            None
        )

    def test_remove_object_by_wrong_id(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        Cache.remove_object_by_id('d1')
        self.assertDictEqual(
            Cache.get('d'),
            self.__d
        )

    def test_get_wrong_id(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        self.assertEqual(
            Cache.get('d1'),
            None
        )

    def test_get_objects(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        self.assertDictEqual(
            Cache.get_objects(),
            {'d': self.__d}
        )

    def test_get_list_of_objects(self):
        Cache.clean()
        Cache.add(self.__d, 'd')
        self.assertListEqual(
            Cache.get_list_of_objects(),
            ['d']
        )

