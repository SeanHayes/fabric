"""
Convenience decorators for use in fabfiles.
"""

from functools import wraps
from types import StringTypes
from fabric.operations import run, sudo
from fabric.state import env
from fabric.context_managers import cd
import os
import pdb

def hosts(*host_list):
    """
    Decorator defining which host or hosts to execute the wrapped function on.

    For example, the following will ensure that, barring an override on the
    command line, ``my_func`` will be run on ``host1``, ``host2`` and
    ``host3``, and with specific users on ``host1`` and ``host3``::

        @hosts('user1@host1', 'host2', 'user2@host3')
        def my_func():
            pass

    `~fabric.decorators.hosts` may be invoked with either an argument list
    (``@hosts('host1')``, ``@hosts('host1', 'host2')``) or a single, iterable
    argument (``@hosts(['host1', 'host2'])``).

    Note that this decorator actually just sets the function's ``.hosts``
    attribute, which is then read prior to executing the function.

    .. versionchanged:: 0.9.2
        Allow a single, iterable argument (``@hosts(iterable)``) to be used
        instead of requiring ``@hosts(*iterable)``.
    """
    def attach_hosts(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            return func(*args, **kwargs)
        _hosts = host_list
        # Allow for single iterable argument as well as *args
        if len(_hosts) == 1 and not isinstance(_hosts[0], StringTypes):
            _hosts = _hosts[0]
        inner_decorator.hosts = list(_hosts)
        return inner_decorator
    return attach_hosts


def roles(*role_list):
    """
    Decorator defining a list of role names, used to look up host lists.

    A role is simply defined as a key in `env` whose value is a list of one or
    more host connection strings. For example, the following will ensure that,
    barring an override on the command line, ``my_func`` will be executed
    against the hosts listed in the ``webserver`` and ``dbserver`` roles::

        env.roledefs.update({
            'webserver': ['www1', 'www2'],
            'dbserver': ['db1']
        })

        @roles('webserver', 'dbserver')
        def my_func():
            pass

    As with `~fabric.decorators.hosts`, `~fabric.decorators.roles` may be
    invoked with either an argument list or a single, iterable argument.
    Similarly, this decorator uses the same mechanism as
    `~fabric.decorators.hosts` and simply sets ``<function>.roles``.

    .. versionchanged:: 0.9.2
        Allow a single, iterable argument to be used (same as
        `~fabric.decorators.hosts`).
    """
    def attach_roles(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            return func(*args, **kwargs)
        _roles = role_list
        # Allow for single iterable argument as well as *args
        if len(_roles) == 1 and not isinstance(_roles[0], StringTypes):
            _roles = _roles[0]
        inner_decorator.roles = list(_roles)
        return inner_decorator
    return attach_roles


def runs_once(func):
    """
    Decorator preventing wrapped function from running more than once.

    By keeping internal state, this decorator allows you to mark a function
    such that it will only run once per Python interpreter session, which in
    typical use means "once per invocation of the ``fab`` program".

    Any function wrapped with this decorator will silently fail to execute the
    2nd, 3rd, ..., Nth time it is called, and will return the value of the
    original run.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        if not hasattr(decorated, 'return_value'):
            decorated.return_value = func(*args, **kwargs)
        return decorated.return_value
    return decorated


def runs_on_remote(is_local=False, remote_fabfile_path=None, *args, **kwargs):
    """
    Decorator that runs a function on a remote machine which has a copy of your
    fabfile.
    
    Given the following fabfile:
from fabric.api import *

env.hosts = []

def remote():
    env.hosts = ['your_host']

@runs_on_remote(remote_fabfile_path='/path/to/fabfile/dir/')
def foo():
    print local('ls /')

    If you run `fab remote foo` on your local machine, fabric will run `fab foo`
    on your remote machine.
    
    This functionality is useful for when you need to use Python's os and os.path
    libraries on your remote machine, or if you need to import a Django settings.py
    file on your remote machine.
    """
    def decorator(func):
        @wraps(func)
        def inner_decorator(*args, **kwargs):
            is_loc = is_local
            path = remote_fabfile_path
            
            #if fab function is being executed locally, proceed with execution
            if len(env.hosts) == 0 or is_loc:
                return func(*args, **kwargs)
            #else, execute this fab function remotely using the remote machine copy of the fabfile
            else:
                cmd = 'fab %s' % func.__name__
                #pdb.set_trace()
                
                if path is None:
                    path = os.getcwd()
                
                with cd(path):
                    ret = run(cmd)
                #pdb.set_trace()
                return ret
        
        return inner_decorator
    return decorator
