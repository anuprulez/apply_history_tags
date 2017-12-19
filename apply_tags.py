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
        # connect to running Galaxy's instance
        g_instance = GalaxyInstance( self.galaxy_url, self.galaxy_api_key )
        history = g_instance.histories
        # get the Galaxy's current history
        current_history = history.get_current_history()
        current_history_id = current_history[ "id" ]
        # get all datasets belonging to a history
        all_datasets = history.show_matching_datasets( current_history_id )
        for dataset in all_datasets:
            if not dataset[ "deleted" ]: # if dataset is not in a deleted mode
                # current dataset id
                dataset_id = dataset[ "dataset_id" ]
                # get information about the dataset like it's tools, input parameters etc
                # used in its creation. One parameter "input" lists all the dataset id(s) 
                # used in creating the current dataset which is/are its parent datasets.
                # pull the list of all parents recursively
                dataset_info = history.show_dataset_provenance( current_history_id, dataset_id, True )
                if "parameters" in dataset_info:
                    dataset_parent_inputs = list()
                    parameters = dataset_info[ "parameters" ]
                    if "input" in parameters:
                        dataset_parent_inputs.append( parameters[ "input" ] ) # just one parent
                    elif "input1" in parameters:
                        dataset_parent_inputs = self.create_parent_dataset_inputs( parameters ) # multiple parents
                    self.propagate_tags( history, current_history_id, dataset_parent_inputs, dataset_id, dataset )   

    @classmethod
    def create_parent_dataset_inputs( self, parameters ):
        """
        Create a list of all parent inputs for a dataset.
        """
        parent_input_counter = 1
        dataset_parent_inputs = list()
        while True:
            # parent datasets root attributes comes as 'input1', 'input2' and so on.
            parent_input_name = "input" + str( parent_input_counter )
            if parent_input_name in parameters:
                dataset_parent_inputs.append( parameters[ parent_input_name ] )
                parent_input_counter += 1
            else:
                break
        return dataset_parent_inputs

    @classmethod
    def propagate_tags( self, history, current_history_id, dataset_parent_inputs, dataset_id, dataset ):
        """
        Propagate history tags from parent(s) to a child
        """
        for parent in dataset_parent_inputs:
            parent_dataset_id = parent[ "id" ]
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
