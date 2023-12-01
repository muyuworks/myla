import unittest

from myla import files, persistence, utils


class TestFiles(unittest.TestCase):

    def setUp(self) -> None:
        self.db = persistence.Persistence(database_url="sqlite://")
        self.db.initialize_database()
        self.session = self.db.create_session()

    def tearDown(self) -> None:
        self.session.close()

    def test_file_create(self):
        id = utils.random_id()
        file = files.FileUpload(purpose="assistant", metadata={"k1": "v1", "k2": "v2"})
        file_created = files.create(id=id, file=file, filename="filename", bytes=0, session=self.session)

        self.assertEqual(id, file_created.id)
        self.assertEqual("assistant", file_created.purpose)
        self.assertEqual({"k1": "v1", "k2": "v2"}, file_created.metadata)

        file_read = files.get(id=id, session=self.session)
        self.assertEqual(id, file_read.id)
        self.assertEqual("assistant", file_read.purpose)
        self.assertEqual({"k1": "v1", "k2": "v2"}, file_read.metadata)

        status = files.delete(id=id, session=self.session)
        self.assertEqual(id, status.id)
        self.assertEqual("file.deleted", status.object)
        self.assertEqual(True, status.deleted)

        file_read = files.get(id=id, session=self.session)
        self.assertIsNone(file_read)
