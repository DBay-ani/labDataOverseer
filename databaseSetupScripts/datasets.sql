CREATE TABLE IF NOT EXISTS Datasets (
    sessionID INTEGER,
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY, 
    timeStarted INTEGER DEFAULT CURRENT_TIMESTAMP NOT NULL,
    --- The use of the below two fields are a bit over-fitted to our current use, 
    --- but likely they can be refactored out later
    worm_sex TEXT NOT NULL,
    worm_strain TEXT NOT NULL,
    misc BLOB, 
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID),
    CHECK(worm_sex in ("h", "m")),
    CHECK(length(worm_strain) > 0)
    );
CREATE TEMP TRIGGER AddSessionInfo_Datasets
AFTER INSERT ON Datasets
FOR EACH ROW 
BEGIN
    UPDATE Datasets SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;


CREATE TABLE IF NOT EXISTS DataContentType (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sessionID INTEGER,
    name TEXT  UNIQUE NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY,
    misc BLOB,
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
CREATE TEMP TRIGGER AddSessionInfo_DataContentType
AFTER INSERT ON DataContentType
FOR EACH ROW 
BEGIN
    UPDATE DataContentType SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
END;
INSERT OR IGNORE INTO DataContentType (ID, name, misc) 
VALUES
    ( 0, 'OFP', 'orange fluorescent protein'),
    ( 1, 'BFP', 'blue fluorescent protein'),
    ( 2, 'google_sheet', 'The Google sheet that the data collector/experimenter used to record the conditions collected.'),
    ( 3, 'mNeptune', NULL),
    ( 4, 'freely_moving', 'The confocal data collected for the freely moving worm... etc.'),
    ( 5, 'all_red', NULL), 
    ( 6, 'NIR', 'Near Infrared recording of the E Elegans worm while freely moving.');

CREATE TABLE IF NOT EXISTS DatasetContent (
    sessionID INTEGER,
    rowID INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT  NOT NULL, --- SQLite3 seems to restrict to one primary key... ---- PRIMARY KEY, -- file path or URL.... NOTE: might have to relax the unique contraint for Google sheets...
    timeAdded INTEGER DEFAULT CURRENT_TIMESTAMP NOT NULL,
    datasetMemberOf INTEGER NOT NULL, 
    dataRecordType INTEGER NOT NULL, 
    misc TEXT, 
    FOREIGN KEY( datasetMemberOf ) REFERENCES Datasets(ID)
    FOREIGN KEY( dataRecordType ) REFERENCES DataContentType(ID)
    FOREIGN KEY( sessionID ) REFERENCES Sessions(ID)
    );
---- NOTE(c7eac8f1-432b-4260-9060-c90d91019153): Below is prohibited by SQLite syntax (see, for instance, 
---- https://stackoverflow.com/questions/59086591/how-to-create-partial-index-on-table-with-where-clause-in-sqlite/59089132#59089132 )
---- so, while there may be better ways to do this, for now we get around the issue by manually assigning an 
---- ID to the 'google_sheet' type above and manually specify that index here...
---- ---- Below, we use unique index to check  that certain values are unique while other we allow
---- ---- not to be.
---- CREATE UNIQUE INDEX IF NOT EXISTS UniqueIndexOn_DatasetContent
---- ON DatasetContent (location)
---- WHERE dataRecordType NOT IN (SELECT * FROM DataContentType AS B WHERE B.name='google_sheet' AND B.ID);
CREATE UNIQUE INDEX IF NOT EXISTS UniqueIndexOn_DatasetContent
ON DatasetContent (location)
WHERE dataRecordType != 2;
CREATE TEMP TRIGGER AddSessionInfo_DatasetContent
AFTER INSERT ON Datasets
FOR EACH ROW 
BEGIN
    UPDATE DatasetContent SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE rowID=new.rowID;
END;

CREATE VIEW IF NOT EXISTS DatasetAndMostRecentIndividualFiles(
    dataset_id,
    dataset_name,
    dataContentTypeName,
    location
    )
AS SELECT 
    A1.ID,
    A1.name,
    B1.name,
    C1.location
FROM
    Datasets AS A1,
    DataContentType AS B1,
    DatasetContent as C1
WHERE
    C1.dataRecordType=B1.ID AND
    C1.datasetMemberOf = A1.ID
GROUP BY 
    A1.ID,
    B1.ID
HAVING
    C1.timeAdded = max(C1.timeAdded);


CREATE VIEW IF NOT EXISTS DatasetAndMostRecentFiles (
    dataset_id,
    dataset_name,
    worm_sex,
    worm_strain,
    OFP,
    BFP,
    google_sheet,
    mNeptune,
    freely_moving,
    NIR,
    all_red
    )
AS SELECT 
    A1.ID,
    A1.name,
    A1.worm_sex,
    A1.worm_strain,
    B1.location,
    B2.location,
    B3.location,
    B4.location,
    B5.location,
    B6.location,
    B7.location
FROM
    Datasets AS A1,
    DatasetAndMostRecentIndividualFiles AS B1,
    DatasetAndMostRecentIndividualFiles AS B2,
    DatasetAndMostRecentIndividualFiles AS B3,
    DatasetAndMostRecentIndividualFiles AS B4,
    DatasetAndMostRecentIndividualFiles AS B5,
    DatasetAndMostRecentIndividualFiles AS B6,
    DatasetAndMostRecentIndividualFiles AS B7
WHERE
    B1.dataset_id=A1.ID AND
    B2.dataset_id=A1.ID AND
    B3.dataset_id=A1.ID AND
    B4.dataset_id=A1.ID AND
    B5.dataset_id=A1.ID AND
    B6.dataset_id=A1.ID AND
    B7.dataset_id=A1.ID AND
    B1.dataContentTypeName='OFP' AND
    B2.dataContentTypeName='BFP' AND
    B3.dataContentTypeName='google_sheet' AND
    B4.dataContentTypeName='mNeptune' AND
    B5.dataContentTypeName='freely_moving' AND
    B6.dataContentTypeName='NIR' AND
    B7.dataContentTypeName='all_red';

CREATE TEMP TRIGGER InsertInto_DatasetAndMostRecentFiles
INSTEAD OF INSERT ON DatasetAndMostRecentFiles
FOR EACH ROW 
BEGIN
    INSERT INTO Datasets(ID, name,
        worm_sex, worm_strain)
    VALUES (new.dataset_id, new.dataset_name, new.worm_sex, new.worm_strain);
    INSERT INTO DatasetContent (datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.OFP,
          (SELECT ID from DataContentType WHERE name = 'OFP') );
    INSERT INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.BFP,
          (SELECT ID from DataContentType WHERE name = 'BFP') );
    INSERT INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.google_sheet,
          (SELECT ID from DataContentType WHERE name = 'google_sheet') );
    INSERT INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.mNeptune,
          (SELECT ID from DataContentType WHERE name = 'mNeptune') );
    INSERT INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.freely_moving,
          (SELECT ID from DataContentType WHERE name = 'freely_moving') );
    INSERT INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.NIR,
          (SELECT ID from DataContentType WHERE name = 'NIR') );
    INSERT INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.all_red,
          (SELECT ID from DataContentType WHERE name = 'all_red') );
END;
--- While the Update_DatasetAndMostRecentFiles trigger is very similar to the 
--- InsertInto_DatasetAndMostRecentFiles trigger, it containst insert statements
--- saying "INSERT OR IGNORE", which offers less error-catching than just an insert
--- and helps make sure that values that were the same as something previously were
--- intentionally given. Note that inside the body of the trigger, we use INSERT instead
--- of actual updates on the tables so that we have a record of old values and when they
--- were in effect.
CREATE TEMP TRIGGER Update_DatasetAndMostRecentFiles
INSTEAD OF UPDATE ON DatasetAndMostRecentFiles
FOR EACH ROW 
BEGIN
    UPDATE Datasets SET --- TODO: record the old values someone (other than just relying on the logging and message tables - some proper, machine-readable way that is closely associated with the Dataset table...)
        worm_sex = new.worm_sex, worm_strain=new.worm_strain 
        WHERE ID=new.dataset_id AND name=new.dataset_name;
    --- TODO: instead of using OR IGNORE below which could fail due to constraints
    --- other than the uniqueness of the locations failing, do something more robust
    --- that only actually inserts if the value is new, and not simply inserts when
    --- contraints don't fail. As-is, this leaves constraint violations that should
    --- be reported to the user to be unreported and, at present in the corresponding
    --- python code for "update", reports an untrouble success despite of this.
    INSERT OR IGNORE INTO DatasetContent (datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.OFP,
          (SELECT ID from DataContentType WHERE name = 'OFP') );
    INSERT OR IGNORE INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.BFP,
          (SELECT ID from DataContentType WHERE name = 'BFP') );
    INSERT OR IGNORE INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.google_sheet,
          (SELECT ID from DataContentType WHERE name = 'google_sheet') );
    INSERT OR IGNORE INTO DatasetContent ( datasetMemberOf, location, dataRecordType )
    VALUES
        ( new.dataset_id, 
          new.mNeptune,
          (SELECT ID from DataContentType WHERE name = 'mNeptune') );
    INSERT OR IGNORE INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.freely_moving,
          (SELECT ID from DataContentType WHERE name = 'freely_moving') );
    INSERT OR IGNORE INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.NIR,
          (SELECT ID from DataContentType WHERE name = 'NIR') );
    INSERT OR IGNORE INTO DatasetContent (datasetMemberOf, location, dataRecordType)
    VALUES
        ( new.dataset_id, 
          new.all_red,
          (SELECT ID from DataContentType WHERE name = 'all_red') );
END;
