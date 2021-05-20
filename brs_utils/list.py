"""
Created on Sep 11 2020

@author: Joan Hérisson
"""

from typing import (
    List,
    TypeVar
)
from copy import deepcopy
from bisect import insort as bisect_insort


## Class to define a generic item
#
#  @param object item
#  @param score score of the item
#  @param id id of the item
class Item:

    def __init__(
        self,
        object: TypeVar,
        score: float,
    ):
        self.object = deepcopy(object)
        self.score = score

    def __eq__(self, item):
        return self.object == item.object

    def __lt__(self, item):
        return self.score < item.score

    def __gt__(self, item):
        return self.score > item.score

    def __str__(self):
        return 'Item' + '\n' \
             + '\t' + 'score:  ' + str(self.score)      + '\n' \
             + '\t' + 'object: ' + str(self.object)      + '\n' \


## Function to insert and/or replace item in list
#
#  @param item item to insert
#  @param list sorted list of items to insert item
#  @return updated list
def insert_and_or_replace_in_sorted_list(
    item: object,
    list: List[object]
) -> List[object]:

    # If present, remove the same item with worse score from the list
    try:

        i = list.index(item)

        # new item's score is better than the one already in the list, then replace it
        if item > list[i]:
            list.pop(i)
            # Insert at the good place current item in the list
            # If the item's score is lower that the last item of the list, then it will be added at the end and cut later when only topX will be kept
            bisect_insort(list, item)

    # Same item does not exist in the list, then insert it
    except ValueError:
        # Insert at the good place current item in the list
        # If the item's score is lower that the last item of the list, then it will be added at the end and cut later when only topX will be kept
        bisect_insort(list, item)

    return list


def diff(first, second):
   l2 = list(second)
   l3 = []
   for el in first:
      if el in l2:
         l2.remove(el)
      else:
         l3 += [el]
   return l3
