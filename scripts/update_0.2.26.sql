ALTER TABLE userorglink ADD "role" VARCHAR;
UPDATE userorglink SET role='owner';

UPDATE organization SET user_id=(SELECT userorglink.user_id FROM userorglink WHERE organization.id=userorglink.org_id);

UPDATE assistant SET org_id=(SELECT userorglink.org_id FROM userorglink WHERE assistant.user_id=userorglink.user_id);
UPDATE thread SET org_id=(SELECT userorglink.org_id FROM userorglink WHERE thread.user_id=userorglink.user_id);
UPDATE message SET org_id=(SELECT userorglink.org_id FROM userorglink WHERE message.user_id=userorglink.user_id);
UPDATE run SET org_id=(SELECT userorglink.org_id FROM userorglink WHERE run.user_id=userorglink.user_id);
UPDATE file SET org_id=(SELECT userorglink.org_id FROM userorglink WHERE file.user_id=userorglink.user_id);