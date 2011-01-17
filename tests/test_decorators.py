from __future__ import with_statement

from nose.tools import eq_
from fudge import Fake, with_fakes

from utils import *
from fabric import decorators
from fabric.api import run, sudo, env
from fabric.context_managers import settings
from server import (server, PORT, PASSWORDS, CLIENT_PRIVKEY, USER,
    CLIENT_PRIVKEY_PASSPHRASE)
import pdb

RESPONSES = {
    'fab fake': 'remote',
}

def fake_function(*args, **kwargs):
    """
    Returns a ``fudge.Fake`` exhibiting function-like attributes.

    Passes in all args/kwargs to the ``fudge.Fake`` constructor. However, if
    ``callable`` or ``expect_call`` kwargs are not given, ``callable`` will be
    set to True by default.
    """
    # Must define __name__ to be compatible with function wrapping mechanisms
    # like @wraps().
    if 'callable' not in kwargs and 'expect_call' not in kwargs:
        kwargs['callable'] = True
    return Fake(*args, **kwargs).has_attr(__name__='fake')


@with_fakes
def test_runs_once_runs_only_once():
    """
    @runs_once prevents decorated func from running >1 time
    """
    func = fake_function(expect_call=True).times_called(1)
    task = decorators.runs_once(func)
    for i in range(2):
        task()


def test_runs_once_returns_same_value_each_run():
    """
    @runs_once memoizes return value of decorated func
    """
    return_value = "foo"
    task = decorators.runs_once(fake_function().returns(return_value))
    for i in range(2):
        eq_(task(), return_value)


class TestRunOnRemote(FabricTest):
    """
    Tests for the @run_on_remote decorator.
    """
    @server(responses=RESPONSES)
    @with_fakes
    def test_runs_on_remote(self):
        """
        @run_on_remote runs function on remote machine instead of locally
        """
        with settings(hosts=['localhost']):
            func = fake_function(callable=True).times_called(0).returns('local')
            #test server doesn't handle the ch context manager used in
            #run_on_remote unless it's an empty string
            task = decorators.run_on_remote(remote_fabfile_path='')(func)
            ret = task()
            assert ret == 'remote'
    
    @server(responses=RESPONSES)
    @with_fakes
    def test_runs_on_local(self):
        """
        @run_on_remote runs function locally if no hosts are defined
        """
        with settings(hosts=[]):
            func = fake_function(callable=True, expect_call=True).times_called(1).returns('local')
            task = decorators.run_on_remote()(func)
            ret = task()
            assert ret == 'local'

