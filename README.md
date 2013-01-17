reconcile-legislators
=====================

A test reconciliation service to match legislators' names. 

Will function as a google refine (now [open refine](https://github.com/OpenRefine) ) [reconciliation service](http://code.google.com/p/google-refine/wiki/)  that matches legislator names to the data about them in [congress-legislators](https://github.com/unitedstates/congress-legislators). Once the data has been reconciled, attributes returned by the service can be accessed via google refine's expression language, for instance: `cell.recon.match.id`. [ See more about [GREL recon expressions](http://code.google.com/p/google-refine/wiki/Variables#Recon)].

In it's current state, the URL for the reconciliation service is `yr-url-here/refine/reconcile/legislators/`. As per the [spec](http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi) any callback arg, i.e. `/refine/reconcile/legislators/?callback=blah` will return the service metadata--most of which can be mocked up anyway. 

Optionally will take a 'state', 'year' or 'office' property; the state must be an exact postal service abbreviation ('CA', 'DC' etc.); the year must be an exact 4-digit year during which the legislator was in office; the office must be either 'HOUSE' or 'SENATE'. While the name is matched against using a mish-mash of fuzzy matching techniques, state, year and office must be exact.

At the moment, matches are done in a two-step process: the first pass is to pull last names that match the first 8-ish characters, the second is to cull this set with fuzzy-matching techniques. Other blocking methods (metaphone on the last name, for instance) might be more useful, depending on the input data.  

