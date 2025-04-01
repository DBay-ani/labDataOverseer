
databaseName="./homeForDatabase/dataOverseerDatabase.db"; # KB is short for "Knowledge Base"
databaseWriteTimeoutLimit= 100; # this is in seconds.
timeToSleepBetweenChecks=10; # 7200; # in seconds
nameOfFileToCauseDaemonToExit="./tmp/internal/END_MAIN_LOOP"


baseOfCommunicationsLocations="/home/b4ba59dcd2b847bb9b12155facf1f0ce/";
directory_communication_incoming=baseOfCommunicationsLocations+"tempDataStore/inbox/";
placeToMoveOldInboxContentTo=baseOfCommunicationsLocations+"tmp/external/";
directory_communication_outgoing=baseOfCommunicationsLocations+"tempDataStore/outbox/";


timeToSleepBetweenChecks_communicationDaemon=5; # In seconds
communicationDaemon_logCycleFrequency=int( 24 * (3600 // timeToSleepBetweenChecks_communicationDaemon));
timeToWaitBeforeDeletingOldReceivedMessageFiles=(24 * 3600); # In seconds
maxSizeCommunicationWillReadInBytes=(2**19); # Half a MiB


defaultInterfaceForFileCommunication="sweet_orchestra_polite_turbot";
