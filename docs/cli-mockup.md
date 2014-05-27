OParl Validator CLI
===================

    $ oparval --help
    Oparl Validator 1.0
    
    Usage: oparlval [-l depth] [-n number] [--compact] URL           
    
    Validates a OParl System or OParl Documents.
    To test the whole System pass the system URL without any arguments.
    
    Options:                                                                        
        -l depth     set max recursion depth
        -n number    set max number of documents to test per document type
        --compact    gives a compact error report     
        -v version   set the OParl Version. Currently "1" is the only valid option.

Das ganze System testen
-----------------------

    $ oparlval refserv.oparl.org
    Testing "OParl Reference Server" Oparl version 1.0
    http://refserv.oparl.org/bodies/0/meetings/5 errors:
    'organization' is a required property
    'auxiliaryDocument' is not of type 'array'
    'resultsProtocol' link (http://refserv.oparl.org/bodies/0/meetings/0/results_protocol) is dead (404)

    http://refserv.oparl.org/bodies/0/meetings/12 error:
    'resultsProtocol' link (http://refserv.oparl.org/bodies/0/meetings/12/results_protocol) is not to a OParl:Document

    Tested: 4042 Documents, 2 with errors; 10 Server Capabilities, 0 errors

Nur einen Teil der Dokumente testen
-----------------------------------

Hierbei werden die Server Anforderungen nicht getestet. Wenn keine OParl Version mit -v angegeben wird, wird von der aktuellen Version ausgegangen.

    $ oparlval -l 2 -n 10 http://refserv.oparl.org/bodies/0/meetings
    http://refserv.oparl.org/bodies/0/meetings/5 errors:
    'organization' is a required property
    'auxiliaryDocument' is not of type 'array'
    'resultsProtocol' link (http://refserv.oparl.org/bodies/0/meetings/0/results_protocol) is dead (404)

    Tested: 20 Documents, 1 with error


Kompakte Fehlerausgabe
----------------------

    $ oparlval -l 2 --compact http://refserv.oparl.org/bodies/0/meetings
    ┌────────────┬─────┬──────────────────────────────────────────────────┐
    │ Type       │  #  │  Errors: id(errors)                              │
    ├────────────┼─────┼──────────────────────────────────────────────────┤
    │ meetings   │ 143 │ 5(iml), 12(l), 25(il), 31(m), 48(m), 42(iml)     │
    │            │     │                                                  │
    │ agendaitems│ 512 │ OK                                               │
    └────────────┴─────┴──────────────────────────────────────────────────┘
    Errors:
    i: invalid attribute(s) 
    m: missing attribute(s)
    l: link(s) dead or wrong