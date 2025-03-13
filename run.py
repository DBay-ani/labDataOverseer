import sqlite3
import config;
from utils.contracts import requires, ensures;

from databaseIOManager import objDatabaseInterface; 

import time;

objDatabaseInterface.open();

import os ;



while( not os.path.exists(config.defaultValues.nameOfFileToCauseDaemonToExit) ):
    
    try:
        print("hi!");
    except:
        print("oh no");


    time.sleep(config.defaultValues.timeToSleepBetweenChecks);
