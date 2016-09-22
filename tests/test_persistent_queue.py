import os
import unittest
import uuid

from persistent_queue import PersistentQueue


class TestPersistentQueue(unittest.TestCase):
    def setUp(self):
        random = str(uuid.uuid4()).replace('-', '')
        self.filename = '{}_{}'.format(self.id(), random)
        self.queue = PersistentQueue(self.filename)

        self.persist_filename = ''

    def tearDown(self):
        os.remove(self.filename)

    def test_count(self):

        self.assertEqual(len(self.queue), 0)
        self.assertEqual(self.queue.count(), 0)

        self.queue.push(1)
        self.assertEqual(len(self.queue), 1)
        self.assertEqual(self.queue.count(), 1)

        self.queue.push(2)
        self.assertEqual(len(self.queue), 2)
        self.assertEqual(self.queue.count(), 2)

        for i in range(100 + 1):
            self.queue.push(i)

        self.assertEqual(len(self.queue), 103)
        self.assertEqual(self.queue.count(), 103)

    def test_clear(self):
        self.queue.push(5)
        self.queue.push(50)

        self.assertEqual(self.queue.peek(2), [5, 50])
        self.assertEqual(len(self.queue), 2)
        self.queue.clear()
        self.assertEqual(len(self.queue), 0)

    def test_push(self):
        self.queue.push(5)
        self.assertEqual(self.queue.peek(1), 5)

        self.queue.push([10, 15, 20])
        self.assertEqual(self.queue.peek(4), [5, 10, 15, 20])

        data = {"a": 1, "b": 2, "c": [1, 2, 3]}
        self.queue.push(data)
        self.assertEqual(self.queue.peek(5), [5, 10, 15, 20, data])

        self.queue.push([])
        self.assertEqual(self.queue.peek(5), [5, 10, 15, 20, data])

    def test_pop(self):
        self.queue.push('a')
        self.queue.push('b')
        self.assertEqual(len(self.queue), 2)

        self.assertEqual(self.queue.pop(), 'a')
        self.assertEqual(len(self.queue), 1)

        self.assertEqual(self.queue.pop(1), 'b')
        self.assertEqual(len(self.queue), 0)

        self.queue.push('a')
        self.queue.push('b')
        self.queue.push('c')
        self.queue.push('d')
        self.assertEqual(len(self.queue), 4)

        self.assertEqual(self.queue.pop(3), ['a', 'b', 'c'])
        self.assertEqual(len(self.queue), 1)

        self.assertEqual(self.queue.pop(100), ['d'])
        self.assertEqual(len(self.queue), 0)

        self.assertEqual(self.queue.pop(100), [])
        self.assertEqual(self.queue.pop(), None)

        self.queue.push('d')
        self.assertEqual(self.queue.pop(0), [])
        self.assertEqual(len(self.queue), 1)

    def test_peek(self):
        self.queue.push(1)
        self.queue.push(2)
        self.queue.push("test")

        self.assertEqual(self.queue.peek(), 1)
        self.assertEqual(self.queue.peek(1), 1)
        self.assertEqual(self.queue.peek(2), [1, 2])
        self.assertEqual(self.queue.peek(3), [1, 2, "test"])

        self.assertEqual(self.queue.peek(100), [1, 2, "test"])

        self.queue.clear()

        self.queue.push(1)
        self.assertEqual(len(self.queue), 1)
        self.assertEqual(self.queue.peek(), 1)
        self.assertEqual(self.queue.peek(1), 1)
        self.assertEqual(self.queue.peek(2), [1])

        self.assertEqual(self.queue.peek(0), [])

    def test_big_file_part_1(self):
        data = {"a": list(range(1000))}

        for i in range(2000):
            self.queue.push(data)

        self.assertEqual(len(self.queue), 2000)

        for i in range(1995):
            self.assertEqual(self.queue.pop(), data)
            self.queue.flush()

        self.assertEqual(len(self.queue), 5)

    def test_big_file_part_2(self):
        data = {"a": list(range(1000))}

        for i in range(2000):
            self.queue.push(data)

        self.assertEqual(self.queue.pop(1995), [data for i in range(1995)])
        self.assertEqual(len(self.queue), 5)

    def test_copy(self):
        new_queue_name = 'another_queue'
        self.queue.push([5, 4, 3, 2, 1])
        self.assertEqual(len(self.queue), 5)
        self.assertEqual(self.queue.pop(), 5)

        new_queue = self.queue.copy(new_queue_name)

        self.assertEqual(len(self.queue), len(new_queue))
        self.assertEqual(self.queue.pop(), new_queue.pop())
        self.assertEqual(self.queue.pop(), new_queue.pop())
        self.assertEqual(self.queue.pop(), new_queue.pop())
        self.assertEqual(self.queue.pop(), new_queue.pop())

        os.remove(new_queue_name)

    def test_usage(self):
        self.queue.push(1)
        self.queue.push(2)
        self.queue.push(3)
        self.queue.push(['a', 'b', 'c'])

        self.assertEqual(self.queue.peek(), 1)
        self.assertEqual(self.queue.peek(4), [1, 2, 3, 'a'])
        self.assertEqual(len(self.queue), 6)

        self.queue.push('foobar')

        self.assertEqual(self.queue.pop(), 1)
        self.assertEqual(len(self.queue), 6)
        self.assertEqual(self.queue.pop(6), [2, 3, 'a', 'b', 'c', 'foobar'])

    def test_delete(self):
        self.queue.push(2)
        self.queue.push(3)
        self.queue.push(7)
        self.queue.push(11)
        self.assertEqual(len(self.queue), 4)

        self.queue.delete(2)
        self.assertEqual(len(self.queue), 2)
        self.assertEqual(self.queue.peek(2), [7, 11])
        self.assertEqual(self.queue.pop(2), [7, 11])

        self.queue.push(2)
        self.queue.delete(1000)
        self.assertEqual(len(self.queue), 0)

        self.queue.push(2)
        self.queue.delete(0)
        self.assertEqual(len(self.queue), 1)

class TestPersistentQueueWithNoAutoFlush(TestPersistentQueue):
    def setUp(self):
        random = str(uuid.uuid4()).replace('-', '')
        self.filename = '{}_{}'.format(self.id(), random)
        self.queue = PersistentQueue(self.filename, auto_flush=False)

        self.persist_filename = ''

class TestPersistentQueueWithDill(TestPersistentQueue):
    def setUp(self):
        import dill

        random = str(uuid.uuid4()).replace('-', '')
        self.filename = '{}_{}'.format(self.id(), random)
        self.queue = PersistentQueue(self.filename, loads=dill.loads,
                                     dumps=dill.dumps)

        self.persist_filename = ''

class TestPersistentQueueWithBson(unittest.TestCase):
    def setUp(self):
        import bson

        random = str(uuid.uuid4()).replace('-', '')
        self.filename = '{}_{}'.format(self.id(), random)
        self.queue = PersistentQueue(self.filename, loads=bson.loads,
                                     dumps=bson.dumps)

        self.persist_filename = ''

    def tearDown(self):
        os.remove(self.filename)

    def test_big_file_part_1(self):
        data = {"a": list(range(1000))}

        for i in range(2000):
            self.queue.push(data)

        self.assertEqual(len(self.queue), 2000)

        for i in range(1995):
            self.assertEqual(self.queue.pop(), data)
            self.queue.flush()

        self.assertEqual(len(self.queue), 5)

    def test_big_file_part_2(self):
        data = {"a": list(range(1000))}

        for i in range(2000):
            self.queue.push(data)

        self.assertEqual(self.queue.pop(1995), [data for i in range(1995)])
        self.assertEqual(len(self.queue), 5)


if __name__ == '__main__':
    unittest.main()
