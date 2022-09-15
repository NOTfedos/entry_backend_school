---------------------------------------------------------------------
DROP SCHEMA IF EXISTS "files" CASCADE;
CREATE SCHEMA "files";
CREATE TYPE "files"."system_item_type" AS ENUM ('FILE', 'FOLDER');


CREATE TABLE IF NOT EXISTS "files"."system_item"(
     "id"             VARCHAR(256) NOT NULL
    ,"parent_id"      VARCHAR(256) REFERENCES "files"."system_item" ("id") ON DELETE CASCADE
    ,"size"           INTEGER NOT NULL
    ,"date"           TIMESTAMP WITH TIME ZONE NOT NULL
    ,"itemtype"       "files"."system_item_type"
    ,"url"            VARCHAR(256)
    ,PRIMARY KEY ("id")
);

CREATE SEQUENCE "files"."system_item_history_id_seq" INCREMENT 1 START 1;
CREATE TABLE IF NOT EXISTS "files"."system_item_history"(
     "id"             INTEGER NOT NULL DEFAULT nextval('files.system_item_history_id_seq'::REGCLASS)
    ,"item_id"        VARCHAR(256) NOT NULL REFERENCES "files"."system_item" ("id") ON DELETE CASCADE
    ,"parent_id"      VARCHAR(256) REFERENCES "files"."system_item" ("id") ON DELETE CASCADE
    ,"size"           INTEGER NOT NULL
    ,"date"           TIMESTAMP WITH TIME ZONE NOT NULL
    ,"itemtype"       "files"."system_item_type"
    ,"url"            VARCHAR(256)
    ,PRIMARY KEY ("id")
);
ALTER SEQUENCE "files"."system_item_history_id_seq" OWNED BY "files"."system_item_history"."id";