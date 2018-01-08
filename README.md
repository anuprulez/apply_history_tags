# Apply tags from root datasets to their children

It propagates (history) tags from a root dataset to all its children. Before executing this script, make sure you have the Galaxy's API key and its instance running. Please execute this script using the following command:

`python apply_tags.py <galaxy_ip> <galaxy_api_key> <history_id optional>`

For example,
`python apply_tags.py "http://localhost:8080" "**********************" "f2db41e1fa331b3e"` or
`python apply_tags.py "http://localhost:8080" "**********************"`

The last argument is history id (which is optional). If not provided, the script will look for all the histories associated with the current user. While running, the script shows which history it is working upon and display datasets one by one with their respective parents (found recursively). When it finishes, please refresh your Galaxy's instance to see the effect.

## Dependencies

Bioblend (https://bioblend.readthedocs.io/en/latest/index.html)

## Feature/Request
https://github.com/usegalaxy-eu/galaxy-freiburg/issues/132

