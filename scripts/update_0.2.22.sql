ALTER TABLE thread ADD tag TEXT;
CREATE INDEX ix_thread_tag ON thread (tag);

ALTER TABLE message ADD tag TEXT;
CREATE INDEX ix_message_tag ON thread (tag);

ALTER TABLE assistant ADD tag TEXT;
CREATE INDEX ix_assistant_tag ON thread (tag);

ALTER TABLE file ADD tag TEXT;
CREATE INDEX ix_file_tag ON thread (tag);

ALTER TABLE organization ADD tag TEXT;
CREATE INDEX ix_organization_tag ON thread (tag);

ALTER TABLE run ADD tag TEXT;
CREATE INDEX ix_run_tag ON thread (tag);

ALTER TABLE secretkey ADD tag TEXT;
CREATE INDEX ix_secretkey_tag ON thread (tag);

ALTER TABLE user ADD tag TEXT;
CREATE INDEX ix_user_tag ON thread (tag);
