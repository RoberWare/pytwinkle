from ..pytwinkle import Twinkle
from ..secrets import NAME, DOMAIN, PASSWORD

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
        
    if event=="failed_call":
        line=args[0]
        print("failed_call, line: %s"%(line))
        
    if event=="dtmf_received":
        line=args[0]
        key=args[0]
        print("dtmf_received, line: %s, key: %s"%(key))
        
    if event=="answered_call":
        call=args[0]
        print("answered: %s"%(str(call)))
        
    if event=="ended_call":
        line=args[0]
        print("call ended, line: %s"%(line))
  
mTP = Twinkle(callback)  
mTP.set_account(NAME, DOMAIN, PASSWORD)
mTP.run()