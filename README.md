reconcile-legislators
=====================

A test google refine (now [open refine](https://github.com/OpenRefine) ) [reconciliation service](http://code.google.com/p/google-refine/wiki/)  that matches legislator names to the data about them in [congress-legislators](https://github.com/unitedstates/congress-legislators) (data is for all legislators), or candidate names to FEC ids (available electronically to the 1980's or so). 

Once the data has been reconciled, attributes returned by the service can be accessed via google refine's expression language, for instance: `cell.recon.match.id`. [ See more about [GREL recon expressions](http://code.google.com/p/google-refine/wiki/Variables#Recon)].

Legislators
-----------
In it's current state, the URL for the legislators reconciliation service is `yr-url-here/refine/reconcile/legislators/`. As per the [spec](http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi) any callback arg, i.e. `/refine/reconcile/legislators/?callback=blah` will return the service metadata--most of which can be mocked up anyway. 

Optionally will take a 'state', 'year' or 'office' property; the state must be an exact postal service abbreviation ('CA', 'DC' etc.); the year must be an exact 4-digit year during which the legislator was in office; the office must be either 'HOUSE' or 'SENATE' (case insensitive). While the name is matched against using a mish-mash of fuzzy matching techniques, state, year and office must be exact.

At the moment, matches are done in a two-step process: the first pass is to pull last names that match the first 8-ish characters, the second is to cull this set with fuzzy-matching techniques. Other blocking methods (metaphone on the last name, for instance) might be more useful, depending on the input data.  

Candidates
----------
URL is `yr-url-base/refine/reconcile/fec_ids/` . Also takes a 'state' (2-letter postal code), 'cycle' (4-digit even year ending cycle, i.e. 2012 for 2011-12) and office (case insensitive 'House' or 'Senate'). If a cycle isn't specified, many cycles will be returned. 

Uses same general matching approach, and blocks with the last name. Thus, reversed names--i.e. "ron, paul"--won't work...
