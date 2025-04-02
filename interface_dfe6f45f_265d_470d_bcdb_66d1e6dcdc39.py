

from interfaceBaseClasses import InterfaceBaseClass;
import typing;
from databaseIOManager import objDatabaseInterface; 
import os;

class interface_dfe6__dc39__sweet_orchestra(InterfaceBaseClass):

    def __init__(self):
        super().__init__();
        self.keysForContentToRead : typing.FrozenSet[str]=\
            frozenset(["base_path", "freely_moving", "all_red", "mNeptune", "OFP", "BFP", "google_sheet", "worm_sex", "worm_strain"]);
        self.keysForFilesInContentToRead : typing.FrozenSet[str]=self.keysForContentToRead.difference(["base_path", "worm_sex", "worm_strain", "google_sheet"]);
        self.keysForURLsInContentToRead : typing.FrozenSet[str]=frozenset(["google_sheet"]);
        self.keysForMetadataInContent : typing.FrozenSet[str]=frozenset(["worm_sex", "worm_strain"]);
        self.keysToInfer :typing.FrozenSet[str] = frozenset(["NIR"]);
        self.allowedFileExtensions : typing.FrozenSet[str]= frozenset({".h5", ".nd2"});
        return ;

    @staticmethod
    def get_human_readable_name() -> str:
        return "sweet_orchestra_polite_turbot";

    def process(self, inputVal : typing.Dict[str, typing.Union[str,typing.Dict[str,typing.Optional[str]]]]) -> typing.Dict[str, typing.Union[str,typing.Dict[str,str]]]:
        keyToFunctionMap={"add": self._add, "ls" : self._ls, "get": self._get, "update": self._update}
        # see TODO(19e8f005-450a-4790-9ee9-0eead5001b4c).
        # if("request" not in inputVal):
        #     raise Exception("The message does not specify a request type "+\
        #         "(note: comparisons are case sensative and the key to use in order to " + 
        #         "specify your request is, well, \"request\").")
        if(inputVal["request"] not in keyToFunctionMap):
            raise Exception(f"Unrecognized user request type: \"{inputVal["request"]}\"");  
        contentToReturn = keyToFunctionMap[inputVal["request"]](inputVal); # ["content"]);
        return contentToReturn;  

    def checkAndRaiseErrorIfUnknownAdditionalKeys(self, \
        addedDescription: str, valToCheck : typing.Dict[str,typing.Any], allowedKeys : typing.FrozenSet[str]) -> None:
        # see TODO(19e8f005-450a-4790-9ee9-0eead5001b4c).
        keysInTopLevelOfInputVal :typing.FrozenSet[str]=frozenset(valToCheck.keys());
        if(keysInTopLevelOfInputVal != allowedKeys):
            raise Exception("Expected keys not found in the message received. Location in the received message where problem arose: "+addedDescription +\
                "\nExtra keys (fine if empty):"+ str(keysInTopLevelOfInputVal.difference(allowedKeys)) +\
                "\nKeys missing (fine if empty):"+str(allowedKeys.difference(keysInTopLevelOfInputVal)) +\
                "\nNOTE: comparisons ARE case-sensative.");
        return;

    def _add_or_update(self, inputVal: typing.Dict[str, typing.Union[str,typing.Dict[str,str]]], \
                       databaseFunctionToExecute : typing.Callable[..., None], messageStringAddition : str, \
                       getdataset_id: typing.Callable[[str], int] ) -> typing.Dict[str,str]:
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request","content"]));
        contentToRecord : typing.Dict[str,str] =inputVal["content"];

        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "in the \"content\" dictionary", contentToRecord, self.keysForContentToRead);        
        for thisKey in self.keysForContentToRead:
            if(not isinstance(contentToRecord[thisKey],str)):
                raise Exception(f"In the \"content\" dictionary, the value of the key \"{thisKey}\" is not a string."+\
                                " Type found for the value:"+str(type(contentToRecord[thisKey])));
            if(len(contentToRecord[thisKey]) ==0):
                raise Exception(f"In the \"content\" dictionary, the value of the key \"{thisKey}\" is an empty string.");
        if(contentToRecord["worm_sex"] not in {"h","m"}):
            raise Exception("Unknown value specified for \"worm_sex\". "+\
                            "We expect either \"h\" for hermaphrodite or \"m\" for male." + \
                            "Value found:\""+contentToRecord["worm_sex"]+"\"");
    
        # TODO: eventually do the below more robustly and in a more generalizable way.
        for thisKey in self.keysToInfer:
            if(thisKey == 'NIR'):
                # Notice that the for-loop which adds many things (but not all things at present)
                # to valuesToRecord checks that such a file exists.
                contentToRecord["NIR"] = contentToRecord["freely_moving"][:-len(".nd2")] + ".h5";

        basePathForFiles= contentToRecord["base_path"];
        if(len(basePathForFiles) < 1):
            raise Exception("Value for \"base_path\" provided is invalid");
        if(basePathForFiles[-1] != "/"):
            basePathForFiles=basePathForFiles+"/";
        
        valuesToRecord=dict();
        for thisKey in self.keysForFilesInContentToRead.union(self.keysToInfer):
            thisFullPath= basePathForFiles + contentToRecord[thisKey];
            if(not os.path.exists(thisFullPath)):
                raise Exception(f"The value for the key \"{thisKey}\" specifies a file that could not be found. The file specified: \"{thisFullPath}\".");
            if(not any([thisFullPath.endswith(thisExtension) for thisExtension in self.allowedFileExtensions])):
                # NOTE: we do a conversion to a set below from a frozenset so that the representation is clearer to people -
                #     don't want those who are not overly familiar with Python to be thrown off by seeing the text "frozenset", etc....
                raise Exception(f"The path provided under the key \"{thisKey}\" specifies a file with an unknown extension. We expected a "+\
                    f"value in {set(self.allowedFileExtensions)} to end the path provided. The path provided by the user was: {thisFullPath}");
            valuesToRecord[thisKey] =  thisFullPath;
        
        # TODO: give better checks for the file existing...below is a bit constrained and
        # misses most critical use cases.
        startingURLLocation="https://docs.google.com/document/d/"
        if(not contentToRecord["google_sheet"].startswith(startingURLLocation)):
            raise Exception(f"The value provided in \"google_sheet\" is not as expected. It does not start with \"{startingURLLocation}\"." + \
                            f"Value provided for \"google_sheet\": {contentToRecord['google_sheet']}");

        valuesToRecord['google_sheet'] =  contentToRecord["google_sheet"];

        # TODO: write explicit checks here that the worm_sex and worm_strain are as expected - but, at present, 
        #     the database does those checks and will raise an exception if they are violated, and I'm low on time.
        for thisKey in self.keysForMetadataInContent:
            valuesToRecord[thisKey] = contentToRecord[thisKey];
        
        dataset_name=contentToRecord["freely_moving"];
        for thisExtension in self.allowedFileExtensions:
            if(dataset_name.endswith(thisExtension)):
                dataset_name=dataset_name[:-len(thisExtension)];
                assert(dataset_name+thisExtension == contentToRecord["freely_moving"]);
                break;
         
        dataset_idNumber=getdataset_id(dataset_name);

        keysInFixedOrder = sorted(list(valuesToRecord.keys()));
        databaseFunctionToExecute(dataset_idNumber, dataset_name, keysInFixedOrder, valuesToRecord);
        #objDatabaseInterface.cursor.execute("INSERT INTO DatasetAndMostRecentFiles( dataset_id, dataset_name, " + ",".join(keysInFixedOrder) +")"+\
        #    "VALUES (?,?,"+  ",".join(["?" for x in keysInFixedOrder]) +")", [dataset_idNumber, dataset_name]+ [valuesToRecord[x] for x in keysInFixedOrder]);
        objDatabaseInterface.connection.commit();

        dataFromDatabaseAfterStoring=[x for x in objDatabaseInterface.cursor.execute("SELECT * FROM DatasetAndMostRecentFiles WHERE dataset_id=?", [dataset_idNumber])];
        contentOfReply={"message": f"Data {messageStringAddition} successfully to database under the dataset name \"{dataset_name}\", ID number {dataset_idNumber}.\n" + \
            "Briefly, data as currently stored in the database:\n\t"+str(dataFromDatabaseAfterStoring)+"\n" +\
            "Issue request for `ls` to retrieve this information again in the future."}
        return contentOfReply;

    def _add(self, inputVal: typing.Dict[str, typing.Union[str,typing.Dict[str,str]]]):
        # databaseFunctionToExecute : typing.Callable[..., None], messageStringAddition : str)
        def databaseFunctionToExecute(dataset_idNumber, dataset_name, keysInFixedOrder, valuesToRecord):
            objDatabaseInterface.cursor.execute("INSERT INTO DatasetAndMostRecentFiles( dataset_id, dataset_name, " + ",".join(keysInFixedOrder) +")"+\
                "VALUES (?,?,"+  ",".join(["?" for x in keysInFixedOrder]) +")", [dataset_idNumber, dataset_name]+ [valuesToRecord[x] for x in keysInFixedOrder]);
            return;
        messageStringAddition="added"  
        def getdataset_id(ignoreVal):
            # TODO: make the below line more robust.
            dataset_idNumber=  [ (1 if (x["maxID"] is None) else (x["maxID"]+1)) for x in objDatabaseInterface.cursor.execute("SELECT max(ID) as maxID FROM Datasets")][0]
            return dataset_idNumber ;
        
        return self._add_or_update(inputVal, databaseFunctionToExecute,messageStringAddition, getdataset_id);

    def _update(self, inputVal: typing.Dict[str, typing.Union[str,typing.Dict[str,str]]]):
        # databaseFunctionToExecute : typing.Callable[..., None], messageStringAddition : str)
        def databaseFunctionToExecute(dataset_idNumber, dataset_name, keysInFixedOrder, valuesToRecord):
            objDatabaseInterface.cursor.execute("UPDATE DatasetAndMostRecentFiles SET dataset_id = ?, dataset_name =?, " + "=? ,".join(keysInFixedOrder) +" =?",\
                 [dataset_idNumber, dataset_name]+ [valuesToRecord[x] for x in keysInFixedOrder]);
            return;
        messageStringAddition="updated"  
        def getdataset_id(dataset_name):
            # TODO: make the below line more robust.
            dataset_idNumber=  [ x for x in objDatabaseInterface.cursor.execute("SELECT ID as ID FROM Datasets WHERE name = ?", [dataset_name])]
            if(len(dataset_idNumber) == 0):
                raise Exception(f"The dataset specified to be updated (\"{dataset_name}\", "+\
                                " as inferred from the file name of the \"freely_moving\" key) does not exist in our records. Has it "+\
                                "been added to the database in the past with the add-request? If not, that should be done, since the " + \
                                "update command will not create datasets if they don't already exist.");
            dataset_idNumber=dataset_idNumber[0]["ID"];
            return dataset_idNumber ;
        
        return self._add_or_update(inputVal, databaseFunctionToExecute,messageStringAddition, getdataset_id);
    


    def _ls(self, inputVal):
        if("content" not in inputVal):
            inputVal["content"] = {"filter": None};
        
        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request","content"]));

        if(inputVal["content"]["filter"] is not None):
            raise NotImplementedError(f"We have not yet implemented filter {inputVal["filter"]} for the \"ls\" command."+ \
                                      " Try again without specifying a filter (just enter \"filter\":null in the content section of your JSON).");

        content=objDatabaseInterface.cursor.execute("SELECT * FROM  DatasetAndMostRecentFiles");
    
        return { x["dataset_name"] : x for x in content }; 

    def _get(self, inputVal):

        self.checkAndRaiseErrorIfUnknownAdditionalKeys(\
            "at top-level of the received message's JSON.", inputVal, frozenset(["interface_id","request", "content"]));
        
        assert(isinstance(inputVal["content"], dict));
        if(set(inputVal["content"].keys()) not in frozenset([ frozenset(["dataset_name"]), frozenset(["dataset_id"]) ]) ):
            raise Exception(f"Unknown filtering criteria to the get-request. "+\
                f"We allow on to filter by \"dataset_name\" or \"dataset_id\". Found keys: {set(inputVal["content"].keys())}");

        # TODO: code the below more robustly.
        key="dataset_name";
        if(list(inputVal["content"].items())[0][0] == "dataset_id"):
            key="dataset_id";
        value=list(inputVal["content"].items())[0][1];

        content=objDatabaseInterface.cursor.execute("SELECT * FROM  DatasetAndMostRecentFiles WHERE " + key +" = ?", \
            [value]);
        content=[x for x in content];
        # TODO: code the below more robustly.
        assert(len(content) <= 1);
        if(len(content) ==0):
            raise Exception(f"Dataset not found: {key}=\"{value}\"")

        return content;