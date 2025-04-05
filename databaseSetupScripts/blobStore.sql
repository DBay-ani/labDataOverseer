
--- NOTE: this method of listing out content-types could have
---     short-comings, but for out current use-case, at least, its fine etc.
--- Note: in regard to storing blobs on the database (in contrast to the note
---     immediately above which was in regards to content-types/ blob metadata)
---     there are some aspects of that are questionable if we lean too-heavily into that
---     (e.g., storing the actual multi-gigabyte confocal data on the database), but for our
---     present use-case and intended aims, what is here may be reasonable. Related, see:
---         https://www.sqlite.org/mostdeployed.html
---         https://sqlite.org/forum/info/a02a8bc478cee744d8269c7a56c867bdc3706f5b5c099aa1c09f6bf65a9774a3
---         https://www.sqlite.org/whentouse.html
---         https://softwareengineering.stackexchange.com/questions/150669/is-it-a-bad-practice-to-store-large-files-10-mb-in-a-database
---         TOAST (The Other ARchival Storage Technique) and ACID (https://en.wikipedia.org/wiki/ACID) 

CREATE TABLE IF NOT EXISTS BlobContentType(
    ID integer PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE, 
    description TEXT,
    isCompressionFormat INTEGER NOT NULL,
    CHECK(length(name) > 0), --- NOTE, could further check, perhaps with the ~, that it is not all whitespace....
    CHECK(isCompressionFormat in (0,1)) 
);
---- TODO/NOTE: consider expanding to basic MIME types etc....
INSERT OR IGNORE INTO BlobContentType (name, description, isCompressionFormat)
VALUES ('md', 'Markdown', 0),
       ('pdf', 'Portable Document Format', 0),
       ('gzip', 'GNU Implementation of ZIP, https://web.archive.org/web/20250331225751/https://en.wikipedia.org/wiki/Gzip', 1);

CREATE TABLE IF NOT EXISTS BlobContent(
    sessionID integer,
    ID integer PRIMARY KEY AUTOINCREMENT,
    timeAdded INTEGER DEFAULT CURRENT_TIMESTAMP,
    name TEXT,
    content BLOB NOT NULL,
    contentTypeWhenUncompressed INTEGER,
    contentCompressionTypeIfApplicable INTEGER,
    additionalNoteOrMetadata BLOB,
    FOREIGN KEY (contentTypeWhenUncompressed) REFERENCES BlobContentType( ID),
    FOREIGN KEY (contentCompressionTypeIfApplicable) REFERENCES BlobContentType( ID)
);
CREATE TEMP TRIGGER  AddSessionInfoAndCheck_BlobContent
AFTER INSERT ON BlobContent
FOR EACH ROW 
BEGIN
    UPDATE BlobContent SET 
        sessionID=(SELECT * FROM CurrentSession)
    WHERE ID=new.ID;
    --- We use the RAISE statements below in part due to the 
    --- restrictions on CHECK constraints forbidding subqueries
    SELECT RAISE(ABORT, 
        'Invalid type provided as the non-compressed type of a blob that was attempted to be stored in table BlobContent')
    FROM BlobContentType
    WHERE ID=new.contentTypeWhenUncompressed AND isCompressionFormat=1;
    SELECT RAISE(ABORT, 
        'Invalid type provided as the compressed type of a blob that was attempted to be stored in table BlobContent')
    FROM BlobContentType
    WHERE ID=new.contentCompressionTypeIfApplicable AND isCompressionFormat=0;
END;

CREATE VIEW IF NOT EXISTS BlobContentView (
    name, 
    content,
    string_contentTypeWhenUncompressed,
    string_contentCompressionTypeIfApplicable,
    additionalNoteOrMetadata)
AS SELECT
    A1.name, 
    A1.content,
    B1.name,
    B2.name,
    A1.additionalNoteOrMetadata
FROM
    BlobContent AS A1,
    BlobContentType AS B1,
    BlobContentType AS B2
WHERE
    B1.ID = A1.contentTypeWhenUncompressed AND
    B2.ID = A1.contentCompressionTypeIfApplicable ;
CREATE TRIGGER IF NOT EXISTS InsertInto_BlobContentView
INSTEAD OF INSERT ON BlobContentView
FOR EACH ROW 
BEGIN
    INSERT INTO BlobContent (
        name, content, contentTypeWhenUncompressed, 
        contentCompressionTypeIfApplicable, additionalNoteOrMetadata)
    SELECT 
        new.name, new.content, B1.ID, B2.ID, new.additionalNoteOrMetadata
    FROM
        BlobContentType AS B1,
        BlobContentType AS B2
    WHERE 
        B1.name = new.string_contentTypeWhenUncompressed AND
        B2.name = new.string_contentCompressionTypeIfApplicable ;
END;
