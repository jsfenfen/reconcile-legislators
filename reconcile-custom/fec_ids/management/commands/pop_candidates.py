

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from fec_ids.models import Candidate

DATA_DIR = "./fec_ids/data"


class Command(BaseCommand):
    args = '<cycle>'
    help = "Populate the candidates table from the candidate master file. Use a 2-digit cycle"
    requires_model_validation = False
    
    def handle(self, *args, **options):
        cycle = args[0]
        cycle_year = 2000 + int(cycle)
        if cycle_year > 2020:
            cycle_year = cycle_year - 100;
        assert cycle, "You must enter a two-digit cycle"

        data_filename = "%s/%s/cn.txt" % (DATA_DIR, cycle)
        data_file = open(data_filename, "r")
        for line in data_file:
            line = line.replace("\n","")
            columns = line.split("|")
            data_dict = {}
            
            data_dict['cycle']=cycle_year
            data_dict['fec_id'] = columns[0].strip()
            data_dict['fec_name'] = columns[1].strip()            
            data_dict['party'] = columns[2].strip()
            data_dict['election_year'] = columns[3].strip()
            data_dict['state_race'] = columns[4].strip()
            data_dict['office'] = columns[5].strip()
            data_dict['district'] = columns[6].strip()                                                            
            data_dict['seat_status'] = columns[7].strip() 
            data_dict['candidate_status'] = columns[8].strip()
            data_dict['campaign_com_fec_id'] = columns[9].strip()
#            data_dict['zipcode'] = columns[14].strip()

            
            
            try:
                existing_candidate = Candidate.objects.get(fec_id=data_dict['fec_id'], cycle=cycle_year)

            except Candidate.DoesNotExist:
                
                
                # office is the first digit of the fec_id (?)
                office = data_dict['fec_id'][0]
                # state race is the next two digits

                
                print "Adding candidate with name: %s id: %s" % (data_dict['fec_name'], data_dict['fec_id'])
                Candidate.objects.create(**data_dict)
                