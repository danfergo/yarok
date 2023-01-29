from yarok.core.components_manager import ComponentsManager
from yarok.core.config_block import ConfigBlock
from yarok.core.component import component
from yarok.core.interface import interface
from yarok.core.behaviour import behaviour
from yarok.core.platform import Platform
from yarok.core.injector import Injector

from yarok.platforms.mjc.platform import PlatformMJC
from yarok.platforms.hw.platform import PlatformHW

__PLATFORM__ = None
__VERSION__ = '0.0.21'


def wait(fn=None, cb=None):
    global __PLATFORM__
    print('[deprecated] wait_once was replaced by platform.wait')
    __PLATFORM__.wait(fn, cb)


def wait_seconds(seconds, cb=None):
    global __PLATFORM__
    print('[deprecated] wait_seconds was replaced by platform.wait_seconds')
    __PLATFORM__.wait_seconds(seconds, cb)


def wait_forever(cb=None):
    global __PLATFORM__
    print('[deprecated] wait_forever was replaced by platform.wait_forever')
    __PLATFORM__.wait_forever(cb)


def wait_once(cb=None):
    global __PLATFORM__
    print('[deprecated] wait_once was replaced by platform.wait_once')
    __PLATFORM__.wait_once(cb)


def load(config: {}):
    global __PLATFORM__
    print('[deprecated] yarok.load was replaced by Platform.create')
    __PLATFORM__ = Platform.create(config)
    return __PLATFORM__


def run(config={}):
    global __PLATFORM__
    print('[deprecated] run was replaced by Platform.create().run()')
    __PLATFORM__ = Platform.create(config)
    __PLATFORM__.run()
