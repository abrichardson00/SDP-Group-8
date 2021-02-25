"""
This is the tray module which supports some ReST actions for the tray data
"""

# System modules
import os
import json
import time
from datetime import datetime

# 3rd party modules
from flask import make_response, abort, send_file


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

### when run the server we load the data from the stored json files
def load_tray_data():
    trays_dict = dict()
    tray_path = os.getcwd() + '/trays'
    for file in os.listdir(tray_path):
        json_data = json.load(open(tray_path + '/' + file))
        trays_dict.update({json_data['name']:json_data})
    #print(trays_dict)
    return trays_dict

# whenever TRAYS is updated, we wan't to call this function to update the appropriate file too
def update_tray_json_file(tray_name):
    json_file_path = os.getcwd() + '/trays/' + tray_name + '.json'
    data = TRAYS.get(tray_name)
    json.dump(data, open(json_file_path, 'w'))


# Data to serve with our API
TRAYS = load_tray_data()


def read_image(tray_name):
    """
    This function responds to a get request for /api/images/{tray_name}
    :param tray_name:   name of tray to find
    :return:            image of tray matching tray_name
    """
    # Does the tray exist?
    if tray_name in TRAYS:
        return send_file("/home/andrew/Documents/SDP/server/images/" + tray_name + ".png") # YOU'LL NEED TO CHANGE THIS!

    # otherwise, nope, not found
    else:
        abort(
            404, "Tray with name '{name}' not found".format(name=tray_name)
        )
    

def read_all(search):
    """
    This function responds to a request for /api/trays
    with the complete lists of trays
    :return:        json string of list of trays
    """
    if search == "":
        print("No searching for items")
    else:
        print("We gonna search for an appropriate tray")
        ### I'll implement some sort of search here which will determine the order of the list of tray jsons which we return ###
    
    # Create the list of trays from our data
    return [TRAYS[key] for key in sorted(TRAYS.keys())]


def read_one(name):
    """
    This function responds to a request for /api/trays/{name}
    with one matching tray from TRAYS
    :param name:   name of tray to find
    :return:       tray matching the given name
    """
    # Does the tray exist?
    if name in TRAYS:
        tray = TRAYS.get(name)

    # otherwise, nope, not found
    else:
        abort(
            404, "Tray with name {name} not found".format(name=name)
        )

    return tray




def update(name, tray):
    """
    This function updates an existing tray in the tray structure
    :param name:  name of tray to update in the tray structure
    :param tray:  json of what to update the tray to
    :return:      updated tray structure
    """
    # Does the tray exist in TRAYS?
    if name in TRAYS:
        ### the request from the app only has the ability to change 'info' and 'status'
        ### even if they specify other data to change, it won't be used at all
        if tray.get("info") != None:
            TRAYS[name]["info"] = tray.get("info")
            TRAYS[name]["timestamp"] = get_timestamp()
            update_tray_json_file(name)
        if tray.get("status") != None:
            ### actually need to call appropriate function to make the simulation move tray out / store tray
            if tray.get("status") != TRAYS[name]["status"]:
                if tray.get("status") == "out":
                    bring_tray(name)
                if tray.get("status") == "stored":
                    store_tray(name)
                
        return TRAYS[name]

    # otherwise, nope, that's an error
    else:
        abort(
            404, "Tray with name {name} not found".format(name=name)
        )


### helper functions to update appropriate data when storing / bringing trays ----------------

def store_tray(name):
    # originally status = "out"
    print("Storing tray " + name + " ...")
    
    # should now call some function which actually moves the robot appropriately
    # for now I'll just emulate that behaviour with a wait command
    TRAYS[name]["status"] = "moving"
    update_tray_json_file(name)
    time.sleep(5)

    TRAYS[name]["status"] = "stored"
    TRAYS[name]["timestamp"] = get_timestamp()
    update_tray_json_file(name)

def bring_tray(name):
    # originally status = "stored"
    print("Bringing tray " + name + " out ...")

    # check for any tray currently out, and store it first
    for tray_name in TRAYS:
        if TRAYS[tray_name]["status"] == "out":
            print("Tray " + tray_name + " is currently out")
            store_tray(tray_name)

    # now bring the desired tray out
    # should now call some function which actually moves the robot appropriately
    # for now I'll just emulate that behaviour with a wait command
    TRAYS[name]["status"] = "moving"
    update_tray_json_file(name)
    time.sleep(5)
    
    TRAYS[name]["status"] = "out"
    update_tray_json_file(name)