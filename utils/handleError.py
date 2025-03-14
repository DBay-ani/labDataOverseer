
from utils.contracts import requires, ensures;
import sys ;
from databaseIOManager import objDatabaseInterface;
import traceback;


def handleError(specificMessage : str) -> str:
    requires(isinstance(specificMessage, str));
    objDatabaseInterface.connection.rollback();
    errorMessageIndented = "    " + "".join(traceback.format_exc()).replace("\n", "\n    ");
    # exceptionAsStringIndented=str(e).replace("\n", "\n    ");
    stringToPrint=specificMessage +  f"\nDetails:\nTraceback:\n{errorMessageIndented}"; # \nException e:\n{exceptionAsStringIndented}";
    objDatabaseInterface.cursor.execute("INSERT INTO RunLogsTable (logInfo) VALUES (?)", \
        [stringToPrint]);
    objDatabaseInterface.connection.commit();
    sys.stderr.write(stringToPrint);
    sys.stderr.flush();
    return errorMessageIndented;


