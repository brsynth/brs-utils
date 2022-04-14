"""
Created on Jul 15 2020

@author: Joan Hérisson
"""

from unittest import TestCase
from brs_utils import (
    insert_and_or_replace_in_sorted_list,
    diff
)
from brs_utils.list import (
    flatten
)

class Obj():
    def __init__(self, l):
        self.l = l
    def __eq__(self, obj):
        print(self.l, obj.l)
        for i in range(0, len(obj.l)):
            if self.l[i] != obj.l[i]:
                print(i, obj.l[i])
                return False
        return True
    def __str__(self):
        return str(self.l)

class Object():
    def __init__(self, score, obj):
        self.score = score
        self.obj   = obj
    def __eq__(self, object):
        return self.obj == object.obj
    def __lt__(self, object):
        return self.score < object.score
    def __gt__(self, object):
        return self.score > object.score
    def __str__(self):
        return "Object("+str(self.score)+", "+str(self.obj)+")"

class InsertOrReplace(TestCase):
    __test__ = True

    def test_int_from_empty(self):
        l = []
        l = insert_and_or_replace_in_sorted_list(1, l)
        self.assertListEqual(l, [1])

    def test_int_from_non_empty_insert_tail(self):
        l = [1]
        l = insert_and_or_replace_in_sorted_list(2, l)
        self.assertListEqual(l, [1, 2])

    def test_int_from_non_empty_insert_head(self):
        l = [2]
        l = insert_and_or_replace_in_sorted_list(1, l)
        self.assertListEqual(l, [1, 2])

    def test_int_from_non_empty_insert_middle(self):
        l = [1,3]
        l = insert_and_or_replace_in_sorted_list(2, l)
        self.assertListEqual(l, [1, 2, 3])

    def test_Object_new(self):
        l = [Object(1, Obj([1,3,5])),
             Object(2, Obj([2,3,5])),
             Object(7, Obj([7,3,5]))]
        obj = Object(3, Obj([3,3,5]))
        l = insert_and_or_replace_in_sorted_list(obj, l)
        self.assertSequenceEqual(l, [Object(1, Obj([1,3,5])),
                                     Object(2, Obj([2,3,5])),
                                     obj,
                                     Object(7, Obj([7,3,5]))])

    def test_Object_same(self):
        l = [Object(1, Obj([1,3,5])),
             Object(2, Obj([2,3,5])),
             Object(7, Obj([7,3,5]))]
        obj = Object(1, Obj([1,3,5]))
        l2 = insert_and_or_replace_in_sorted_list(obj, l)
        self.assertSequenceEqual(l, l2)

    def test_Object_existent_better(self):
        l = [Object(1, Obj([1,3,5])),
             Object(2, Obj([2,3,5])),
             Object(7, Obj([7,3,5]))]
        obj = Object(3, Obj([1,3,5]))
        l = insert_and_or_replace_in_sorted_list(obj, l)
        self.assertSequenceEqual(l, [Object(2, Obj([2,3,5])),
                                     obj,
                                     Object(7, Obj([7,3,5]))])

    def test_Object_existent_lessgood(self):
        l = [Object(1, Obj([1,3,5])),
             Object(2, Obj([2,3,5])),
             Object(7, Obj([7,3,5]))]
        obj = Object(1, Obj([2,3,5]))
        l2 = insert_and_or_replace_in_sorted_list(obj, l)
        self.assertSequenceEqual(l, l2)


class Test_List(TestCase):

    def test_diff(self):
        l1 = [1, 2, 1, 3, 4]
        l2 = [1, 2, 3, 3]
        self.assertSequenceEqual(
            diff(l1, l2),
            [1, 4]
        )

    def test_flatten(self):
        l1 = [1, 2, 3, 4, 5]
        self.assertEqual(
            l1,
            list(flatten(l1))
        )
        l2 = [1, [2], [3, [4, [5, 6]]]]
        self.assertEqual(
            [1, 2, 3, 4, 5, 6],
            list(flatten(l2))
        )
        l3 = ['a', [2, {'b'}]]
        self.assertEqual(
            ['a', 2, 'b'],
            list(flatten(l3))
        )
