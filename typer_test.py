import asyncio
import pyatv
import json
import sys
import os
import re

from atv_keyboard_input import ATVKeyboardInput

scan = pyatv.scan
pair = pyatv.pair
Protocol = pyatv.const.Protocol

loop = asyncio.get_event_loop()


if not os.path.exists("appletv.json"):
    print ("Error: please pair using ps_simple.py before running this program")
    sys.exit(1)

    

j = json.load(open("appletv.json"))
identifier = j["identifier"]
stored_credentials = { Protocol.AirPlay: j["credentials"] }  

async def connect():
    atvs = await scan(loop, identifier=identifier)
    atv = atvs[0]
    for protocol, credentials in stored_credentials.items():
        print ("Setting protocol %s with credentials %s" % (str(protocol), credentials))
        atv.set_credentials(protocol, credentials)
    device = await pyatv.connect(atv, loop)
    print ("Connected!")
    return device



async def main(term, just_clear=False):
    device = await connect()
    keyinput = ATVKeyboardInput(device)
    m=2
    if just_clear:
        m=8
    await keyinput.clear_search(m)
    if just_clear:
        return
    await keyinput.search(term)
    await keyinput.check_context("a") 

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        bn = os.path.basename(sys.argv[0])
        print (f"Usage: {bn} [ -c | --clear ] \"some search term\"")
        sys.exit(1)
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    just_clear = False
    term = args[0]
    if term == "-c" or term == "--clear":
        just_clear=True
        term=""

    loop.run_until_complete(main(term, just_clear))
            
