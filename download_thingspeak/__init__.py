import json, requests
from datetime import datetime, timedelta
import pickle
import os


def download(apiurl,cache='use',verbose=False):
    """
    download(apiurl,cache='use'):

    Loads thingspeak data from apiurl
    Set cache to:
        'use' - to use it
        'refresh' - to not use it
        'only' - to only use it
    """
    filename = 'channel%s.p'%apiurl.split('/')[-1]
    cachefile = os.path.isfile(filename)
    if (cache=='use' or cache=='only') and cachefile:
        alldata = pickle.load( open( filename, "rb" ) )
        if (cache=='only'):
            if verbose: print("Using just cache - may be out of date")
            return alldata
        if verbose: print("Using cache")
        nextid = alldata[-1]['entry_id']+1
        endtime = datetime.strptime(alldata[-1]['created_at'],'%Y-%m-%dT%H:%M:%SZ')+timedelta(seconds=1)
    else: #no cachefile or refresh -> we want to reload from the API
        if verbose: print("Ignoring/overwriting cache")
        if (cache=='only'):
            ##TODO Throw exception - can't only use cache as there is no cache
            assert False, "Can't only use cache as there is no cache"
        nextid = 1
        alldata = []
        endtime = None    

    result = None
    if verbose: print("Using %d records from cache" % len(alldata))
    while result != '-1':
        result = json.loads(requests.post(apiurl+'/feeds/entry/%d.json' % nextid).content)

        starttime = endtime
        if result == '-1':
            endtime = datetime.now()
        else:
            endtime = datetime.strptime(result['created_at'],'%Y-%m-%dT%H:%M:%SZ')
        if (nextid==1):
            starttime = endtime
        else:
            start = datetime.strftime(starttime,'%Y-%m-%dT%H:%M:%SZ')
            end = datetime.strftime(endtime-timedelta(seconds=1),'%Y-%m-%dT%H:%M:%SZ')
            data = json.loads(requests.post(apiurl+'/feeds.json?start=%s&end=%s' % (start,end)).content)
            alldata.extend(data['feeds'])
            if verbose: print("    Adding %d records..." % len(data['feeds']))
        nextid += 7999 #thought download was 8000 fields, but it's 8000 records. 8000/len(result)
    if verbose: print("New cache has %d records, saving." % len(alldata))
    pickle.dump( alldata, open( filename, "wb" ) )
    return alldata
