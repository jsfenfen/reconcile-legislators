import re, pickle

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from fec_ids.models import Candidate

# should go in settings

PICKLED_LOOKUP_FILE = getattr(settings, 'PICKLED_LOOKUP_FILE')
SUBMITTED_FILES_DIR = getattr(settings, 'SUBMITTED_FILES_DIR')



def strip_upper(raw_candidate_name):
    cleaned = str(raw_candidate_name.upper()).strip().strip('"')
    return cleaned
    
class Command(BaseCommand):
    help = "One-off to build lookup tables from submitted files in varying formats, pickle and dump. It's space inefficient b/c candidate data is repeated for each entry; if this becomes a concern could be pushed to a database."
    requires_model_validation = False
    def __init__(self): 
        self.candidate_hash = {}
        self.candidate_hash['2012'] = {}


    def add_to_hash(self, cycle, name, fec_id):
        result = self.candidate_hash[cycle]
        try:
            if result[fec_id] != fec_id:
                raise Exception("new fec_id %s for entry %s does not match existing id: %s" % (fec_id, name, result['fec_id']))
        except KeyError:
            pass
                
        
        name = strip_upper(name)
        
        # get data from the FEC's candidate's database for that year. This sometimes has errors in it -- redistricting seems to be especially problematic for house districts -- but ... 
        fec_data = None
        try:
            fec_data = Candidate.objects.get(fec_id=fec_id, cycle=cycle)
            print fec_data
        except Candidate.DoesNotExist:
            # Will catch header row here too
            print "Missing id: '%s' - %s" % (fec_id, name)
            return None
        
        candidate_hash_entry = {
            'fec_id':fec_id,
            'fec_name':fec_data.fec_name,
            'party':fec_data.party,
            'office':fec_data.office,
            'district':fec_data.district,
            'state_race':fec_data.state_race,
        }
        try:
            self.candidate_hash[cycle][name]
        except KeyError:
            self.candidate_hash[cycle][name] = candidate_hash_entry
        print "'%s':%s" % (name, fec_id)
    
    def handle(self, *args, **options):
                
        if (True):
            # jsvine contrib - for 2012.
            this_cycle = '2012'
            # allow comments; these have been added to document the submissions.
            is_comment = re.compile(r'\s*\#') 
            filename = SUBMITTED_FILES_DIR + "/missing-ids.tsv"
            thisfile = open(filename, "r")
            for line in thisfile:
                if not re.match(is_comment, line):
                    line = line.replace("\n","")
                    fields = line.split('\t')
                    [name, fec_id] = fields
                    self.add_to_hash(this_cycle, name, fec_id)
                
        if (True):
            this_cycle ='2012'
            # sunlight contrib is a python file
            from fec_ids.contributed_data.candidate_2012_ids import candidate_lookup
            for c in candidate_lookup:
                print c, candidate_lookup[c]
                self.add_to_hash(this_cycle, c, candidate_lookup[c])
        
        
        # pickle what we've got
        print self.candidate_hash
        pickle.dump( self.candidate_hash, open( PICKLED_LOOKUP_FILE, "wb" ) )
        
        # load with: candidate_hash = pickle.load( open( pickle_location, "rb" ) )
        
        