
import sqlite3
import threading
import unittest

from myla import persistence, threads, utils

db_file = "./tests/data/myla-test.db"
stop = False


class TestPersistence(unittest.TestCase):
    def setUp(self) -> None:

        self.db = persistence.Persistence(database_url=f"sqlite:///{db_file}", connect_args={"timeout": 1})
        self.db.initialize_database()
        #with self.db.create_session() as session:
        #    session.exec(text("PRAGMA journal_mode = WAL"))

    def tearDown(self) -> None:
        #if os.path.exists(db_file):
        #    os.remove(db_file)
        #self.session.close()
        pass

    def test_database_lock(self):

        def _read_thread():
            global stop
            session = self.db.create_session()

            while not stop:
                try:
                    tl = threads.list(limit=100, session=session)
                    print(f"list: {len(tl.data)}")
                except Exception as e:
                    #print(f"Read thread error: {e}")
                    stop = True
                    raise e

        def _write_thread():
            global stop
            #db = persistence.Persistence(database_url=f"sqlite:///{db_file}")
            session = self.db.create_session()

            c = 0
            while not stop:
                try:
                    threads.create(thread=threads.ThreadCreate(), session=session)

                    c += 1
                    if c % 1000 == 0:
                        print(f"Create threads: {c} {stop}")
                except Exception as e:
                    stop = True
                    session.rollback()
                    raise e

        def _native_write_thread():
            global stop
            conn = sqlite3.connect(db_file, isolation_level=None)
            #conn = self.db.engine.connect().connection

            c = 0
            while not stop:
                try:
                    conn.execute("INSERT INTO thread (id) VALUES (?)", (utils.random_id(),))

                    c += 1
                    if c % 100 == 0:
                        print(f"Native create threads: {c}")

                    if c == 100000:
                        stop = True
                        print("stop")
                except Exception as e:
                    stop = True
                    raise e

        threading.Thread(target=_write_thread).start()
        threading.Thread(target=_write_thread).start()
        threading.Thread(target=_write_thread).start()
        #threading.Thread(target=_native_write_thread).start()
        threading.Thread(target=_read_thread).start()
        threading.Thread(target=_read_thread).start()
        threading.Thread(target=_read_thread).start()
