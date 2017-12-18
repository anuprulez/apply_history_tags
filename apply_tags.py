"""
Apply tags to the inherited history items of Galaxy
"""

import sys
import time
from bioblend.galaxy import GalaxyInstance


class ApplyTagsHistory:

    @classmethod
    def __init__( self, galaxy_url, galaxy_api_key ):
        self.galaxy_url = galaxy_url
        self.galaxy_api_key = galaxy_api_key

    @classmethod
    def merge_tags( self, parent_tags, child_tags ):
        """
        Take union of child and parent's tags
        """
        # take all the tags from the child
        tags = child_tags
        for parent_tag in parent_tags:
            parent_tag_name = parent_tag.split( ":" )[ 1 ]
            is_tag_present = False
            for child_tag in child_tags:
                child_tag_name = child_tag.split( ":" )[ 1 ]
                if child_tag_name == parent_tag_name:
                    is_tag_present = True 
            # if parent's tag is not present in the list of child's tags, add it
            if not is_tag_present:
                tags.append( parent_tag )
        return tags

    @classmethod
    def read_galaxy_history( self ):
        """
        Read Galaxy's current history and inherit all the tags from a parent
        to a child history item
        """
        g_instance = GalaxyInstance( self.galaxy_url, self.galaxy_api_key )
        history = g_instance.histories
        current_history = history.get_current_history()
        current_history_id = current_history[ "id" ]

        # get all datasets belonging to a history
        all_datasets = history.show_matching_datasets( current_history_id )
        for dataset in all_datasets:
            if not dataset[ "deleted" ]:
                # current dataset id
                dataset_id = dataset[ "dataset_id" ]
                # get information about the dataset like it's tools, input parameters etc
                # used in its creation. One parameter "input" lists all the dataset id(s) 
                # used in creating the current dataset which is/are its parent datasets
                dataset_info = history.show_dataset_provenance( current_history_id, dataset_id  )
                for attrs in dataset_info:
                    if attrs == "parameters":
                        parameters = dataset_info[ attrs ]
                        for parameter in parameters:
                            if parameter == "input":
                                dataset_parent_inputs = parameters[ parameter ]
                                # get the parent dataset(s)
                                for parent_attr in dataset_parent_inputs:
                                    if parent_attr == "id":
                                        parent_dataset_id = dataset_parent_inputs[ parent_attr ]
                                        parent_dataset = history.show_dataset( current_history_id, parent_dataset_id )
                                        # take a union of all the tags between the child and its parent
                                        appended_tags = self.merge_tags( parent_dataset[ "tags" ], dataset[ "tags" ] )
                                        # do a database update for the child dataset so that it reflects the tags from its parent
                                        history.update_dataset( current_history_id, dataset_id, tags = appended_tags )
                                        print "Tags updated successfully!"


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print( "Usage: python apply_tags.py <galaxy_ip> <galaxy_api_key>" )
        exit( 1 )

    start_time = time.time()

    history_tags = ApplyTagsHistory( sys.argv[ 1 ], sys.argv[ 2 ] )
    history_tags.read_galaxy_history()
    
    end_time = time.time()
    print "Program finished in %d seconds" % int( end_time - start_time )
