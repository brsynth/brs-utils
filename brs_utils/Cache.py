"""A class to represent a cache of objects."""
# The MIT License (MIT)
#
# Copyright (c) 2018 Institute for Molecular Systems Biology, ETH Zurich.
# Copyright (c) 2019 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from typing import (
    Dict,
    List,
    TypeVar
)
from logging import (
    Logger,
    getLogger,
    ERROR
)
from copy import deepcopy


class Cache:

    # static and private
    __objects = {}
    __logger = getLogger(__name__)
    __logger.setLevel(ERROR)

    @staticmethod
    def set_log_level(level: int) -> None:
        Cache.__logger.setLevel(level)

    @staticmethod
    def get_log_level() -> None:
        return Cache.__logger.level

    @staticmethod
    def add(obj: TypeVar, id: str = None) -> None:
        '''
        Add an object to the cache.

        Parameters
        ----------
        object: TypeVar
            The object to add
        id: str
            ID of the object to add
        '''
        if id is None:
            try:
                id = obj.get_id()
            except AttributeError:
                Cache.__logger.error(f'id is not given and obj has no attribute get_id, nothing added')
        Cache.__objects[id] = obj

    @staticmethod
    def touch(obj: TypeVar, id: str = None) -> None:
        '''
        Add an object to the cache if does not exist, do nothing otherwise.

        Parameters
        ----------
        object: TypeVar
            The object to add
        id: str
            ID of the object to add
        '''
        if Cache.get(id) is None:
            Cache.add(id=id, obj=None)

    @staticmethod
    def remove(obj: TypeVar) -> None:
        '''
        Del an object from the cache.

        Parameters
        ----------
        object: TypeVar
            The object to remove
        '''
        if obj is not None:
            try:
                # Find object by ID
                Cache.remove_object_by_id(
                    list(Cache.get_objects().keys())[list(Cache.get_objects().values()).index(object)]
                )
            except ValueError:
                Cache.__logger.warning(f'No such object {id} found in cache, nothing deleted.')
        else:
            Cache.__logger.warning(f'Object passed is None, nothing deleted.')

    @staticmethod
    def clean() -> None:
        '''
        Remove all objects from the cache.
        '''
        for obj_id in Cache.get_list_of_objects():
            Cache.remove_object_by_id(obj_id)

    @staticmethod
    def rename(id: str, new_id: str) -> None:
        '''
        Rename an object of the cache.

        Parameters
        ----------
        id: str
            ID of the object to rename from
        new_id: str
            ID of the object to rename to
        '''
        Cache.copy(id, new_id)
        Cache.remove_object_by_id(id)

    @staticmethod
    def copy(id: str, new_id: str) -> None:
        '''
        Copy an object of the cache.

        Parameters
        ----------
        id: str
            ID of the object to copy from
        new_id: str
            ID of the object to copy to
        '''
        if id not in Cache.get_list_of_objects():
            Cache.__logger.warning(f'Compound {id} already in cache, nothing added.')
        else:
            Cache.__objects[new_id] = deepcopy(Cache.get(id))

    @staticmethod
    def remove_object_by_id(id: str) -> None:
        '''
        Del an object from the cache by ID.

        Parameters
        ----------
        id: str
            ID of the object to remove
        '''
        try:
            del Cache.__objects[id]
        except KeyError:
            Cache.__logger.warning(f'No such object {id} found in cache, nothing deleted.')

    @staticmethod
    def get(id: str) -> TypeVar:
        '''
        Return the object with ID from the cache

        Parameters
        ----------
        id: str
            ID of the object to return from the cache

        Returns
        -------
        object: TypeVar
            The object with the given ID
        '''
        try:
            return Cache.get_objects()[id]
        except KeyError:
            return None

    @staticmethod
    def get_objects() -> Dict:
        '''
        Return a dictionary of all objects in the cache.

        Returns
        -------
        objects: Dict
            All objects in the cache
        '''
        return Cache.__objects

    @staticmethod
    def get_list_of_objects() -> List[str]:
        '''
        Return IDs of all objects in the cache.

        Returns
        -------
        object_ids: List
            All object IDs in the cache
        '''
        return list(Cache.__objects.keys())

