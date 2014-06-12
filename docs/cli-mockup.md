OParl Validator CLI
===================

    $ oparval --help
    Oparl Validator 1.0
    
    usage: oparlval [-h] [-t type] [-a] [-n number] [-v version] [-V] URL       
    
    Validates an OParl System or single OParl Objects.
    To test the whole System use the --all argument.
    
    positional arguments:
      URL                   URL of the API Endpoint or an OParl Object

    optional arguments:
      -h, --help            show this help message and exit
      -t type, --type type  set the document types that should be checked (could
                            be used multiple times)
      -a, --all             test the whole system
      -n number, --max-documents number
                            set max number of documents to test per document type
      -v version, --set-version version
                            set the OParl version. Currently "1" is the only valid
                            option.
      -V, --version         show program's version number and exit



Beispiel 1: Das ganze System testen
-----------------------

    $ oparlval --all http://refserv.oparl.org
    Testing "OParl Reference Server" Oparl version 1.0
    http://refserv.oparl.org/bodies/0/meetings/5 'organization' is a required property
    http://refserv.oparl.org/bodies/0/meetings/5 'auxiliaryDocument' is not of type 'array'
    http://refserv.oparl.org/bodies/0/meetings/5 'resultsProtocol' link is dead (404)

    http://refserv.oparl.org/bodies/0/meetings/12 'resultsProtocol' link is not to an oparl:Document

    Tested: 4042 Objects, 2 with errors; 10 Server Capabilities, 0 errors


Beispiel 2: Nur einen Teil der Objekte testen
-----------------------------------
In diesem Beispiel werden, jeweils maximal zehn "Meeting" Objekte und die damit verknüpften "AgendaItem" Objekte getestet.

    $ oparlval -t meeting -t agendaItem -n 10 http://refserv.oparl.org/bodies/0/meetings

    Tested: 10 meeting Objects, 0 with error
    Tested: 10 agendaItem Objects, 0 with error
