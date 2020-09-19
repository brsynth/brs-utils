"""
Created on Sep 11 2020

@author: Joan Hérisson
"""

from bisect import insort as bisect_insort

## Function to insert and/or replace sbml item in sbml items list
#
#  @param item item to insert
#  @param list sorted list of items to insert item
#  @return updated list
def insert_and_or_replace_in_sorted_list(item, list):
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
