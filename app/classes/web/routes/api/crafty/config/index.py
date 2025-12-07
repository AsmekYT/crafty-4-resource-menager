# imports as before

# keep config the same only add as shown at the top of the file:

config_json_schema = {
    "type": "object",
    "properties": {
        "modrinth_api_token": {
            "type": "string",
            "error": "typeString",
            "fill": True,
        },
# rest of the objects for eg.
#
#       "https_port": {
#           "type": "integer",
#           "error": "typeInteger",
#           "fill": True,
#       },