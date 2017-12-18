# Apply tags from root datasets to their children

It propagates (history) tags from a root dataset to all its children. Before executing this script, make sure you have Galaxy's API key and its instance running. Please execute this script using the following command:

`python apply_tags.py <galaxy_ip> <galaxy_api_key>`

For example, `python apply_tags.py "http://localhost:8080" "**********************"`

When it finishes, please refresh your Galaxy's instance to see the effect.

## Dependencies

Bioblend (https://bioblend.readthedocs.io/en/latest/index.html)


