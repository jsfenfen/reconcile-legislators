import json, re
from utils.json_helpers import render_to_json, render_to_json_via_template
from legislators.legislator_reconciler import run_legislator_query
from fec_ids.fec_reconciler import run_fec_query
from django.views.decorators.csrf import csrf_exempt 
from django.conf import settings

try:
    PREVIEW_BASE_URL = settings.PREVIEW_BASE_URL
    PREVIEW_WIDTH = settings.PREVIEW_WIDTH
    PREVIEW_HEIGHT = settings.PREVIEW_HEIGHT
except:
    raise Exception("Couldn't import preview settings. Are PREVIEW_BASE_URL, PREVIEW_WIDTH and PREVIEW_HEIGHT defined in a settings file?")

# Return the service metadata 
def get_metadata(callbackarg, reconciliation_type):
    
    reconciliation_name = 'sunlight reporting reconcile 0.1'
    PREVIEW_BASE = ""
    if (reconciliation_type=='fec_ids'):
        reconciliation_name = 'fec id matcher 0.1'
        PREVIEW_BASE = PREVIEW_BASE_URL % ('fec_ids')
    elif (reconciliation_type=='legislators'):
        reconciliation_name = 'legislators matcher 0.1'
        PREVIEW_BASE = PREVIEW_BASE_URL % ('legislators')
            
    return render_to_json_via_template("reconcilers/templates/service_metadata.json", {
        'space_base':"http://reporting.sunlightfoundation.com/",
        'url_base':"http://reporting.sunlightfoundation.com/",
        'preview_base':PREVIEW_BASE,
        'reconciliation_name':reconciliation_name, 
        'callbackarg':callbackarg,
        'preview_width':PREVIEW_WIDTH,
        'preview_height':PREVIEW_HEIGHT
    })

def normalize_properties(query):
    # properties can use either 'p' or 'pid'; 'pid' seems to be a throwback to freebase and won't be used here. Convert all pid's or p's to keys
    properties = query.get('properties')
    if not properties:
        return None
    newprop_array = []
    for this_prop in properties:
        try:
            this_prop['pid']
            newprop_array.append({this_prop['pid']:this_prop['v']})
        except KeyError:
            newprop_array.append({this_prop['p']:this_prop['v']})
            
    #print "properties are: %s" % newprop_array
    return newprop_array
    
def do_legislator_query(query):
    #print "running query: %s" % (query['query'])
    properties = normalize_properties(query)
    #print "running query with properties=%s" % (properties)
    state = None
    office = None
    year = None
    congress=None
    if properties:
        for thisproperty in properties:
            for key in thisproperty:
                if key=='state':
                    state = thisproperty['state']
                elif key =='office':
                    office = thisproperty['office']
                elif key =='year':
                    year = thisproperty['year']
                elif key =='congress':
                    congress = thisproperty['congress']
    match_key_hash = run_legislator_query(query['query'], state=state, office=office, year=year, congress=congress)
    return match_key_hash
    
def do_fec_query(query):
    #print "running query: %s" % (query['query'])
    properties = normalize_properties(query)
    #print "running query with properties=%s" % (properties)
    state = None
    office = None
    cycle = None
    if properties:
        for thisproperty in properties:
            for key in thisproperty:
                if key=='state':
                    state = thisproperty['state']
                elif key =='office':
                    office = thisproperty['office']
                elif key =='cycle':
                    cycle = thisproperty['cycle']
    match_key_hash = run_fec_query(query['query'], state=state, office=office, cycle=cycle)
    return match_key_hash
    


def do_query(query, reconciliation_type):
    if reconciliation_type == 'legislators':
        return do_legislator_query(query)
    elif reconciliation_type == 'fec_ids':
        return do_fec_query(query)
    else:
        raise Exception ("Invalid reconciliation type: %s" % (reconciliation_type))

@csrf_exempt
def refine(request, reconciliation_type):
    
    #print "request is: %s" % (request)    
    # spec is to return metadata for any callback arg. 
    if request.REQUEST.get('callback'):
        callbackarg = request.REQUEST.get('callback')
        return get_metadata(callbackarg, reconciliation_type)
        
    query = request.REQUEST.get('query')
    queries = request.REQUEST.get('queries')

    result = {}
    if query:
        #print "query is: %s" % query
        # Spec allows a simplified version, i.e. ?query=boston, so check for that first. 
        # ?query={"query":"boston","type":"/music/musical_group"}
        # ?query={"query":"Ford Taurus","limit": 3,"type":"/automotive/model","type_strict":"any","properties": [{"p":"year","v": 2009},{"pid":"/automotive/model/make","v":{"id":"/en/ford"}} ]}
        # !!This means using the word 'query' in an abbreviated search will break !! 
        if not re.search('query', query):
            query = "{\"query\":\"%s\"}" % query
            #print "revised query is: %s" % query
        
        q = json.loads(query)
        result  = do_query(q, reconciliation_type)
        #print "\n" + str(result)
        thisjson={}
        thisjson['result'] = result
        #print "this json = %s" % thisjson
        return render_to_json(json.dumps(thisjson))
        
    elif queries:
        # ?queries={ "q0" : { "query" : "hackney" }, "q1" : { "query" : "strategic" } }
        q = json.loads(queries)
        thisjson={}
        if q is not None:

            for key, query in q.iteritems():
                
                result  = do_query(query, reconciliation_type)
                #print "\n" + str(result)
                thisjson[key] = {'result':result}
                
        #print "this json: %s" % thisjson
        return render_to_json(json.dumps(thisjson))
        
    else:
        print "Couldn't decode the query JSON!"
        return render_to_json('')
    