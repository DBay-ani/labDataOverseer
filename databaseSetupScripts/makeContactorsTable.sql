


CREATE TABLE Contactors (
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



