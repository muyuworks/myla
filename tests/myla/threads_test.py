import unittest

from myla import threads, persistence


class TestUsers(unittest.TestCase):

    def setUp(self) -> None:
        self.db = persistence.Persistence(database_url="sqlite://")
        self.db.initialize_database()
        self.session = self.db.create_session()

    def tearDown(self) -> None:
        self.session.close()

    def test_create(self):
        t_created = threads.create(thread=threads.ThreadCreate(metadata={'k': 'v'}), session=self.session)
        self.assertIsInstance(t_created, threads.ThreadRead)
        self.assertEqual(t_created.metadata, {'k': 'v'})
        
        t_read = threads.get(id=t_created.id, session=self.session)
        self.assertEqual(t_read.metadata, t_created.metadata)