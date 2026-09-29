""" unit tests for the ae_lockname portion """
import time
import threading
from ae.lockname import NamedLocks


class TestNamedLocks:
    def test_init(self):
        nl = NamedLocks()
        assert len(nl.active_lock_counters) == 0
        assert nl

    def test_sequential(self):
        nl = NamedLocks()
        nl2 = NamedLocks()
        assert len(nl2.active_lock_counters) == 0

        assert nl.acquire('test', timeout=0.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1
        assert len(nl2.active_lock_counters) == 1 and nl2.active_lock_counters['test'] == 1

        nl.release('test')
        assert len(nl.active_lock_counters) == 0
        assert len(nl2.active_lock_counters) == 0

        assert nl2.acquire('test', timeout=.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1
        assert len(nl2.active_lock_counters) == 1 and nl2.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl.active_lock_counters) == 0
        assert len(nl2.active_lock_counters) == 0

    def test_locking_with_timeout(self):
        nl = NamedLocks(reentrant_locks=False)
        assert nl.acquire('test', timeout=0.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2 = NamedLocks(reentrant_locks=False)
        assert not nl2.acquire('test', timeout=.01)
        assert len(nl2.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl.release('test')
        assert len(nl2.active_lock_counters) == 0
        assert nl2.acquire('test', timeout=.01)
        assert len(nl2.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl2.active_lock_counters) == 0

    def test_reentrant_locking_with_timeout(self):
        nl = NamedLocks()
        assert nl.acquire('test', timeout=0.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2 = NamedLocks()
        assert nl2.acquire('test', timeout=.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 2

        nl.release('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl2.active_lock_counters) == 0

        assert nl2.acquire('test', timeout=.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl.active_lock_counters) == 0

    def test_non_blocking_args(self):
        nl = NamedLocks(reentrant_locks=False)
        assert nl.acquire('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2 = NamedLocks(reentrant_locks=False)
        assert nl2.acquire('otherTest')
        assert len(nl.active_lock_counters) == 2 and nl.active_lock_counters['test'] == 1 \
            and nl.active_lock_counters['otherTest'] == 1

        nl2.release('otherTest')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        assert not nl2.acquire('test', blocking=False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        assert not nl2.acquire('test', False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        assert not nl2.acquire('test', timeout=.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl.release('test')
        assert len(nl2.active_lock_counters) == 0

        assert nl2.acquire('test', blocking=False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl2.active_lock_counters) == 0

    def test_reentrant_non_blocking_args(self):
        nl = NamedLocks()
        assert nl.acquire('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2 = NamedLocks()
        assert nl2.acquire('otherTest')
        assert len(nl.active_lock_counters) == 2 and nl.active_lock_counters['test'] == 1 \
            and nl.active_lock_counters['otherTest'] == 1
        nl2.release('otherTest')

        assert nl2.acquire('test', blocking=False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 2

        assert nl2.acquire('test', False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 3

        assert nl2.acquire('test', timeout=.01)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 4

        nl.release('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 3

        nl.release('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 2

        nl.release('test')
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl.release('test')
        assert len(nl2.active_lock_counters) == 0

        assert nl2.acquire('test', blocking=False)
        assert len(nl.active_lock_counters) == 1 and nl.active_lock_counters['test'] == 1

        nl2.release('test')
        assert len(nl2.active_lock_counters) == 0

    def test_with_context_with(self):
        with NamedLocks('tst_lock_id') as nl:
            assert 'tst_lock_id' in nl.active_locks

    def test_error_context(self):
        with NamedLocks('test2') as nl:
            assert 'test2' in nl.active_locks
            nl.release('test2')
            assert 'test2' not in nl.active_locks
        assert 'test2' not in nl.active_locks

        with NamedLocks('test3') as nl:
            assert 'test3' in nl.active_locks
            assert nl.active_locks.pop('test3')
            assert 'test3' not in nl.active_locks

    def test_duplicate_acquire(self):
        def thr():
            """ sub thread """
            print('thread start')
            time.sleep(.5)
            print('thread b4 release')
            nl.release('test')  # del nl.active_locks['test']
            print('thread after release')

        with NamedLocks('test', reentrant_locks=False) as nl:
            print('before dup blocking')
            threading.Thread(target=thr).start()
            nl.acquire('test', blocking=True)
            print('after dup blocking')
