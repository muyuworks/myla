import unittest

from myla import assistants, persistence


class TestUsers(unittest.TestCase):

    def setUp(self) -> None:
        self.db = persistence.Persistence(database_url="sqlite://")
        self.db.initialize_database()
        self.session = self.db.create_session()

    def tearDown(self) -> None:
        self.session.close()

    def test_create_get_list_assistant(self, user_id=None):
        asst_created = assistants.create(assistant=assistants.AssistantCreate(
            name='name',
            description='desc',
            model='model',
            instructions='instruction',
            tools=[{'type': 'retrieval'}],
            file_ids=['1'],
            metadata={'k': 'v'}
            ), user_id=user_id, session=self.session)
        self.assertIsNotNone(asst_created.id)

        asst_read = assistants.get(id=asst_created.id, user_id=user_id, session=self.session)
        self.assertIsNotNone(asst_read)
        self.assertEqual(asst_created.id, asst_read.id)
        self.assertEqual(asst_read.name, 'name')
        self.assertEqual(asst_read.description, 'desc')
        self.assertEqual(asst_read.instructions, 'instruction')
        self.assertEqual(asst_read.tools, [{'type': 'retrieval'}])
        self.assertEqual(asst_read.file_ids, ['1'])
        self.assertEqual(asst_read.model, 'model')
        self.assertEqual(asst_read.metadata, {'k': 'v'})

        asst_list = assistants.list(user_id=user_id, session=self.session)
        self.assertEqual(len(asst_list.data), 1)
        asst_read = asst_list.data[0]
        self.assertEqual(asst_created.id, asst_read.id)
        self.assertEqual(asst_read.name, 'name')
        self.assertEqual(asst_read.description, 'desc')
        self.assertEqual(asst_read.instructions, 'instruction')
        self.assertEqual(asst_read.tools, [{'type': 'retrieval'}])
        self.assertEqual(asst_read.file_ids, ['1'])
        self.assertEqual(asst_read.model, 'model')
        self.assertEqual(asst_read.metadata, {'k': 'v'})

    def test_create_get_list_assistant_with_user_id(self):
        self.test_create_get_list_assistant(user_id='shellc')
