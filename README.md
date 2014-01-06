groove-dl
----------------------------
A downloader to Grooveshark's awesome music library. Based off of the [wiki
here](http://nettech.wikia.com/wiki/Grooveshark_Internal_API).

###Syntax:
to interactively search and download:

    python groove.py 'query'

to download the whole playlist:

    python groove.py 'http://grooveshark.com/#!/playlist/asudaihsdias'

to download a whole artist:

    python groove.py 'http://grooveshark.com/#!/profile/asudaihsdias'

sometimes artist are specified using shorter urls:

    python groove.py 'http://grooveshark.com/#!/ozarkhenry'

###Dependencies:

Python2 >= 2.6, with no other external dependencies
