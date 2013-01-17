reconcile-legislators
=====================

A test reconciliation service to match legislators' names. 

Will function as a google refine (now [open refine](https://github.com/OpenRefine) ) [reconciliation service](http://code.google.com/p/google-refine/wiki/)  that matches legislator names to the data about them in [congress-legislators](https://github.com/unitedstates/congress-legislators). Once the data has been reconciled, attributes returned by the service can be accessed via google refine's expression language, for instance: `cell.recon.match.id`. [ See more about [GREL recon expressions](http://code.google.com/p/google-refine/wiki/Variables#Recon)].

In it's current state, the URL for the reconciliation service is `yr-url-here/refine/reconcile/legislators/`. As per the [spec](http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi) any callback arg, i.e. `/refine/reconcile/legislators/?callback=blah` will return the service metadata--most of which can be mocked up anyway. 

Optionally will take a 'state' and 'year' property; the state must be an exact postal service, and the year must be an exact 4-digit year during which the legislator was in office. While the name uses a variety of fuzzy matching techniques, state and year must be exact. 

