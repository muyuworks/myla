import unittest

from myla import users, persistence


class TestUsers(unittest.TestCase):

    def setUp(self) -> None:
        self.db = persistence.Persistence(database_url="sqlite://")
        self.db.initialize_database()
        self.session = self.db.create_session()

    def tearDown(self) -> None:
        self.session.close()

    def test_list_sa_users(self):
        sa_users = users.list_sa_users(session=self.session)
        self.assertIsInstance(sa_users, users.UserList)
        self.assertCountEqual(sa_users.data, [])

    def test_create_organization(self):
        org = users.create_organization(users.OrganizationCreate(), session=self.session)
        self.assertIsInstance(org, users.OrganizationRead)
        self.assertIsNotNone(org.id)

        org_read = users.get_organization(id=org.id, session=self.session)
        self.assertEqual(org_read.id, org.id)
        self.assertFalse(org_read.is_primary)

    def test_create_organization_with_metadata(self):
        org = users.create_organization(users.OrganizationCreate(display_name='org', metadata={'k': 'v'}), session=self.session)
        self.assertIsInstance(org, users.OrganizationRead)
        self.assertEqual(org.display_name, 'org')
        self.assertEqual(org.metadata, {'k': 'v'})

    def test_create_organization_without_auto_commit(self):
        org = users.create_organization(users.OrganizationCreate(), session=self.session, auto_commit=False)
        self.assertIsInstance(org, users.OrganizationRead)
        self.assertIsNotNone(org.id)

        org_read = users.get_organization(id=org.id, session=self.db.create_session())
        self.assertIsNone(org_read)

    def test_create_user(self):
        user = users.create_user(user=users.UserCreate(username='shellc', password='shellc'), session=self.session)

        self.assertIsInstance(user, users.UserRead)

        user_read = users.get_user(id=user.id, session=self.session)
        self.assertEqual(user.id, user_read.id)

        user_dbo = users.get_user_dbo(id=user.id, session=self.session)
        self.assertEqual(user_dbo.password, users.generate_password('shellc', user_dbo.salt))

        orgs = users.list_orgs(user_id=user_read.id, session=self.session)
        self.assertIsInstance(orgs, users.OrganizationList)
        self.assertEqual(len(orgs.data), 1)
        self.assertEqual(orgs.data[0].display_name, user.display_name)
        self.assertEqual(orgs.data[0].is_primary, True)
        #self.assertEqual(orgs.data[0].user_id, user.id)

    def test_create_secret_key(self):
        sk = users.create_secret_key(key=users.SecrectKeyCreate(tag='web'), user_id='shellc', session=self.session)
        self.assertIsInstance(sk, users.SecretKeyRead)
        self.assertIsNotNone(sk.id)
        self.assertEqual(sk.tag, 'web')
        self.assertEqual(sk.user_id, 'shellc')

        sk = users.get_secret_key(id=sk.id, session=self.session)
        self.assertIsInstance(sk, users.SecretKeyRead)
        self.assertIsNotNone(sk.id)
        self.assertEqual(sk.tag, 'web')
        self.assertEqual(sk.user_id, 'shellc')

        sks = users.list_secret_keys(user_id='shellc', session=self.session)
        self.assertEqual(len(sks.data), 1)
        sk = sks.data[0]
        self.assertIsInstance(sk, users.SecretKeyRead)
        self.assertIsNotNone(sk.id)
        self.assertEqual(sk.tag, 'web')
        self.assertEqual(sk.user_id, 'shellc')

    def create_default_superadmin(self):
        sa = users.create_default_superadmin(session=self.session)
        self.assertEqual(sa.username, 'admin')

        sa = users.create_default_superadmin(session=self.session)
        self.assertIsNone(sa)
