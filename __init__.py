
import typing
import sys
import string
import itertools
import bpy

DEBUG = 'DEBUG_MODE' is sys.argv

def ASSERT_DRIVER_RESOLVABLE(fn: str,
                             id: bpy.types.ID,
                             path: str,
                             index: typing.Optional[int]=None) -> None:
    assert isinstance(id, bpy.types.ID), \
        (f'{fn}(id, path, index=None): Expected id to be'
            f'{bpy.types.ID.__class__.__name__}, not {id.__class__.__name__}')
    assert isinstance(path, str), \
        f'{fn}(id, path, index=None): Expected path to be str, not {path.__class__.__name__}'
    if index is not None:
        assert isinstance(index, int), \
            f'{fn}(id, path, index=None): Expected index to be int, not {index.__class__.__name__}'
        assert index >= 0, \
            f'{fn}(id, path, index=None): Expected index to be greater than or equal to 0, not {index}'

def driver_find(id: bpy.types.ID,
                path: str,
                index: typing.Optional[int]=None) -> typing.Optional[bpy.types.FCurve]:
    """Return a driver a path (index) for the id, or None if a driver at path (index) does not exist"""
    if DEBUG:
        ASSERT_DRIVER_RESOLVABLE('driver_find', id, path, index)
    animdata = id.animation_data
    if animdata is not None:
        drivers = animdata.drivers
        return drivers.find(path) if index is None else drivers.find(path, index=index)

def driver_ensure(id: bpy.types.ID, path: str, index: typing.Optional[int]=None) -> bpy.types.FCurve:
    """Return a driver at path (index) for the id"""
    if DEBUG:
        ASSERT_DRIVER_RESOLVABLE('driver_ensure', id, path, index)
    fcurve = driver_find(id, path, index)
    if fcurve is None:
        drivers = id.animation_data_create().drivers
        fcurve = drivers.new(path) if index is None else drivers.new(path, index=index)
    return fcurve

def driver_remove(id: bpy.types.ID, path: str, index: typing.Optional[int]=None) -> None:
    """Remove the driver at path (index) for the id"""
    if DEBUG:
        ASSERT_DRIVER_RESOLVABLE('driver_remove', id, path, index)
    fcurve = driver_find(id, path, index)
    if fcurve is not None:
        fcurve.id_data.animation_data.drivers.remove(fcurve)

def driver_variables_empty(driver: bpy.types.Driver) -> bpy.types.ChannelDriverVariables:
    """Return empty variables for driver"""
    if DEBUG:
        assert isinstance(driver, bpy.types.Driver), \
            (f'driver_variables_empty(driver): Expected driver to be '
             f'{bpy.types.Driver.__class__.__name__}, not {driver.__class__.__name__}')
    variables = driver.variables
    driver_variables_clear(variables)
    return variables

def driver_variables_clear(variables: bpy.types.ChannelDriverVariables) -> None:
    """Clear driver variables"""
    if DEBUG:
        assert isinstance(variables, bpy.types.ChannelDriverVariables), \
            (f'driver_variables_clear(variables): Expected variables to be '
             f'{bpy.types.ChannelDriverVariables.__class__.__name__}, not {variables.__class__.__name__}')
    while len(variables):
        variables.remove(variables[-1])

class DriverVariableNameGenerator:
    """Generator for minimal length sequential valid driver variable names"""

    def __init__(self) -> None:
        self._index = 0
        self._chars = string.ascii_letters
        self._count = 1
        self._names = iter(self._chars)
    
    def __iter__(self) -> typing.Iterator[str]:
        return self

    def __next__(self) -> str:
        try:
            name = next(self._names)
        except StopIteration:
            self._count += 1
            self._names = itertools.product(self._chars, repeat=self._count)
            name = next(self._names)
        return name
