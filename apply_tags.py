"""
Apply tags to the inherited history items of Galaxy
"""

import sys
import time
from bioblend.galaxy import GalaxyInstance


class ApplyTagsHistory:

    @classmethod
    def __init__( self, galaxy_url, galaxy_api_key, history_id = None ):
        self.galaxy_url = galaxy_url
        self.galaxy_api_key = galaxy_api_key
        self.history_id = history_id

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
        g_instance = GalaxyInstance( self.galaxy_url, self.galaxy_api_key, self.history_id )
        history = g_instance.histories
        job = g_instance.jobs
        # if the history id is not supplied, then update tags for all the histories accessible to the user
        if self.history_id is None:
            all_histories = history.get_histories()
            for history_item in all_histories:
                print "History name: %s and id: %s" % ( history_item[ "name" ], history_item[ "id" ] )
                self.find_dataset_parents_update_tags( g_instance, history, job, history_item[ "id" ] )
                print "Tags updated for history id: %s" % history_item[ "id" ]
                print "-------------------------------------------------------"
        else:
            try:
                history_item = history.show_history( self.history_id )
                print "History name: %s and id: %s" % ( history_item[ "name" ], history_item[ "id" ] )
                self.find_dataset_parents_update_tags( g_instance, history, job, history_item[ "id" ] )
                print "Tags updated for history id: %s" % history_item[ "id" ]
            except Exception as exception:
                print "Problem occurred with history id: %s" % self.history_id

    @classmethod
    def find_dataset_parents_update_tags( self, g_instance, history, job, history_id ):
        """
        Operate on datasets for a particular history and recursively find parents
        for a dataset
        """
        # get all datasets belonging to a history
        all_datasets = history.show_matching_datasets( history_id )
        for dataset in all_datasets:
            if not dataset[ "deleted" ]: # if dataset is not in a deleted mode
                # current dataset id
                child_dataset_id = dataset[ "id" ]
                # get information about the dataset like the job id
                # used in its creation. One parameter "inputs" from the job details lists all the dataset id(s) 
                # used in creating the current dataset which is/are its parent datasets.
                # get the list of all parents
                parent_dataset_ids = list()
                ds = g_instance.datasets.show_dataset( child_dataset_id )
                print "Dataset: %s " % ds[ "name" ]
                # define a routine to recursively find parent(s) of a dataset
                def recursive_parents( history, job, history_id, dataset_id ):
                    dataset_info = history.show_dataset_provenance( history_id, dataset_id, False )
                    job_details = job.show_job( dataset_info[ "job_id" ], True )
                    if "inputs" in job_details:
                        # get all the inputs for the job that created this dataset.
                        # these inputs are the parent datasets of the current dataset
                        job_inputs = job_details[ "inputs" ]
                        # check for empty input files for root dataset
                        if job_inputs:
                            # collect all the parent datasets
                            for item in job_inputs:
                                # the value of the 'item' varies from tool to tool given the type of input
                                # it could be input or infile or infile1 or in_file. it needs to be generic
                                parent_id = job_inputs[ item ][ "id" ]
                                parent_dataset_ids.append( parent_id )
                                recursive_parents( history, job, history_id, parent_id )
                # collect parents recursively
                recursive_parents( history, job, history_id, child_dataset_id )
                # display all the parents of a particular dataset
                print "Parent datasets for %s: " % ds[ "name" ]
                for item in parent_dataset_ids:
                    parent_ds = g_instance.datasets.show_dataset( item )
                    print parent_ds[ "name" ]
                print "===================================="
                # update history tags for a dataset taking all from its parents if there is a parent
                if len( parent_dataset_ids ) > 0:
                    self.propagate_tags( history, history_id, parent_dataset_ids, child_dataset_id, dataset )

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


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print( "Usage: python apply_tags.py <galaxy_ip> <galaxy_api_key> <history_id as optional parameter>" )
        exit( 1 )

    start_time = time.time()
    history_id = None
    if len( sys.argv ) > 3:
        history_id = sys.argv[ 3 ]
    history_tags = ApplyTagsHistory( sys.argv[ 1 ], sys.argv[ 2 ], history_id )
    history_tags.read_galaxy_history()
    
    end_time = time.time()
    print "Program finished in %d seconds" % int( end_time - start_time )
