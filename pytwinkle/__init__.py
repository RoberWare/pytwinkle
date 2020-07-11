import os, sys, subprocess, time, re
#from configparser import ConfigParser, RawConfigParser
from multiprocessing import Process, Manager, Value

manager = Manager()

def parse_line(input): 
    """ Parse properties files """
    key, value = input.split('=')
    key = key.strip()  # handles key = value as well as key=value
    value = value.strip()

    return key, value

class Twinkle():
    def __init__(self, callback):
        cmd="twinkle -c"
        self.twinkle_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 
                                                                 stderr=subprocess.STDOUT,
                                                                 stdin=subprocess.PIPE)
        self.session_expires=Value('i', 0)                                                     
        self.keep_session_process = Process(target=self.keep_session, args=[self.session_expires]) #m.group(2)
        
        self.debug=0
        self.stdout= manager.list()
        self.counter = 0
        self.n_line = 0
        self.state = {'name':None,'line':0}
        self.states = ['new_msg', 'incoming_call', 'answered_call'] # They need more than one line.
        self.msg = {"from":None, "to":None, "msg":None}
        self.msgs = []
        self.incoming_call = {"from":None, "to":None}
        self.call_history = []
        self.answered_call = {"code":None, "msg":None, "to":None}
        
        self.callback=callback

    def set_account_by_file(self, path):
        head, filename = os.path.split(path)
        os.system('cp %s ~/.twinkle/%s.cfg'%(path,filename))

    def set_account(self, username, domain, password):
        mod_path = os.path.dirname(__file__)
        configFilePath = mod_path+r'/user.cfg'
        data={}
        block=""
        with open(configFilePath) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    block=line[2:]
                    data[block]={}
                elif not line:
                    continue
                else:
                    key,value = parse_line(line)
                    data[block][key] = value 
                
        data['USER']['user_name']=username
        data['USER']['user_domain']=domain
        data['USER']['auth_name']="%s@%s"%(username, domain)
        data['USER']['auth_pass']=password
        
        n=0
        with open(os.path.expanduser('~/.twinkle/%s.cfg'%(username)), 'w') as f:
            for block in data:
                if n!=0:f.write('\n')
                f.write("# "+block+'\n')
                n+=1
                for key in data[block]:
                    f.write(key+"="+data[block][key]+'\n')
 
 
 
        configFilePath = os.path.expanduser(mod_path+r'/twinkle.sys')
        data={}
        block=""
        with open(configFilePath) as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    block=line[2:]
                    data[block]={}
                elif not line:
                    continue
                else:
                    key,value = parse_line(line)
                    data[block][key] = value 
                
        data['Startup']['start_user_profile']=username
        
        n=0
        with open(os.path.expanduser(r'~/.twinkle/twinkle.sys'), 'w') as f:
            for block in data:
                if n!=0:f.write('\n')
                f.write("# "+block+'\n')
                n+=1
                for key in data[block]:
                    f.write(key+"="+data[block][key]+'\n')      
        
    def set_callback(self, callback):
        self.callback=callback

    def check_registration_succeeded(self, line):
        is_reg = False
        m = re.search(r'(.*): registration succeeded \(expires \= (.*) seconds\)',line)
        if m:
            is_reg = True
            if self.callback: self.callback("registration_succeeded",m.group(1),m.group(2))
            self.session_expires.value=int(m.group(2))
            if not self.keep_session_process.is_alive():
                self.keep_session_process.start()
        return is_reg

    def keep_session(self,seconds):
        while True:
            if (seconds.value>0):
                time.sleep(seconds.value-60)
                seconds.value=0
                self.twinkle_process.stdin.write(str.encode("register\n"))
                self.twinkle_process.stdin.flush()  
            else:
                time.sleep(1)
                if not (seconds.value>0):
                    self.twinkle_process.stdin.write(str.encode("register\n"))
                    self.twinkle_process.stdin.flush()                  
    def check_msg(self,line):
        is_msg=False
        #print(self.n_line-self.state['line'])
        #print(self.state['name'])
        if re.search('Received message',line):
            is_msg=True
            self.state['name'] = 'new_msg'
            self.state['line'] = self.n_line
        elif self.state['name']=='new_msg':
            is_msg=True
            #print("\t?? %s"%(line))
            m=re.search(r'From:\s*sip:(.*)', line) #\s*sip:(.*?)
            n=re.search(r'To:\s*sip:(.*)', line)
            if m:
                self.msg['from'] = m.group(1)
            elif n:
                self.msg['to'] = n.group(1)
            elif (self.n_line-self.state['line'])>=4:
                self.msg['msg']=line
                self.state['name'] = None
                self.state['line'] = 0
                self.msgs.append(self.msg)
                #print("new_msg!")
                #print(self.msg)
                if self.callback: self.callback("new_msg",self.msg)
                self.msg={'from':None, 'to':None, 'msg':None}

    def check_incoming_call(self,line):
        is_call = False
        #print(self.n_line-self.state['line'])
        #print(self.state['name'])
        if re.search(r'Line [0-9]: incoming call',line):
            is_call = True
            #print("?")
            self.state['name'] = 'incoming_call'
            self.state['line'] = self.n_line
        elif self.state['name']=='incoming_call':
            is_call = True
            #print("\t?? %s"%(line))
            m=re.search(r'From:\s*sip:(.*)', line) #\s*sip:(.*?)
            n=re.search(r'To:\s*sip:(.*)', line)
            if m:
                self.incoming_call['from'] = m.group(1)
            elif n:
                self.incoming_call['to'] = n.group(1)
            else:
                self.state['name'] = None
                self.state['line'] = 0
                self.call_history.append(self.incoming_call)
                if self.callback: self.callback("incoming_call",self.incoming_call)
                self.incoming_call={'from':None, 'to':None}
        return is_call
        
    def check_cancelled_call(self,line):
        is_can = False
        m = re.search(r'Line (.*): far end cancelled call.',line)
        if m:
            is_can = True
            if self.callback: self.callback("cancelled_call", m.group(1))
        return is_can
        
    def check_answered_call(self, line):
        is_call = False
        #print(self.n_line-self.state['line'])
        #print(self.state['name'])
        if re.search(r'Line [0-9]: far end answered call.',line):
            is_call = True
            #print("?")
            self.state['name'] = 'answered_call'
            self.state['line'] = self.n_line
        elif self.state['name']=='answered_call':
            is_call = True
            #print("\t?? %s"%(line))
            m=re.search(r'\d+\s*(.*)', line) #\s*sip:(.*?)
            n=re.search(r'To:\s*sip:(.*)', line)
            if m:
                #print("code",m.group(1))
                self.answered_call['msg'] = m.group(1)
                #self.answered_call['msg'] = m.group(2)
            elif n:
                #print("to")
                self.answered_call['to'] = n.group(1)
            else:
                #print("ok")
                self.call_history.append(self.answered_call)
                self.state['name'] = None
                self.state['line'] = 0
                if self.callback: self.callback("answered_call",self.answered_call)
                self.answered_call={'msg':None, 'code':None, 'to':None}
        return is_call        

    def check_ended_call(self, line):
        is_reg = False
        m = re.search(r'Line (.*): far end ended call.',line)
        if m:
            is_reg = True
            if self.callback: self.callback("ended_call",m.group(1))
        return is_reg
            
    def process(self):
        b_length = self.counter-self.n_line
        #print(">>> block %d"%(b_length))
        for x in range(b_length):
            line=self.stdout[self.n_line].decode("utf-8") 
            if self.debug:
                print(line)
            if self.check_registration_succeeded(line):
                pass
            elif self.check_msg(line):
                pass
            elif self.check_incoming_call(line):
                pass
            elif self.check_cancelled_call(line):
                pass
            elif self.check_answered_call(line):
                pass
            elif self.check_ended_call(line):
                pass
            self.n_line+=1

    def get_stdout(self):
        """from http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
        """     
        while True:
            line = self.twinkle_process.stdout.readline()
            #print(line)
            if line != '':
                self.stdout.append(line)
            if not line:# != '' and p.poll() != None:
                break
            #time.sleep(0.5)

        #return str(stdout)

    def register(self):
        self.twinkle_process.stdin.write(str.encode("register -a\n"%(uri)))
        self.twinkle_process.stdin.flush()

    def deregister(self):
        self.twinkle_process.stdin.write(str.encode("deregister\n"%(uri)))
        self.twinkle_process.stdin.flush()

    def call(self, uri):
        self.twinkle_process.stdin.write(str.encode("call %s\n"%(uri)))
        self.twinkle_process.stdin.flush()

    def answer(self):
        self.twinkle_process.stdin.write(str.encode("answer\n"))
        self.twinkle_process.stdin.flush()

    def answerbye(self):
        self.twinkle_process.stdin.write(str.encode("answerbye\n"))
        self.twinkle_process.stdin.flush()    
        
    def reject(self):
        self.twinkle_process.stdin.write(str.encode("reject\n"))
        self.twinkle_process.stdin.flush()    
        
    def bye(self):
        self.twinkle_process.stdin.write(str.encode("bye\n"))
        self.twinkle_process.stdin.flush()

    def hold(self):
        self.twinkle_process.stdin.write(str.encode("hold\n"))
        self.twinkle_process.stdin.flush()
        
    def retrieve(self):
        self.twinkle_process.stdin.write(str.encode("retrieve\n"))
        self.twinkle_process.stdin.flush()
        
    def mute(self):
        self.twinkle_process.stdin.write(str.encode("mute\n"))
        self.twinkle_process.stdin.flush()
        
    def redial(self):
        self.twinkle_process.stdin.write(str.encode("redial\n"))
        self.twinkle_process.stdin.flush()
        
    def quit(self):
        self.twinkle_process.stdin.write(str.encode("quit\n"))
        self.twinkle_process.stdin.flush()
        
    def call(self, uri):
        self.twinkle_process.stdin.write(str.encode("call %s\n"%(uri)))
        self.twinkle_process.stdin.flush()

    def message(self, uri, msg):
        self.twinkle_process.stdin.write(str.encode("message %s %s\n"%(uri, msg)))
        self.twinkle_process.stdin.flush()
        
    def run(self):
        get_stdout_process=Process(target=self.get_stdout,args=[])
        get_stdout_process.start()
        while True:
            #time.sleep(0.5)
            if len(self.stdout) > self.counter:
                #print("hey! %d > %d"%(len(self.stdout), self.counter))
                self.counter = len(self.stdout)
                self.process()
        get_stdout_process.join()

if __name__ == '__main__':
    pass
    
    
    
    