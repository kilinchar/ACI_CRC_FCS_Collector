#Simple Script for CRC/FCS Collection
#Harun KILINC


import requests
import os
import pandas as pd
from datetime import datetime
import time
import numpy as np
import ipaddress
import getpass
import sys

crc_api = "/node/class/rmonEtherStats.json?&order-by=rmonEtherStats.modTs|desc"
fcs_api = "/node/class/rmonDot3Stats.json?&order-by=rmonDot3Stats.modTs|desc"
lldp_api = "/node/class/lldpAdjEp.json?&order-by=lldpAdjEp.dn|asc"


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
            crc = i["rmonEtherStats"]["attributes"]["cRCAlignErrors"]
            try:
                interface = dn.split("/")[4][6:] + "/" + dn.split("/")[5][:-1]
                if interface.startswith("eth"):
                    d = {j: {"Node": node, "interface": interface, "crc": crc}}
                    crc_dic.update(d)
                    j += 1
                else:
                    pass
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
                d = {j: {"Node": node, "interface": interface, "lldp_neighbour": neighbour, "neighbour_interface":neighbour_interface}}
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
    
    @staticmethod
    def df_to_excel(df):
        try:
            t = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            xl = "CRC_FCS_"+t+".xlsx"
            writer = pd.ExcelWriter(xl, engine="xlsxwriter")
            df.to_excel(writer, index = False)
            writer.save()
            print("Please check excel named %s for whole crc and fcs records!" % (xl))
        except:
            print("An exception occurred during the creation of excel for dataframe!!")


if __name__ == '__main__':
    contoller = input("Please enter APIC IP Adress: ")
    username = input("Please enter username for APIC: ")
    password = getpass.getpass("Please enter password for APIC: ")
    try:
        ipaddress.ip_address(contoller)
    except ValueError:
        print('Please check controller address, Given does not appear to be an IPv4')
        print("Exiting!!")
        sys.exit(1)
    try:
        interval = int(input("Please give time as integer value of interval for counters as seconds: "))
    except ValueError:
        print("Interval value is not valid. Please enter interval value as integer!")
        print("Exiting!!")
        sys.exit(1)

    try:
        session = RestSession(contoller, username, password)
        if session.login().ok:
            #Gather Data Frame for LLDP
            native_lldp = session.get_json(lldp_api)
            parser_lldp = Parsers(native_lldp)
            dict_lldp = parser_lldp.lldp()[0]
            max_row = parser_lldp.lldp()[1]
            df_lldp = DataFrame(dict_lldp, max_row).df()
            print("LLDP information is collected. Going for next step!")
            ##Gather Data Frames for first crc, fcs
            #First CRC
            native_crc_1 = session.get_json(crc_api)
            parser_crc_1 = Parsers(native_crc_1)
            dict_crc_1= parser_crc_1.crc()[0]
            max_row = parser_crc_1.crc()[1]
            df_crc_1 = DataFrame(dict_crc_1, max_row).df()
            print("First CRC information is collected. Going for next step!")
            #First FCS
            native_fcs_1 = session.get_json(fcs_api)
            parser_fcs_1 = Parsers(native_fcs_1)
            dict_fcs_1= parser_fcs_1.fcs()[0]
            max_row = parser_fcs_1.fcs()[1]
            df_fcs_1 = DataFrame(dict_fcs_1, max_row).df()
            print("First FCS information is collected. Going for next step!")
            #Merge dfs for 1st round
            df_1 = pd.merge(df_crc_1, df_fcs_1, how="left", on=["Node", "interface"])
            ##Sleep for given internal (sec)
            print("Waiting for %s seconds for 2nd round!" % (interval))
            time.sleep(interval)
            ##Gather Data Frames for second crc, fcs
            #Second CRC
            native_crc_2 = session.get_json(crc_api)
            parser_crc_2 = Parsers(native_crc_2)
            dict_crc_2= parser_crc_2.crc()[0]
            max_row = parser_crc_2.crc()[1]
            df_crc_2 = DataFrame(dict_crc_2, max_row).df()
            print("Second CRC information is collected. Going for next step!")
            #Second FCS
            native_fcs_2 = session.get_json(fcs_api)
            parser_fcs_2 = Parsers(native_fcs_2)
            dict_fcs_2= parser_fcs_2.fcs()[0]
            max_row = parser_fcs_2.fcs()[1]
            df_fcs_2 = DataFrame(dict_fcs_2, max_row).df()
            print("Second FCS information is collected. Going for next step!")
            #Merge dfs for 2nd round
            df_2 = pd.merge(df_crc_2, df_fcs_2, how="left", on=["Node", "interface"])
            #Rename columns for further merge
            df_2.rename(columns={'fcs':'fcs2'}, inplace=True)
            df_2.rename(columns={'crc':'crc2'}, inplace=True)
            #Merge all CRC/FCS dfs
            df_total = pd.merge(df_1, df_2, how="left", on=["Node", "interface"])
            #Convert values of crc and fcs to integer for numeric operaions
            df_total["fcs2"] = df_total["fcs2"].astype(int)
            df_total["crc2"] = df_total["crc2"].astype(int)
            df_total["fcs"] = df_total["fcs"].astype(int)
            df_total["crc"] = df_total["crc"].astype(int)
            #Use np in order to get diff of crcs and fcss
            df_total["crc_diff"] = np.where(df_total["crc"] == df_total["crc2"], 0, df_total["crc2"] - df_total["crc"])
            df_total["fcs_diff"] = np.where(df_total["fcs"] == df_total["fcs2"], 0, df_total["fcs2"] - df_total["fcs"])
            ###Merge lldp and final crc/fcs dfs
            df = pd.merge(df_total , df_lldp, how="left", on=["Node", "interface"])
            df = df.fillna('')
            df = df.sort_values("crc2", ascending=False)
            print("Data collections is ready!!")
            print("Generating Excel!!")
            #Create Excel
            DataFrame.df_to_excel(df)
            time.sleep(1)
            print("#################################################################################")
            print("------------------- Printing Top 20 Based on CRC Values ---------------------")
            print("#################################################################################")
            print(df.head(20))  

        else:
            print("Unable to login due to status code %s and reason is %s " % (session.login().status_code, session.login().reason))
    except requests.exceptions.ConnectionError:
        print("Unable to connect to APIC. Please check IP address you entered or please check your connection to APIC!!")
    except Exception as e:
        print("Exiting due to below exception. Please check below for details!!")
        print("#################################################################################")
        print(e)
        print("#################################################################################")
