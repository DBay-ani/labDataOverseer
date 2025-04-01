
---- TODO: consider including (in future iterations) information about whether the endpoint 
----     is capable of sending, capable of receiving, or both.... eh...
CREATE TABLE IF NOT EXISTS ContactorsTable (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT Default "Contactor with Unspecified Name" NOT NULL, 
    contactInfo TEXT NOT NULL,
    notifyAboutGeneralMaintenceAndInfo INTEGER NOT NULL,
    notifyWhenAdditions INTEGER NOT NULL,
    notifyWhenProblem INTEGER NOT NULL,
    endpointType TEXT NOT NULL,
    CHECK( endpointType in ('email', 'file_directory') ), 
    CHECK(length(name) > 0),
    CHECK(length(contactInfo) > 0),
    CHECK( notifyAboutGeneralMaintenceAndInfo in (0, 1)),
    CHECK( notifyWhenAdditions in (0, 1)),
    CHECK( notifyWhenProblem in (0, 1)),
    UNIQUE( name, contactInfo, endpointType)
);


