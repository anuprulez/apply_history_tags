"""
Apply tags to the inherited history items of Galaxy
"""

import sys
import time


class ApplyTagsHistory:

    @classmethod
    def __init__( self, galaxy_url, galaxy_api_key ):
        self.galaxy_url = galaxy_url
        self.galaxy_api_key = galaxy_api_key


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print( "Usage: python apply_tags.py <galaxy_ip> <galaxy_api_key>" )
        exit( 1 )

    start_time = time.time()

    history_tags = ApplyTagsHistory( sys.argv[ 1 ], sys.argv[ 2 ] )
    
    print history_tags.galaxy_url
    print history_tags.galaxy_api_key
    
    end_time = time.time()
    print "Program finished in %d seconds" % int( end_time - start_time )
