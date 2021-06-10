"""
named threading locks
=====================

named locks are used in multi-threaded applications and based on the Python threading lock classes
:class:`threading.Lock` and :class:`threading.RLock`. the advantage of the named locks in contrary to Python threading
locks is that a lock don't need to create and store a reference of a Python threading lock object - the
:class:`NamedLocks` does this automatically for your application and does keep track of all the named locks of your
application in its class variables.

so a named lock get exclusively identified only by an unique string. and to create other blocking locks you only need a
reference to the :class:`NamedLocks` class.

named locks are very useful e.g. if you want to lock a certain record of database table. for this you simply create a
new instance of the :class:`NamedLocks` class and as unique string you can use the table name followed by the primary
key of the record to lock::

    named_lock = NamedLocks()
    if named_lock.acquire(table_name + primary_key)

        ...     # locked database transaction code goes here

        named_lock.release(table_name + primary_key)

if now any other process of your application want to lock the same record (same table name and primary key) then it will
be blocked until the process that acquired this named lock first is releasing the table record lock.

alternatively and especially if your application want to create multiple named locks you can use the class
:class:`NamedLocks` as a context manager, passing all the named lock strings to the constructor::

    with NamedLocks(table_name1 + primary_key1, table_name2 + primary_key2, ...):
        ...     # locked database transaction

"""
import threading
from typing import ClassVar, Dict, Type, Union

# noinspection PyProtectedMember
from ae.core import main_app_instance, _LOGGER, po      # type: ignore   # mypy

__version__ = '0.2.8'


class NamedLocks:
    """ manage all named locks of your application.

    migrated from https://stackoverflow.com/users/355230/martineau answer in stackoverflow on the question
    https://stackoverflow.com/questions/37624289/value-based-thread-lock.

    .. note::
        currently the sys_lock feature is not implemented. use either ae.lockfile or the github extension portalocker
        (see https://github.com/WoLpH/portalocker) or the encapsulating extension ilock
        (https://github.com/symonsoft/ilock). more on system wide named locking:
        https://stackoverflow.com/questions/6931342/system-wide-mutex-in-python-on-linux.

    """
    locks_change_lock: ClassVar[threading.Lock] = threading.Lock()
    """ threading lock class variable used to change status of all NamedLock instances """
    active_locks: ClassVar[Dict[str, Union[threading.Lock, threading.RLock]]] = dict()
    """ class variable keeping a dictionary of all active RLock/Lock instances """
    active_lock_counters: ClassVar[Dict[str, int]] = dict()         #: lock counters class variable for reentrant locks

    def __init__(self, *lock_names: str, reentrant_locks: bool = True, sys_lock: bool = False):
        """ prepare new named lock(s).

        :param lock_names:          unique lock strings to be prepared to be locked by :meth:`.__enter__`.
        :param reentrant_locks:     pass False to use non-reentrant locks (True=reentrant locks).
        :param sys_lock:            pass True to prepare system lock (works for several independent applications).
                                    CURRENTLY NOT IMPLEMENTED.
        """
        assert not sys_lock, "sys_lock is currently not implemented"

        self._lock_names = lock_names       #: tuple of lock names
        self._lock_class: Type[Union[threading.Lock, threading.RLock]] = \
            threading.RLock if reentrant_locks else threading.Lock
        """ used threading lock class """
        self._sys_lock = sys_lock           #: True if lock will be system-wide (not only application-wide)
        # map class intern dpo method to cae.dpo() or to global dpo (referencing the module method dpo())
        cae = main_app_instance()
        self._print_func = cae.dpo if cae and getattr(cae, 'startup_end', False) else po
        """ print function used to show debug and error messages """

        self.dpo("NamedLocks.__init__", lock_names)

    def __enter__(self):
        """ locking context enter method. """
        self.dpo("NamedLocks.__enter__")
        for lock_name in self._lock_names:
            self.dpo("NamedLocks.__enter__ b4 acquire ", lock_name)
            self.acquire(lock_name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ locking context exit method. """
        self.dpo("NamedLocks __exit__", exc_type, exc_val, exc_tb)
        for lock_name in self._lock_names:
            self.dpo("NamedLocks.__exit__ b4 release ", lock_name)
            self.release(lock_name)

    def dpo(self, *args, **kwargs):
        """ print function which is suppressing printout if debug level is too low. """
        if 'logger' not in kwargs:
            kwargs['logger'] = _LOGGER
        return self._print_func(*args, **kwargs)

    def acquire(self, lock_name: str, *args, **kwargs) -> bool:
        """ acquire the named lock specified by the `lock_name` argument.

        :param lock_name:       name of the lock to acquire.
        :param args:            passed to the acquire method of the underlying :class:`~threading.RLock` respectively
                                :class:`~threading.Lock` class instance.
        :param kwargs:          passed to the acquire method of the underlying :class:`~threading.RLock` or
                                :class:`~threading.Lock` class instance.
        :return:                True if named lock got acquired successfully, else False.
        """
        self.dpo("NamedLocks.acquire", lock_name, 'START')

        while True:     # break at the end - needed to retry after conflicted add/del of same lock name in threads
            with NamedLocks.locks_change_lock:
                lock_exists = lock_name in NamedLocks.active_locks
                lock_instance = NamedLocks.active_locks[lock_name] if lock_exists else self._lock_class()

            # request the lock - out of locks_change_lock context, to not block other instances of this class
            lock_acquired = lock_instance.acquire(*args, **kwargs)

            if lock_acquired:
                with NamedLocks.locks_change_lock:
                    if lock_exists != (lock_name in NamedLocks.active_locks):  # redo/retry if lock state has changed
                        self.dpo("NamedLocks.acquire", lock_name, 'RETRY')
                        lock_instance.release()
                        continue
                    if lock_exists:
                        NamedLocks.active_lock_counters[lock_name] += 1
                    else:
                        NamedLocks.active_locks[lock_name] = lock_instance
                        NamedLocks.active_lock_counters[lock_name] = 1
            break

        self.dpo("NamedLocks.acquire", lock_name, 'END')

        return lock_acquired

    def release(self, lock_name: str):
        """ release the named lock specified by the `lock_name` argument.

        :param lock_name:       name of the lock to release.
        """
        self.dpo("NamedLocks.release", lock_name, 'START')

        with NamedLocks.locks_change_lock:
            if lock_name not in NamedLocks.active_lock_counters or lock_name not in NamedLocks.active_locks:
                self.dpo("NamedLocks.release", lock_name, 'IDX-ERR')
                return

            if NamedLocks.active_lock_counters[lock_name] == 1:
                NamedLocks.active_lock_counters.pop(lock_name)
                lock = NamedLocks.active_locks.pop(lock_name)
            else:
                NamedLocks.active_lock_counters[lock_name] -= 1
                lock = NamedLocks.active_locks[lock_name]

        lock.release()

        self.dpo("NamedLocks.release", lock_name, 'END')
