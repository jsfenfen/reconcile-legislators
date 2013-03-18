reconcile-legislators
=====================

A test google refine (now [open refine](https://github.com/OpenRefine) ) [reconciliation service](http://code.google.com/p/google-refine/wiki/)  that matches legislator names to the data about them in [congress-legislators](https://github.com/unitedstates/congress-legislators) (data is for all legislators), or candidate names to FEC ids (available electronically to the 1980's or so). 

Once the data has been reconciled, attributes returned by the service can be accessed via google refine's expression language, for instance:  `cell.recon.match.id`. [ See more about [GREL recon expressions](http://code.google.com/p/google-refine/wiki/Variables#Recon)].

Candidates
----------
URL is `yr-url-base/refine/reconcile/fec_ids/` . Also takes a 'state' (2-letter postal code), 'cycle' (4-digit even year ending cycle, i.e. 2012 for 2011-12) and office (case insensitive 'House' or 'Senate'). If a cycle isn't specified, many cycles will be returned. This can be especially confusing if the candidate's district number ever changed. 

Uses same general matching approach, and blocks with the last name. Thus, reversed names--i.e. "ron, paul"--won't work...

Before fuzzy matching is conducted, a lookup table is consulted; if a lookup entry is found that is returned as a match, with score set to 1. If a candidate is found by fuzzy matching the match boolean is set to false, and a numberic score of 0-1 is returned. 

An alternate end point that only checks the alias table for matches is also available--it's generally much faster. It is at: `yr-url-base/refine/reconcile/fec_ids_nofuzzy/`.

Legislators
-----------
In it's current state, the URL for the legislators reconciliation service is `yr-url-here/refine/reconcile/legislators/`. As per the [spec](http://code.google.com/p/google-refine/wiki/ReconciliationServiceApi) any callback arg, i.e. `/refine/reconcile/legislators/?callback=blah` will return the service metadata--most of which can be mocked up anyway. 

Optionally will take a 'state', 'year' or 'office' property; the state must be an exact postal service abbreviation ('CA', 'DC' etc.); the year must be an exact 4-digit year during which the legislator was in office; the office must be either 'HOUSE' or 'SENATE' (case insensitive). While the name is matched against using a mish-mash of fuzzy matching techniques, state, year and office must be exact.

Fuzzy Matching
-----

At the moment, matches are done in a multi-step process: the first pass is to pull last names that match the first 8-ish characters, the second is to cull this set with fuzzy-matching techniques. Other blocking methods (metaphone on the last name, for instance) might be more useful, depending on the input data.

Because it's relatively common for names to appear switched (i.e. "Ron, Paul") the matcher will try to find matches for a reversed version of the name with the same technique. This can be turned off for better performance by setting CHECK_FOR_NAME_REVERSALS to 'False' in the local_settings file.

Logging is set up to record all fuzzy match attempts; the hope is that examination of scoring metrics will help 'tune' them. 

Contributed Alias Tables
----
Some somewhat random alias tables are available--for the 2012 cycle--in fec_ids/contributed_data. These exist as is; there's a management command called generate_lookup_tables that reads these and pickles into a location set by the settings file. 

Simplified candidates direct json call
----
A slightly simplified syntax is available for directly querying the candidates match engine outside of google refine. Specifically, it doesn't require the odd 'pid':'v' properties list. Like refine, it uses json urlencoded and passed as a GET argument. It's at: `/refine/reconcile-json/fec_ids_nofuzzy/` or `/refine/reconcile-json/fec_ids/`.

Instead of using what refine would generate--something like:

> /?queries={"q0":{"query":"runyan, jon","type":"","type_strict":"should","properties":[{"pid":"state","v":"NJ"}]},"q1":{"query":"Romney, Mitt","type":"","type_strict":"should","properties":[{"pid":"state","v":""}]}}


set the properties values of the query as top-level elements of query item

> /?queries={"q0":{"query":"runyan, jon","state":"NJ"}, "q1":{"query":"Romney, Mitt","state":"", "cycle":"2012"}}


The return values use the query names, and look like this (they are not necessarily returned in the order they are given):

> {"q1": {"result": [{"score": 1, "type": [], "name": "ROMNEY, MITT / RYAN, PAUL D. - REP (P: US-)", "match": true, "id": "P80003353"}]}, "q0": {"result": [{"score": 1, "type": [], "name": "RUNYAN, JON - REP (H: NJ--03)", "match": true, "id": "H0NJ03153"}]}}
	
There's not a hard cap to the number of queries per request, but refine limits it to 10 or so. 