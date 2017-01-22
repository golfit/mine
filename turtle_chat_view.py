import turtle
from turtle_chat_client import Client
from abc import ABCMeta,abstractmethod
from turtle_chat_widgets import Button, TextInput

class TextBox(TextInput) :
    def draw_box(self):
        my_turtle=turtle.clone()
        my_turtle.hideturtle()
        my_turtle.penup()
        my_turtle.width(5)
        my_turtle.shape('circle')
        my_turtle.goto(self.pos[0]-self.width/2,self.pos[1]-self.height/2)
        my_turtle.pendown()
        my_turtle.goto(self.pos[0]+self.width/2,self.pos[1]-self.height/2)
        my_turtle.goto(self.pos[0]+self.width/2,self.pos[1]+self.height/2)
        my_turtle.goto(self.pos[0]-self.width/2,self.pos[1]+self.height/2)
        my_turtle.goto(self.pos[0]-self.width/2,self.pos[1]-self.height/2)
        my_turtle.penup()

    def write_msg(self):
        self.writer.clear()
        #Add newlines every self.letters_per_line for wrapping.
        if(len(self.get_msg()) % self.letters_per_line==0 and len(self.get_msg()) != 0):
            self.new_msg+='\r'
        self.writer.write(self.get_msg())

class SendButton(Button):
    #def __new__(self,view,my_turtle=None,shape=None,pos=(0,0)):
        #Since adding an input, need to override __new__
        #super(SendButton,self).__new__(my_turtle=None,shape=None,pos=(0,0))
        #super(SendButton,self).__new__()

    #def __init__(self,my_turtle=None,shape=None,pos=(0,0),view=None):

    #def __new__(cls,*args,**kwargs):
    #    super(SendButton,self).__new__()

    def __init__(self,my_turtle=None,shape=None,pos=(0,0),view=None):
        super(SendButton,self).__init__(my_turtle=my_turtle,shape=shape,pos=pos)
        if view is None :
            self.view=View()
        else :
            self.view=view

    def get_view(self):
        return self.view()

    def fun(self,x=None,y=None):
        print(self.view.get_msg()) #Debug - print message
        self.view.my_client.send(self.view.get_msg()) #Send message
        #Display message
        #Update view to include new message sent.
        self.view.msg_sent()

class View:
    _MSG_LOG_LENGTH=5 #Number of messages to retain in view
    _SCREEN_WIDTH=300
    _SCREEN_HEIGHT=600
    _LINE_SPACING=round(_SCREEN_HEIGHT/2/(_MSG_LOG_LENGTH+1))

    def __init__(self,username='Me',partner_name='Partner'):
        self.username=username
        self.partner_name=partner_name
        self.msg_queue=[] #List to store all previous messages.
        #Set screen dimensions
        #turtle.setup(View._SCREEN_WIDTH,View._SCREEN_HEIGHT)
        turtle.setup(View._SCREEN_WIDTH,View._SCREEN_HEIGHT)
        turtle.hideturtle()
        #Create one turtle object for each message to display
        self.msg_disp=[]
        turtle.shape('classic')
        for i in range(View._MSG_LOG_LENGTH):
            self.msg_disp.append(turtle.clone()) #Create a turtle object
            self.msg_disp[i].penup() #Do not draw - this turtle will display text, only
            self.msg_disp[i].hideturtle() #Don't show turtle icon
            self.msg_disp[i].goto(-View._SCREEN_WIDTH/2+10,i*View._LINE_SPACING)

        #Encapsulate a chat client
        self.my_client=Client(username,partner_name)

        self.new_msg='' #Stream for sending out message.

        #SendButton(view=self, pos=(0,-View._SCREEN_HEIGHT/2+100))
        self.textbox=TextBox(pos=(0,-100))
        self.send_btn=SendButton(pos=(0,-View._SCREEN_HEIGHT/2+100), view=self,shape='send_button.gif')
        self.setup_listeners()
        self.lowercase=True #Default case of letters

    def msg_sent(self):
        #Add marker that this message is from this (current) user
        show_this_msg=self.username+':\r'+self.textbox.get_msg()
        #Insert message into queue
        self.msg_queue.insert(0,show_this_msg)
        #Update message display
        self.display_msg()
        #Remove message from textbox.
        self.textbox.clear_msg()

    def get_msg(self):
        return self.textbox.get_msg()

    def setup_listeners(self):
        #Set up send button - additional listener, in addition to click,
        #so that return button will send a message.
        turtle.onkeypress( self.send_btn.fun, 'Return')

        turtle.listen()

    def msg_received(self,msg):
        print(msg) #Debug - print message
        show_this_msg=self.partner_name+' says:\r'+ msg
        self.msg_queue.insert(0,show_this_msg) #Insert message into beginning of queue
        self.display_msg() #Update input messages

    def display_msg(self):
        #Display most recent messages, where index, 0, is the most recent
        for i in range(min(len(self.msg_disp),len(self.msg_queue))):
            self.msg_disp[i].clear() #Clear previous text, if any
            self.msg_disp[i].write(self.msg_queue[i])

if __name__ == '__main__':
    my_view=View()
    _WAIT_TIME=200 #Time between check for new message, ms
    def check() :
        msg_in=my_view.my_client.receive()
        if not(msg_in is None):
            if msg_in==my_view.my_client._END_MSG:
                print('End message received')
                sys.exit()
            else:
                my_view.msg_received(msg_in)
        turtle.ontimer(check,_WAIT_TIME) #Check recursively
    check()
    turtle.mainloop()
