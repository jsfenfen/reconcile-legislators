from fuzzywuzzy import fuzz
import jellyfish
import unicodedata, pickle
from utils.matchlength import longest_match
from django.db.models import Q
from fec_ids.models import Candidate
from nameparser import HumanName
from datetime import date
from operator import itemgetter

from django.conf import settings

from utils.nicknames import nicknamedict


PICKLED_LOOKUP_FILE = getattr(settings, 'PICKLED_LOOKUP_FILE')
candidate_hash = pickle.load( open( PICKLED_LOOKUP_FILE, "rb" ) )


#push to settings?
default_cycle='2012'

debug=True

# We should have been given a last name to block with. We should probably block by
# something less restrictive (this fails on incorrectly formatted names, i.e. "ron, 
# paul") but... 
# cycle must match a string, not an int, eventually 
def block_by_startswith(name, numchars, state=None, office=None, cycle=None):
    namestart = name[:numchars]
    if debug:
        print "blocking with %s" % (namestart)
        
    matches = Candidate.objects.filter(fec_name__istartswith=namestart)
    
    if office:
        if office.upper() == 'HOUSE':
            matches = matches.filter(office='H')
        elif office.upper() == 'SENATE':
            matches = matches.filter(office='S')
        elif office.upper() == 'PRESIDENT':
            matches = matches.filter(office='P')        
        
    if state:
        state = state.strip().upper()
        matches = matches.filter(state_race=state)
    
    # default to the current year; this will break for the house between jan. 1 and whenever folks are sworn in, usually jan. 3, I think... 
    if cycle:
        # make sure it's a string
        cycle = str(cycle)
        matches = matches.filter(cycle=cycle)
    
    matches = matches.order_by('fec_name', 'office', 'state_race', 'district', 'fec_id', 'party')
    match_values = matches.values('fec_name', 'office', 'state_race', 'district', 'fec_id', 'party').distinct()

    return match_values

def simple_clean(string):
    try:
        string = unicodedata.normalize('NFKD',string).encode('ascii','ignore')
    except TypeError:
        print "unicode typeerror!"
    return string.strip().lower()

# throw out the lowest one and calculate an average. 
def compute_scores(array):
    sorted_array = sorted(array)
    truncated = sorted_array[1:]
    avg = sum(truncated) / float(len(truncated))
    return avg

def unnickname(firstname):
    firstname = simple_clean(firstname)
    try:
        firstname = nicknamedict[firstname]
    except KeyError:
        pass
    return firstname

def hash_lookup(name, state=None, office=None, cycle=None):
    result_array = []
    print "1. running hash lookup with name='%s' and cycle='%s' and state='%s' office='%s'" % (name, cycle, state, office)
    # try to short circuit with the alias table. For now we're using a default cycle--but maybe we should only do this when a cycle is present ?
    # Again, cycle is a string. 
    hashname = str(name).upper().strip().strip('"')
    if cycle:
        hash_lookup_cycle = str(cycle)
    else:
        hash_lookup_cycle = default_cycle
        
    # Our lookup hash is only for 2012 for now, so... 
    # This doesn't address bootstrapping 2012 lookups for 2014...

    if hash_lookup_cycle=='2012':
        try:
            print "2. running hash lookup with name='%s' and cycle='%s'" % (hashname, hash_lookup_cycle)
            found_candidate = candidate_hash[hash_lookup_cycle][hashname]
        except KeyError:
            print "Key error for '%s' '%s'" % (hashname, hash_lookup_cycle)
            return None
        if found_candidate:
            valid_candidate = True
            print "Found candidate %s" % found_candidate
            
            # If we have additional identifiers, insure that they're right. 
            if state and len(state) > 1:
                if state != found_candidate['state']:
                    valid_candidate = False
            if office and len(office) > 0:
                if upper(office) != upper(found_candidate['office']):
                    valid_candidate = False
                    
            if valid_candidate:
                result_array.append({'name':found_candidate['fec_name'], 'id':found_candidate['fec_id'], 'score':1, 'type':[], 'match':True})
                print "Hash lookup succeeded!"
                return result_array
    return None

def run_fec_query(name, state=None, office=None, cycle=None, fuzzy=True):
    
    result = hash_lookup(name, state, office, cycle)
    if result:
        return result
    if not fuzzy:
        return []
    
    result_array = []    
    starts_with_blocklength = 6;
    
    # don't even bother if there are less than 4 letters 
    if (len(name) < 4):
        return result_array
    
    name1 = HumanName(name)
    name1_standardized = simple_clean(name1.last) + " " + unnickname(name1.first)
    
    # we block with the first n characters of the last name
    blocking_name = simple_clean(name1.last)
    
    # if we can't find the last name, assume the name is the last name. This might be a bad idea. 
    if not blocking_name:
        blocking_name = simple_clean(name)
        
    possible_matches = block_by_startswith(blocking_name, starts_with_blocklength, state, office, cycle)
        
    for match in possible_matches:
        
        name2_name = HumanName(match['fec_name'])
        name2 = simple_clean(name2_name.last) + " " + unnickname(name2_name.first)
        # calculate a buncha metrics
        text1 = name1_standardized
        text2 = name2
        #print "comparing '%s' to '%s'" % (text1, text2)
        ratio = 1/100.0*fuzz.ratio(text1, text2)
        partial_ratio = 1/100.0*fuzz.partial_ratio(text1, text2)
        token_sort_ratio = 1/100.0*fuzz.token_sort_ratio(text1, text2)
        token_set_ratio = 1/100.0*fuzz.token_set_ratio(text1, text2)
        
        avg_len = 1/2*len(text1)+len(text2)
        min_len = min(len(text1), len(text2))
        
        l_ratio = 0
        try:
            l_distance = jellyfish.levenshtein_distance(text1, text2)
            l_ratio = 1.0 - ( (0.0 + l_distance) / (0.0+avg_len) )
        except UnicodeEncodeError:
            pass
            
        long_match = longest_match(text1, text2)
        lng_ratio = (0.0 + long_match) / (0.0 + min_len)
        
        score = 0
        if ( ratio > 0.6 or partial_ratio > 0.6 or l_ratio > 0.6 or lng_ratio > 0.6):
            score = compute_scores([ratio,partial_ratio,l_ratio,lng_ratio])
           
        if debug:
            print "Candidate %s vs %s score: %s" % (text1, text2, score)
            print ("ratio=%s partial_ratio=%s token_sort_ratio=%s token_set_ratio=%s, l_ratio=%s lng_ratio=%s") % (ratio, partial_ratio, token_sort_ratio, token_set_ratio, l_ratio, lng_ratio)
        
        
        if (score > 0.8):
            name_standardized = "%s %s (%s: %s-%s)" % (match['fec_name'], match['party'], match['office'], match['state_race'], match['district'])
            result_array.append({'name':name_standardized, 'id':match['fec_id'], 'score':score, 'type':[], 'match':False})
            if debug:
                print "Match found: %s" % name_standardized
    
    if (len(result_array)==0):
        if debug:
            print "No match for %s, which was standardized to: %s" % (name, name1_standardized)
    # surprisingly, google refine *doesn't* sort by score.
    result_array = sorted(result_array, key=itemgetter('score'), reverse=True)
    return result_array
        
