from utils.contracts import requires, ensures;

import subprocess;


def getRunContext():
    dictToWrite=dict();
    for command in [ ['id'], ['hostname'], ['cat', '/etc/machine-id'], ['pwd'], ['git', 'status'], ['git', 'log', '-n1'], ['env'], ['git', 'diff', 'HEAD']]:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if( len(stderr) > 0 or ((process.returncode) is not None and (process.returncode != 0)) ):
            raise Exception(
                "The following error occurred while gathering information about the running content using commmand"+ \
                str(command)+":\n    "+stderr.replace("\n", "\n    ") \
                );
        dictToWrite[str(command)] = stdout;
    return str(dictToWrite);

