# ACI CRC_FCS Collector

## Sections
- [Description](#description)
- [How it Works?](#how-it-works)
- [CRC and FCS on Nexus 9K](#crc-and-fcs-on-nexus-9k)
- [Parsing and Storing Data](#parsing-and-storing-data)
- [How To Install](#how-to-install)
- [Author Info](#author-info)

---

## Description
ACI CRC_FCS Collector is a python based tool that can collect CRC (Both Stomped CRC and FCS) and FCS data from all leaf/spines via APIC. Also It can gather LLDP info and combine these ouputs. This script uses REST API in order to communicate with Fabric.

---

## How it Works

### Cisco ACI 
ACI fabric is SDN Soluiton from Cisco which can build and manage entire fabric from single managment controller called APIC. One of the major benefit of this controller is utilization of REST APIs. Any object can be configured or monitored via REST. That is how we retrieve raw data and later on parse it. 



> **Note:** Please refer official solution link [Cisco ACI for Data Center](https://www.cisco.com/c/en/us/solutions/data-center-virtualization/application-centric-infrastructure/index.html) for more information about ACI

> **Note:** Please refer [ACI Programmability](https://developer.cisco.com/docs/aci/#!introduction#aci-programmability) for more information about Programmability on ACI

---

### CRC and FCS on Nexus 9K

#### Why Frame can be corrupted
Frames can get corrupted due to several reasons mostly L1 issues. Like faulty cabling and broken hardware, buggy software.

#### How Does it Work?
A CRC is an error detection mechanism in order to identify corrupted frames during the transmittion. 
FCS error is observed when a switch receives a frame locally that doesn't match the CRC value in the FCS trailer. 
If that switch oparetes as cut-through (which is the case for N9Ks), switch will forward the frame before receiving complete data and since FCS Trailer is at the end, it will not be able to drop instead it will "stomp" it so that receiver device can understand that frame is corrupted. These packets are forwarded  as output errors. Due to nature of cut-through switching, all path on ACI Fabric, stomped  CRC counters will be increased.

So basically, If interface has only CRC Errors not FCS, than source of the corrupted frame is somewhere else inside or outside of the fabric.  If interface has FCS errors than that interface most probably the origin of the corrupted packet. 

> **Note:** Please refer official  link [Understand Cyclic Redundancy Check Errors on Nexus Switches](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/nx-os-software/217554-understand-cyclic-redundancy-check-crc.html#anc13) for more information CRC on Nexus Switches.




### Parsing and Storing Data

After retriving raw data from APIC,  we need to parse and store for future use.


In our case, script has built in parser functions that can obtain required data. 


> **Note:** For each object that needs to be tracked, will require its own custom parser.




## How To Install

Script can be used alone with running main.py script alone.. 



    Running Standalone Script:

    1. Install dependent libraries (pip install -r requirements.txt)
    2. Run main script (python main.py) in cmd or bash shell.
    3. Script will ask "APIC IP Adress", "username", "password" and finally interval(integer) value (which will be used for as delta time between two CRC/FCS calculation).
    4. Data collection will start for CRC and FCS. Also LLDP information will be gathered and merged with interface dataframe.
    5. Finally, Script will generate an excel for all interfaces of fabric which includes crc/fcs and diff values. Also will print out top 10 interfaces for CRC counters.

---
### Output Example
---

![Flow Diagram](https://user-images.githubusercontent.com/33183236/153854016-5a1aeb9a-c0d3-4b57-bd8e-15081c7e07fc.JPG)


---

If you have any questions or advice, feel free to reach me out. That is all. Enjoy with it.

---

## Author Info
- Linkedin - [Harun KILINC](https://www.linkedin.com/in/harunkilinc/)
