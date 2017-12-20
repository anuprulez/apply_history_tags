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
            parent_tag_split = parent_tag.split( ":" )
            if len( parent_tag_split ) > 1: # take only hash tags - name: tag_name
                parent_tag_name = parent_tag.split( ":" )[ 1 ]
                is_tag_present = False
                for child_tag in child_tags:
                    child_tag_split = child_tag.split( ":" )
                    if len( child_tag_split ) > 1: # take only hash tags - name: tag_name
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
        job = g_instance.jobs
        # get the Galaxy's current history
        current_history = history.get_current_history()
        current_history_id = current_history[ "id" ]
        # get all datasets belonging to a history
        all_datasets = history.show_matching_datasets( current_history_id )
        for dataset in all_datasets:
            if not dataset[ "deleted" ]: # if dataset is not in a deleted mode
                # current dataset id
                dataset_id = dataset[ "id" ]
                # get information about the dataset like the job id
                # used in its creation. One parameter "inputs" from the job details lists all the dataset id(s) 
                # used in creating the current dataset which is/are its parent datasets.
                # get the list of all parents
                dataset_info = history.show_dataset_provenance( current_history_id, dataset_id, False )
                job_details = job.show_job( dataset_info[ "job_id" ], True )
                if "inputs" in job_details:
                    # get all the inputs for the job that created this dataset.
                    # these inputs are the parent datasets of the current dataset
                    job_inputs = job_details[ "inputs" ]
                    # check for empty input files for root dataset
                    if job_inputs:
                        parent_datasets_ids = list()
                        # collect all the parent datasets
                        for item in job_inputs:
                            # the value of the 'item' varies from tool to tool given the type of input
                            # it could be input or infile or infile1 or in_file. it needs to be generic
                            parent_datasets_ids.append( job_inputs[ item ][ "id" ] )
                        self.propagate_tags( history, current_history_id, parent_datasets_ids, dataset_id, dataset )

    @classmethod
    def propagate_tags( self, history, current_history_id, parent_datasets_ids, dataset_id, dataset ):
        """
        Propagate history tags from parent(s) to a child
        """
        for parent_id in parent_datasets_ids:
            parent_dataset = history.show_dataset( current_history_id, parent_id )
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
