import logging.handlers
import os, sys, logging
from getpass import getpass
from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError
from jnpr.junos.exception import UnlockError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError

#location of config file
conf_file = "/home/thor/scripts/utmconfig.conf"
#define the location of the junos imgage 
package_srx = "/home/thor/junos_packages/junos-srxsme-18.4R3-S2.tgz"
#srx file destination
srx_local = "/var/tmp/"

hostname = input("Device IP address: ")
junos_username = input("Junos OS username: ")
if str(junos_username) == "root": 
    sys.exit(
        'Unfortunately the user root is currently not supported - Please run the tool again and choose another user.')
junos_password = getpass("Junos OS password: ")

def main():
    dev = Device(host=hostname, user=junos_username, passwd=junos_password)
    # open a connection with the device and start a NETCONF session
    try:
        dev.open()
    except ConnectError as err:
        sys.exit("Unfortunately the target device is unreachable. Check connection parameters.")
    ######################################################################################
    #######################CONFIG LOAD STARTS HERE########################################
    ######################################################################################
    dev.bind(cu=Config)
    # Lock the configuration, load configuration changes, and commit
    print ("Locking the configuration")

    try:
        dev.cu.lock()
    except LockError as err:
        print ("Unable to lock configuration: {0}".format(err))
        dev.close()
        return

    print ("Loading configuration changes")
    try:
        dev.cu.load(path=conf_file, merge=True)
    except (ConfigLoadError, Exception) as err:
        print ("Unable to load configuration changes: {0}".format(err))
        print ("Unlocking the configuration")
        try:
                dev.cu.unlock()
        except UnlockError:
            print ("Unable to unlock configuration: {0}".format(err))
        dev.close()
        return

    print ("Committing the configuration")
    try:
        dev.cu.commit(comment='Loaded by example.')
    except CommitError as err:
        print ("Unable to commit configuration: {0}".format(err))
        print ("Unlocking the configuration")
        try:
            dev.cu.unlock()
        except UnlockError as err:
            print ("Unable to unlock configuration: {0}".format(err))
        dev.close()
        return

    print ("Unlocking the configuration")
    try:
        dev.cu.unlock()
    except UnlockError as err:
        print ("Unable to unlock configuration: {0}".format(err))
  ######################################################################################
  #######################UPGRADE PROCESS STARTS HERE####################################
  ######################################################################################
    type = (dev.facts["version"])
    sw = SW(dev)

    if type == "18.4R3-S2":
        print("Looks like your device is already on the latest firmware!.")

    elif type != "18.4R3-S2":
        print("Not on latest Junos version. Copying/installing latest Junos image to device. Please be patient.")
        try:
            ok = sw.install(package=package_srx,remote_path=srx_local,validate=False,progress=update_progress)
                
        except Exception as err:
            ok = False
            print("Unable to install software.")

        if ok == True:
            print("Software installation complete. Rebooting!")
            rsp = sw.reboot()
    else:   
        print("Unable to install software.")

    dev.close()
if __name__ == "__main__":
    main()