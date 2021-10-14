from flask_restful import Resource
# netaddr is a fast easy python library to make IP address related operations, but we can get rid of it and make it
# from scratch like: sum(bin(int(x)).count('1') for x in ,mask.split('.'))
from netaddr import IPAddress
from marshmallow import Schema, fields
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

class LGResponseSchema(Schema):
    prefix = fields.String(required=True, default="0.0.0.0/0")
    nexthop = fields.String(required=True, default="0.0.0.0/0")
    localpreference = fields.Integer(required=True, default= 0)
    location = fields.String(required=True, default='')
    metric = fields.Integer(required=False, default=0)

# the below commented Schema is used only in case of POST resquest.
'''
class LGRequestSchema(Schema):
    prefix = fields.String(required=True, description="0.0.0.0/0")
'''

# Define the Internet gateways (strict list) as 1 POP per city or country or any other way.
locations = {'brussels':'bru-11-r331', 'ashburn':'ashb-eqx-r331'} # limited choice just for test


class BGP(MethodResource, Resource):
    @doc(description='BGP looking for a prefix', tags=['BGP LG'])
    @marshal_with(LGResponseSchema)  # marshalling
    def get(self, location, ipaddress, mask):
        router = locations[location]
        smask = str(IPAddress(mask).netmask_bits())
        prefix = ipaddress+"/"+smask
        result = bgp_lookup_function(router, prefix)
        result['prefix'] = prefix
        result['location'] = location
        return result

# function to be called by the class of resources to do the main operation of getting the required results
def bgp_lookup_function(router, prefix):
    # This function can be executed through the Automation Gateway or SSH directly to the router
    # to be figured out
    result = {'nexthop': '192.168.1.34', 'localpreference': 150, 'Metric': 0}
    return result



