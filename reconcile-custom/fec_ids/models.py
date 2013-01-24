import re

from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES

STATE_CHOICES = dict(STATE_CHOICES)


type_hash={'C':'Communication Cost',
          'D':'Delegate',
          'H':'House',
          'I': 'Not a Committee',
          'N': 'Non-Party, Non-Qualified',
          'P': 'Presidential',
          'Q': 'Qualified, Non-Party',
          'S': 'Senate',
          'X': 'Non-Qualified Party',
          'Y': 'Qualified Party',
          'Z': 'National Party Organization',
          'E': 'Electioneering Communication',
          'O': 'Super PAC'
          }
    
# populated from fec's candidate master
class Candidate(models.Model):
    ## added fields, maybe? 
    #last_name = models.CharField(max_length=100, blank=True, null=True)
    #first_name = models.CharField(max_length=100, blank=True, null=True)
    #middle_name = models.CharField(max_length=100, blank=True, null=True)
    #prefix = models.CharField(max_length=10, blank=True, null=True)
    #suffix = models.CharField(max_length=10, blank=True, null=True)
    ##
    
    cycle = models.CharField(max_length=4) # last year of cycle
    election_year = models.IntegerField(null=True, blank=True) # year of election
    fec_id = models.CharField(max_length=9, blank=True)
    fec_name = models.CharField(max_length=255) 
    party = models.CharField(max_length=3, blank=True)
    office = models.CharField(max_length=1,
                              choices=(('H', 'House'), ('S', 'Senate'), ('P', 'President'))
                              )
    seat_status = models.CharField(max_length=1,
                                  choices=(('I', 'Incumbent'), ('C', 'Challenger'), ('O', 'Open'))
                                  )
    candidate_status = models.CharField(max_length=1,
                                        choices=(('C', 'STATUTORY CANDIDATE'), ('F', 'STATUTORY CANDIDATE FOR FUTURE ELECTION'), ('N', 'NOT YET A STATUTORY CANDIDATE'), ('P', 'STATUTORY CANDIDATE IN PRIOR CYCLE'))
                                         )
  
    district = models.CharField(max_length=2, blank=True)
    # the state where the race is taking place (from the candidate id)
    state_race = models.CharField(max_length=2, blank=True, null=True) 
    campaign_com_fec_id = models.CharField(max_length=9, blank=True)
    
    class Meta:
        unique_together = (("cycle", "fec_id"),)
        
    def race(self):
        
        if self.office == 'P':
            return 'President' 
        elif self.office == 'S' or self.district.startswith('S'):
            return '%s (Senate)' % self.fec_id[2:4]
        else:
            return '%s-%s (House)' % (self.fec_id[2:4], self.district.lstrip('0'))

