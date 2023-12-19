import os
import shutil
import unittest
from myla.vectorstores.faiss_group import FAISSGroup
from myla.utils import random_id, sha256

here = os.path.abspath(os.path.dirname(__file__))


class FAISSGroupTests(unittest.TestCase):
    def setUp(self) -> None:
        self._vectors = [
            [0, 0],
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4]
        ]

        self._records = [
            {
                'id': 0,
                'gid': 'g0',
            },
            {
                'id': 1,
                'gid': 'g0',
            },
            {
                'id': 2,
                'gid': 'g2',
            },
            {
                'id': 3,
                'gid': 'g3',
            },
            {
                'id': 4,
            }
        ]

        self._data = os.path.abspath(os.path.join(here, os.pardir, os.pardir, 'data', random_id()))

    def tearDown(self) -> None:
        if os.path.exists(self._data):
            shutil.rmtree(self._data)
            pass

    def test_create_collection(self):
        vs = FAISSGroup(path=self._data)
        vs.create_collection(collection='col')

    def test_add(self):
        vs = FAISSGroup(path=self._data)
        vs.create_collection(collection='col')

        vs.add(collection='col', records=self._records, vectors=self._vectors, group_by='gid')
        self.assertIsNotNone(vs._data.get('col'))
        self.assertEqual(vs._data.get('col'), self._records)
        self.assertIsNotNone(vs._indexes.get('col'))
        self.assertIsNotNone(vs._ids.get('col'))

        self.assertEqual(len(vs._indexes.get('col')), 4)
        self.assertEqual(len(vs._ids.get('col')), 4)

        self.assertEqual(vs._indexes.get('col').keys(), vs._ids.get('col').keys())

        gids = list(vs._indexes.get('col').keys())
        gids.sort()
        gids_1 = []
        for r in self._records:
            gids_1.append(sha256(r.get('gid', '').encode()).hex())
        gids_1 = list(set(gids_1))
        gids_1.sort()

        self.assertEqual(gids, gids_1)

        self.assertEqual(vs._ids.get('col')[vs._group_id("")], [4])
        self.assertEqual(vs._ids.get('col')[vs._group_id("g0")], [0, 1])
        self.assertEqual(vs._ids.get('col')[vs._group_id("g2")], [2])
        self.assertEqual(vs._ids.get('col')[vs._group_id("g3")], [3])

        vs.add(collection='col', records=[{'gid': 'g2'}, {'gid': 'g3', 'id': 6}], vectors=[[5, 5], [6, 6]], group_by='gid')
        self.assertEqual(vs._ids.get('col')[vs._group_id("g2")], [2, 5])
        self.assertEqual(vs._ids.get('col')[vs._group_id("g3")], [3, 6])

        self.assertEqual(vs._data.get('col')[6]['id'], 6)

    def test_load(self):
        vs = FAISSGroup(path=self._data)
        vs.create_collection(collection='col')

        vs.add(collection='col', records=self._records, vectors=self._vectors, group_by='gid')

        vs._unload(collection='col')
        self.assertIsNone(vs._data.get('col'))

        vs._load(collection='col')
        self.assertIsNotNone(vs._data.get('col'))
        self.assertEqual(vs._data.get('col'), self._records)

    def test_search(self):
        vs = FAISSGroup(path=self._data)
        vs.create_collection(collection='col')

        vs.add(collection='col', records=self._records, vectors=self._vectors, group_by='gid')

        records = vs.search(collection='col', vector=self._vectors[0], group_ids=['g0'])
        self.assertEqual(records[0]['id'], 0)
        self.assertEqual(records[0]['_distance'], 0.0)

        records = vs.search(collection='col', vector=self._vectors[1], group_ids=['g0'])
        self.assertEqual(records[0]['id'], 1)
        self.assertEqual(records[0]['_distance'], 0.0)

        records = vs.search(collection='col', vector=self._vectors[0], group_ids=['g2'])
        self.assertEqual(records[0]['id'], 2)
        self.assertGreaterEqual(records[0]['_distance'], 0.5)

        records = vs.search(collection='col', vector=self._vectors[0], group_ids=None)
        self.assertEqual(records[0]['id'], 4)
        self.assertGreaterEqual(records[0]['_distance'], 0.5)

        records = vs.search(collection='col', vector=self._vectors[1], group_ids=['g0', 'g2', 'g0', None])
        self.assertEqual(records[0]['id'], 1)
        self.assertEqual(records[0]['_distance'], 0.0)

    def test_group_id(self):
        vs = FAISSGroup(path=self._data)
        print(vs._group_id())