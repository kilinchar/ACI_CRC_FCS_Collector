import requests
from config import controller2, username, password
import os
import pandas as pd
from datetime import datetime

crc_api = "/node/class/rmonEtherStats.json?&order-by=rmonEtherStats.modTs|desc"
fcs_api = "/node/class/rmonDot3Stats.json?&order-by=rmonDot3Stats.modTs|desc"
lldp_api = "/node/class/lldpAdjEp.json?&order-by=lldpAdjEp.dn|asc"

# class staticurls():
#     @staticmethod
#     def fcs_url():
#         fcs_url = base_url + fcs_api
#         return fcs_url
#     @staticmethod
#     def crc_url():
#         crc_url = base_url + crc_api
#         return crc_url
#     @staticmethod
#     def lldp_url():
#         lldp_url = base_url + lldp_api
#         return lldp_url

# print(staticurls.fcs_url())
# print("\n")
# print(staticurls.crc_url())


class RestSession():

    def __init__(self, apic, user, password):
        self.ip = apic
        self.username = user
        self.password = password
        requests.packages.urllib3.disable_warnings()
        self.s = requests.session()
        self.base_url = "https://" + str(self.ip) + "/api"
    

    def login(self):
        auth_url = self.base_url + "/aaaLogin.json"
        auth_data = {
            "aaaUser": {
                "attributes": {
                    "name": username,
                    "pwd": password
                }
            }
        }

        response = self.s.post(auth_url, json=auth_data, verify=False)
        return response
    
    def get_json(self, api):
        url = self.base_url + api
        reply = self.s.get(url, verify=False)
        convterted_to_dic = reply.json()
        native = convterted_to_dic["imdata"]
        return native


class Parsers():
    def __init__(self,native):
        self.native = native
    
    def crc(self):
        j = 0
        z = 0
        crc_dic = {}
        for i in self.native:
            dn = i["rmonEtherStats"]["attributes"]["dn"]
            node = dn.split("/")[2]
            interface = dn.split("/")[5][:-1]
            crc = i["rmonEtherStats"]["attributes"]["cRCAlignErrors"]
            try:
                int(interface)
                d = {j: {"Node": node, "interface": interface, "crc": crc}}
                crc_dic.update(d)
                j += 1
            except:
                pass
            z += 1
        return crc_dic, z

    def lldp(self):
        j = 0
        z = 0
        lldp_dic = {}
        for i in self.native:
            dn = i["lldpAdjEp"]["attributes"]["dn"]
            node = dn.split("/")[2]
            try:
                interface = dn.split("/")[6][4:] + "/" + dn.split("/")[7][:-1] ### returns in "eth1/20" format.
                neighbour = i["lldpAdjEp"]["attributes"]["sysName"]
                neighbour_interface = i["lldpAdjEp"]["attributes"]["portIdV"]  ### returns in "eth1/20" format.
                interface.startswith("eth")
                d = {j: {"Node": node, "interface": interface, "neighbour": neighbour, "neighbour_interface":neighbour_interface}}
                lldp_dic.update(d)
                j += 1
            except:
                pass
            z += 1
        return lldp_dic, z

    def fcs(self):
        j = 0
        z = 0
        fcs_dic = {}
        for i in self.native:
            dn = i["rmonDot3Stats"]["attributes"]["dn"]
            fcs = i["rmonDot3Stats"]["attributes"]["fCSErrors"]
            node = dn.split("/")[2]
            try:
                interface = dn.split("/")[4][6:] + "/" + dn.split("/")[5][:-1]
                if interface.startswith("eth"):
                    d = {j: {"Node": node, "interface": interface, "fcs":fcs}}
                    fcs_dic.update(d)
                    j += 1
                else:
                    pass
            except:
                pass
            z += 1
        return fcs_dic, z



class DataFrame(object):
    def __init__(self, dict, max_rows):
        self.max_rows = max_rows
        self.dict = dict
    
    def df(self):
        pd.set_option('display.max_rows', self.max_rows)
        df = pd.DataFrame.from_dict(self.dict, orient="index")
        df.sort_values("Node", ascending=True)
        return df

if __name__ == '__main__':
    session = RestSession(controller2, username, password)
    if session.login().ok:
        native = session.get_json(lldp_api)
        parser = Parsers(native)
        dict = parser.lldp()[0]
        max_row = parser.lldp()[1]
        df = DataFrame(dict, max_row)
        print(df.df())
    else:
        print(session.login().text)