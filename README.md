# Preamble and Information Available Related to this Repository and Its Code

For those with access, visit
[https://github.com/DBay-ani/private_from_dbayani_for_flavell_lab](https://github.com/DBay-ani/private_from_dbayani_for_flavell_lab) 
where you can find a video tutorial and transcript going over the details of this repository's content and what functionality it offers. See [discussionsExplainingThingsAndOrDocumentingThings/links.txt#L22](https://github.com/DBay-ani/private_from_dbayani_for_flavell_lab/blob/212843a0104a1889986a2573a9025469302520ed/discussionsExplainingThingsAndOrDocumentingThings/links.txt#L22) and the file(s) matching "discussionsExplainingThingsAndOrDocumentingThings/transcripts/transcript_*d9M4y2025tzET.txt" in that repository to start. 
- A copy of a redacted transcript from a discussion explaining this code is available here at [./transcript_dbayaniDescribingTheLabDataManagementSystemToPersonZ_d9M4y2025tzET.txt](./transcript_dbayaniDescribingTheLabDataManagementSystemToPersonZ_d9M4y2025tzET.txt), which is copied from the repository [https://github.com/DBay-ani/hub_dbayani_flavell_lab](https://github.com/DBay-ani/hub_dbayani_flavell_lab); be aware that while we believe the redacted transcript adds value for understanding this repository's content, it has not necessarily been reviewed for error either in regard how well it reflects what was actually said or in regard to accuracy of sentiments expressed.
- The material from [https://github.com/DBay-ani/private_from_dbayani_for_flavell_lab](https://github.com/DBay-ani/private_from_dbayani_for_flavell_lab) is also available at [https://zenodo.org/records/17346107](https://zenodo.org/records/17346107) as collected Zip files.

If this material proves useful for you, consider citing it as appropriate. Be aware that, in addition to standard methods of citing works found under this repository or the repository as a whole, the [Zenodo record 17345922, "Collected Publicly Accessibly Content From D Bayani Relating to The Flavell Lab MIT"](https://zenodo.org/records/17345922) also provides a readily available citation equipped with [DOIs](https://www.doi.org/the-identifier/what-is-a-doi/), albeit with regards to a superset of material.


<prev>

# A Few Notes Relating to SQLite3 Use and Databases in General:

First, be aware of the concept of database migration, and aspects of it like Schema migration. Those are terms relating to how one updates the structure of their database and then loads in previously existing data in to the newly shaped store. One tool from SQLite3 that may be particularly useful for that (with respect to the foreseen use of this database) is the `.dump` command in the REPL; you can write the content of the database out to a file as pure SQL using that command. Once the content is dumped to the SQL file, one can modify it - such as removing old schemas that are specified in it, then use it to load the data back into the new database. It may be helpful, if one wants to pursue migration that way, to make use of VIEWs and INSTEAD OF INSERT triggers on them; if the re-arrangements of the data that need to occur can be done in pure SQL or with non-cumbersome foreign-function calls, the TRIGGER on the VIEW could allow insertion like it was a table in the original database, but have the TRIGGER logic take care of how the material should be distributed across the new schema. For more sophisticated modifications, like requiring complex statistical summaries and sophisticated looping/branching control-flow, interacting with the database via Python or some other programming language may be more productive. For the use-cases foreseen, using `.dump` and, as needed, VIEWS would probably cover the vast majority of any need. A few links that may be a helpful starting place for dealing with this further:
- https://www.sqlitetutorial.net/sqlite-dump/
- https://sqlite.org/cli.html#converting_an_entire_database_to_a_text_file
- https://en.wikipedia.org/wiki/Schema_migration
Some tips that might not be immediately useful but good to have around:
- https://stackoverflow.com/questions/989558/best-practices-for-in-app-database-migration-for-sqlite
- https://sqlite.org/cli.html#special_commands_to_sqlite3_dot_commands_
  - One might benefit from being aware of the `.clone` as well as the `.backup` commands, in addition to the `.dump` command listed.
- https://www.sqlite.org/lang_attach.html
  - Possibly useful if one wants to try having the new and the old databases attached and live, then try piping information between them without intermediate files (e.g., ones that `.dump` might produce). I would think, though, that going with an intermediate dump file would be less error prone, while facilitating repeated tries (in case first attempts run into issues).


BE AWARE THAT THE SQLite3 REPL AUTO-COMMITS BY DEFAULT - some changes you make in the REPL WILL permanently be reflected in the database. To enable a transaction - which would prevent changes you make (such as by accident) from being permanent unless you explicitly COMMIT them - try issuing BEGIN as the first command in the REPL, which opens a transaction you can back-out of. For example:
```
$ sqlite3 homeForDatabase/dataOverseerDatabase.db 
SQLite version 3.45.3 2024-04-15 13:34:05
Enter ".help" for usage hints.
sqlite> .tables
BlobContent                          DatasetAndMostRecentIndividualFiles
[...manually shortened....]                       
ContactorsTable                      MessageTable                       
DataContentType                      RunLogsTable                       
DatasetAndMostRecentFiles            SessionContextWhenStarted          
sqlite> BEGIN
   ...> ;
sqlite> DROP TABLE RunLogsTable ;
sqlite> .tables
BlobContent                          DatasetAndMostRecentIndividualFiles
[...]                        
ContactorsTable                      MessageTable                       
DataContentType                      SessionContextWhenStarted          
DatasetAndMostRecentFiles          
sqlite> ROLLBACK ;
sqlite> .tables
BlobContent                          DatasetAndMostRecentIndividualFiles
[...]                          
ContactorsTable                      MessageTable                       
DataContentType                      RunLogsTable                       
DatasetAndMostRecentFiles            SessionContextWhenStarted          
sqlite> SELECT count(*) FROM RunLogsTable;
44
sqlite> 
```
Some other auto-commit related things worth being aware of:
- (potentially) https://www.sqlite.org/c3ref/get_autocommit.html
- see the "autocommit" argument at https://docs.python.org/3/library/sqlite3.html#sqlite3.connect , and where it occurs in the `databaseIOManager.py` file of in this code repo, for instance.



Also, I suggest reading over  the following at least once so that you can be aware of the immediate tool easily at your disposal:
https://sqlite.org/cli.html#special_commands_to_sqlite3_dot_commands_

</prev>
