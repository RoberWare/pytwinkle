from pytwinkle import Twinkle

def callback(event, *args):
    if event=="registration_succeeded":
        uri, expires = args
        print("registratiom succeeded, uri: %s, expires in %s seconds"%(uri, expires))
        mTP.message("roberlama@sip2sip.info", "Hola\n¿Qué tal?")
        mTP.call("roberlama@sip2sip.info")

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
mTP.set_account("roberlama2","sip2sip.info", "calasanz2920")
mTP.run()