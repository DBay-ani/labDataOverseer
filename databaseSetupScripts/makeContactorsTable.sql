

CREATE TABLE IF NOT EXISTS EntProperties( --- ... ripe for abuse if not careful
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    CHECK( length(name) > 0 ) --- could also check that it contains non-whitespace characters.
)
INSERT OR FAIL -- NOTE: Fail, unlike Abort, does not rollback changes on error.
INTO EntityProperties ( name)
VALUES ("INTERNAL");





CREATE TABLE IF NOT EXISTS EntityTable(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT Default "Entity with Unspecified Name" NOT NULL,
    ); -- Note that I'm not enforcing unique names.
INSERT OR FAIL -- NOTE: Fail, unlike Abort, does not rollback changes on error.
INTO EntityTable (name)
VALUES
("SELF");


CREATE TABLE IF NOT EXISTS ContactorsTable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT Default "Contactor with Unspecified Name" NOT NULL, 
    contactInfo TEXT NOT NULL,
    notifyAboutGeneralMaintenceAndInfo INTEGER NOT NULL,
    notifyWhenAdditions INTEGER NOT NULL,
    notifyWhenProblem INTEGER NOT NULL, 
    CHECK(length(name) > 0),
    CHECK(length(contactInfo) > 0),
    CHECK( notifyAboutGeneralMaintenceAndInfo in (0, 1)),
    CHECK( notifyWhenAdditions in (0, 1)),
    CHECK( notifyWhenProblem in (0, 1))
);


