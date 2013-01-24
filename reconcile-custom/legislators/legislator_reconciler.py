from fuzzywuzzy import fuzz
import jellyfish
import unicodedata
from utils.matchlength import longest_match
from django.db.models import Q
from legislators.models import Term, Legislator, Other_Names
from nameparser import HumanName
from datetime import date
from operator import itemgetter


from nicknames.nicknames import nicknamedict

debug=True


# The data isn't by term, but by first and last day; in theory we could give it a time range, but in practice it's easiest to just specify a year. Maybe should modify this to be a term ? 
def block_by_startswith(name, numchars, state=None, office=None, year=None, city=None):
    namestart = name[:numchars]
    if debug:
        print "blocking with %s" % (namestart)
        

    matches = Term.objects.filter(legislator__last_name__istartswith=namestart)
    
    # There's a sorta alias table in othernames. Currently it's mostly empty, but check it anyways. 
    # might be useful to populate ascii versions of nonascii names (lujan; menendez is already in there)
    # the start and end date for the aliases aren't reliably populated, so ignore them.
    alternate_names = Other_Names.objects.filter(last_name__istartswith=namestart)
    alternate_ids = alternate_names.values_list('legislator__bioguide', flat=True)
    if alternate_ids:
        alternate_terms = Term.objects.filter(legislator__bioguide__in=alternate_ids)
        
        matches = matches | alternate_terms
    
    if office:
        if office.upper() == 'HOUSE':
            matches = matches.filter(term_type='rep')
        elif office.upper() == 'SENATE':
            matches = matches.filter(term_type='sen')
        
    if state:
        state = state.strip().upper()
        matches = matches.filter(state=state)
    
    # default to the current year; this will break for the house between jan. 1 and whenever folks are sworn in, usually jan. 3, I think... 
    if not year:
        year = date.today().year
        
    yearint = None
    try:
        yearint = int(year)
    except ValueError:
        pass
    
    if yearint:
        
        end_date = date(yearint, 12, 31)
        # Avoid last few days of year--swearing in is typically Jan. 3
        start_date = date(yearint, 1,10 )
        matches = matches.filter(end__gte=start_date).filter(start__lte=end_date)

    return matches

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

    
def run_legislator_query(name, state=None, office=None, year=None):
    starts_with_blocklength = 6;
    result_array = []
    
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
        
    possible_matches = block_by_startswith(blocking_name, starts_with_blocklength, state, office, year)
        
    for match in possible_matches:
        
        
        name2 = simple_clean(match.legislator.last_name) + " " + unnickname(match.legislator.first_name)
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
            name_standardized = "%s. %s (%s) (%s) %s-%s" % (match.term_type.title(), match.legislator.official_full, match.party, match.state, match.start.strftime("%m/%d/%y"), match.end.strftime("%m/%d/%y"))
#            name_standardized = match.term_type.title() + ". " + match.legislator.official_full + " (" + str(match.party) + ") (" + match.state +") " + match.start.strftime("%m/%d/%y") + "-" + match.end.strftime("%m/%d/%y")
            result_array.append({'name':name_standardized, 'id':match.legislator.bioguide, 'score':score, 'type':[], 'match':False})
            if debug:
                print "Match found: %s" % name_standardized
    
    if (len(result_array)==0):
        if debug:
            print "No match for %s, which was standardized to: %s" % (name, name1_standardized)
    result_array = sorted(result_array, key=itemgetter('score'), reverse=True)
    return result_array
        
"""
url is: /refine/reconcile/legislators/

test from shell with: 
from legislators import legislator_reconciler
legislator_reconciler.run_legislator_query('michaud')




Google docs say response format should look like the below.
refine will quietly fail if any of this stuff is missing; it needs an empty type array
response: 
{
    "result" : [
      {
        "id" : ... string, database ID ...
        "name" : ... string ...
        "type" : ... array of strings ...
        "score" : ... double ...
        "match" : ... boolean, true if the service is quite confident about the match ...
      },
      ... more results ...
    ],
    ... potentially some useful envelope data, such as timing stats ...
  }
  
# issues:


ben ray lujan has an accent over the a in lujan, but often appears without one -- this may require a database level solution. Maybe this is an alias table thingy? 
"""
