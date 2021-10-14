from __main__ import *
import logging


class Configuration (object):
    def __init__(self):
        self.gateway = 'API IP ADDRESS'
        self.version = 'v1'
        self.api_base = 'https://' + self.gateway + '/api/' + self.version
        self.auth = ('username', 'password')
        self.endpoints = {
            'accept_key' : {
                'path' : '/accept_keys',
                'r_id' : ('accept_keys')
            },
            'devices' : {
                'path' : '/devices',
                'r_id' : ('/devices')
            },
            'vlans' : {
                'path' : '/switching/vlans/',
                'r_id' : ('/switching/vlans')                           
            }
        }

    def __update__(self):
        return 'updating'
    def __delete__(self):
        return 'deleting'
class resource_handler ():
    def __init__(self, api_call, call, dev, conf, param,gw_user,gw_password):
        self.api_call = api_call
        self.call = call
        self.dev = dev
        self.conf = conf
        self.param = param
        self.gw_user=gw_user
        self.gw_password=gw_password

def api_call (ep, dev, conf, param,gw_user,gw_password):
    while True:
        logger_debug = logging.getLogger("debugger")
        call = conf.get_list(path=conf.configuration.endpoints[ep]['r_id'], device=dev, parameters=param,gw_user=gw_user,gw_password=gw_password)
        if call.status_code == 200:
            return call.json()
        elif call.status_code == 429:
            logger_debug.info('following device had a problem: ' + str(call.status_code) + ' ' + str(dev) + " " + param)
            time.sleep(10)
            continue
        else:
            #print(param)
            logger_debug.info('following device had a problem: ' + str(call.status_code) + ' ' + str(dev) + " " + param)
            break
class api_client():
    def __init__(self, **kwargs):
        self.configuration = Configuration()
    def get(self,path,gw_user, gw_password):
        url = self.configuration.api_base + path
        try:
        #    rsp = requests.get(url, auth=self.configuration.auth, , verify=False)
            rsp = requests.get(url, auth=(gw_user,gw_password), verify=False)
        except:
            print('unable to execute query: ' + rsp.json())
        
        return rsp
    def printer (self):
        print (self.configuration.gateway)
        print (self.configuration.version)
        print (self.configuration.endpoints)
        print (self.configuration.api_base)
        print (self.configuration.auth)
    def get_list(self, path, device, parameters, gw_user, gw_password):
        url = self.configuration.api_base + self.configuration.endpoints['devices']['r_id'] + '/' + device + path + parameters
        #print(url)    
        try:
            rsp=requests.get(url,auth=(gw_user,gw_password),verify=False)
        except:
            print ('unable to execute query: ' + rsp.json())
        return rsp
