import logging.handlers
import os, sys, logging

from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.utils.scp import SCP
from jnpr.junos.exception import ConnectError
from getpass import getpass

#define the location of the local package
package_srx = "/home/thor/junos_packages/junos-srxsme-18.4R3.3.tgz"
#srx file destination
srx_local = "/var/tmp/"
#logfile location
logfile = "/home/thor/junos_packages/install.log"

def update_progress(dev, report):
    # log the progress of the installing process
    logging.info(report)

def main():
    # initialize logging
    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s:%(name)s: %(message)s')
    logging.getLogger().name = Device
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info('Information logged in {0}'.format(logfile))

    # hostname = input("Device hostname: ")
    # junos_username = input("Junos OS username: ")
    # junos_password = getpass("Junos OS or SSH key password: ")

    # dev = Device(host=hostname, user=junos_username, passwd=junos_password)
    
    dev = Device(host="192.168.100.1", user="admin", passwd="juniper123")
    dev.open()
    type = (dev.facts["version"])
  
    sw = SW(dev)

    if type == "18.4R3.3":
        logging.info("Already on latest firmware.")
        print("Looks like your device is already on the latest firmware!.")

    elif type != "18.4R3.3":
        print("Not on latest Junos version. Copying/installing latest Junos image to device. Please be patient.")
        try:
            logging.info('Starting the software upgrade process: {0}'.format(package_srx))
            ok = sw.install(package=package_srx,remote_path=srx_local,validate=False,progress=update_progress)
                
        except Exception as err:
            msg = 'Unable to install software, {0}'.format(err)
            logging.error(msg)
            ok = False
            print("Unable to install software.")

        if ok == True:
            print("Software installation complete. Rebooting!")
            logging.info("Software installation complete. Rebooting")
            rsp = sw.reboot()
            logging.info("Upgrade pending reboot cycle, please be patient.")
            logging.info(rsp)
    else:   
        msg = 'Unable to install software, {0}'.format(ok)
        logging.error(msg)
        print("Unable to install software.")

    dev.close()
if __name__ == "__main__":
    main()