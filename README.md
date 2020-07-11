<p align="left" >
<a href="https://github.com/RoberWare/pytwinkle/graphs/contributors"><img src="https://img.shields.io/github/contributors/RoberWare/pytwinkle" alt="Github contributors"/></a>
<!-- <a href="https://github.com/RoberWare/pytwinkle"><img src="https://img.shields.io/github/release-pre/RoberWare/pytwinkle" alt="Github release"/></a>
<a href="https://github.com/RoberWare/pytwinkle/stargazers"><img src="https://img.shields.io/github/stars/RoberWare/pytwinkle" alt="Github stars"/></a> -->
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

#### Description
Twinkle sip client, ported to a python module.

#### Tested environments

|                         |                                         |
|-------------------------|-----------------------------------------|
| **Hardware**            | Rpi zero W                              | 
| **Operating systems**   | Linux                                   |
| **Python versions**     | Python 3.x                              |
| **Distros**             | Raspbian 10                             |
| **Languages**           | English                                 |

#### Instalation
```Shell
sudo apt-get install twinkle
sudo pip3 install pytwinkle
```

#### Example
```Python
from pytwinkle import Twinkle

def callback(event, *args):
    if event=="registration_succeeded":
        uri, expires = args
        print("registratiom succeeded, uri: %s, expires in %s seconds"%(uri, expires))
        # The module keeps the session, you havent to register
        mTP.message("name@domain", "Hello")
        mTP.call("name@domain")

    if event=="new_msg":
        msg=args[0]
        print("new_msg!: "+str(msg))
    
    if event=="incoming_call":
        call=args[0]
        print("call: "+str(call))

    if event=="cancelled_call":
        line=args[0]
        print("call cancelled, line: %s"%(line))
        
    if event=="answered_call":
        call=args[0]
        print("answered: %s"%(str(call)))
        
    if event=="ended_call":
        line=args[0]
        print("call ended, line: %s"%(line))
  
mTP = Twinkle(callback)  
mTP.set_account("name","domain","password")
mTP.run()
```

 - Not supported at the moment
   - redirect	Redirect an incoming call
   - transfer	Transfer a standing call
   - conference	Join 2 calls in a 3-way conference
   - mute		Mute a line
   - dtmf		Send DTMF
   - fetch_reg	Fetch registrations from registrar
   - options		Get capabilities of another SIP endpoint
   - line		Toggle between phone lines
   - dnd		Do not disturb
   - auto_answer	Auto answer
   - user		Show users / set active user
   - presence	Publish your presence state


#### Dependencies
- System dependencies
  - python3
  - twinkle
- Python dependencies
    - multiprocessing
    
#### Mentions
  @LubosD - https://github.com/LubosD/twinkle
  
#### Developer
Roberto Lama Rodríguez - roberlama@gmail.com
 
