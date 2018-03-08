# Propagate hashtags from root datasets to their children

It propagates hashtags from a root dataset to all its children. Before executing this script, make sure you have the Galaxy's API key and its instance running. You can execute this script using the following command:

`python apply_tags.py <galaxy_ip> <galaxy_api_key> <history_id optional>`

For example,
`python apply_tags.py "http://localhost:8080" "**********************" "f2db41e1fa331b3e"` or
`python apply_tags.py "http://localhost:8080" "**********************"`
`python apply_tags.py "https://usegalaxy.org" "**********************"`

The last argument is history id (an optional one, the other arguments are mandatory). If not provided, the script will take up the most recently used history. At the start, the script shows which history it is working upon. Once it finishes, please refresh your Galaxy's instance to see the effect.

## Dependencies

Bioblend (https://bioblend.readthedocs.io/en/latest/index.html)

## Feature/Request
https://github.com/usegalaxy-eu/galaxy-freiburg/issues/132

