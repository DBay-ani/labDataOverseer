
databaseName="./homeForDatabase/flavellLabDataOverseerDatabase.db"; # KB is short for "Knowledge Base"
databaseWriteTimeoutLimit= 100; # this is in seconds.
timeToSleepBetweenChecks=10; # 7200; # in seconds
nameOfFileToCauseDaemonToExit="./tmp/internal/END_MAIN_LOOP"

directory_communication_incoming="/home/b4ba59dcd2b847bb9b12155facf1f0ce/tempDataStore/inbox/";
placeToMoveOldInboxContentTo="/home/b4ba59dcd2b847bb9b12155facf1f0ce/tmp/external/";
directory_communication_outgoing="/home/b4ba59dcd2b847bb9b12155facf1f0ce/tempDataStore/outbox/";


communicationDaemon_logCycleFrequency=1000;
timeToSleepBetweenChecks_communicationDaemon=5; # In seconds
