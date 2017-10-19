import json, requests
from datetime import datetime, timedelta
import pickle
import os


def download(apiurl,cache='use',verbose=False,apikey=None):
    """
    download(apiurl,cache='use',verbose=False,apikey=None):

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
        endtime = str_to_date(alldata[-1]['created_at'])+timedelta(seconds=1)
    else: #no cachefile or refresh -> we want to reload from the API
        if verbose: print("Ignoring/overwriting cache")
        if (cache=='only'):
            ##TODO Throw exception - can't only use cache as there is no cache
            assert False, "Can't only use cache as there is no cache"
        nextid = 1
        alldata = []
        endtime = None  
    if (cache=='only'): #we should stop now, and use the cached data we've got
        return alldata
        
    result = None
    if verbose: print("Using %d records from cache" % len(alldata))
    while result != '-1':
        #thingspeak doesn't let you download ranges of ids, instead you have to
        #download ranges of dates. We can only download 8000 at a time, so we
        #need to get the date of the next one we need (then we ask for that datetime
        #until now, and repeat until we run out of new items).
        url = apiurl+'/feeds/entry/%d.json' % (nextid)
        if apikey is not None: url += '?api_key=%s' % apikey
        result = json.loads(requests.post(url).content)
        starttime = endtime
        if result==-1:
            if verbose: print("Warning: Unable to retrieve data (does channel exist? is it public?)")
        if result == '-1':
            endtime = datetime.now()
        else:
            endtime = str_to_date(result['created_at'])
        if (nextid==1):
            starttime = endtime
        else:
            start = datetime.strftime(starttime,'%Y-%m-%dT%H:%M:%SZ')
            end = datetime.strftime(endtime-timedelta(seconds=1),'%Y-%m-%dT%H:%M:%SZ')
            url = apiurl+'/feeds.json?start=%s&end=%s' % (start,end)
            if apikey is not None: url += '&api_key=%s' % apikey            
            data = json.loads(requests.post(url).content)
            if (data!=-1):
                alldata.extend(data['feeds'])
                if verbose: print("    Adding %d records..." % len(data['feeds']))
            else:
                if verbose: print("Warning: unable to read data feed")
            
        nextid += 7999 #thought download was 8000 fields, but it's 8000 records. 8000/len(result)
    if verbose: print("New cache has %d records, saving." % len(alldata))
    pickle.dump( alldata, open( filename, "wb" ) )
    return alldata
    
def str_to_date(st):
    return datetime.strptime(st,'%Y-%m-%dT%H:%M:%SZ')
