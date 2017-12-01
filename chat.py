
import wx
import threading
from sleekxmpp import ClientXMPP


class chat(wx.TextCtrl,ClientXMPP):
    def __init__(self,parent,*args,**kwargs):
        super(chat,self).__init__(parent,-1,style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.SetSize((parent.GetSize()))
        self.Bind(wx.EVT_KEY_UP,self.onKeyPress)
        self.Hide()
        
        
    def available_menus(self):
        list = ['Chat']
        return list
        
    def args_for_menus(self):
        return []
    
    def start(self,parent,settings,sound,history,root):
        self.parent = parent
        self.settings = settings
        self.sound = sound
        self.history = history
        self.root = root
        
        self.set_colours()
        if self.check_login_info():
            self.initChatList()
            if self.connect():
                self.process(block=True)
        else:
            self.no_login_info()
        self.Show()
        self.parent.Layout()
        self.SetFocus()
        
    def check_login_info(self):
        username = self.settings.get('email','username')
        password = self.settings.get('email','password')
        if not username:
            return 0
        if not password:
            return 0
        else:
            ClientXMPP.__init__(self,username,password)
            return 1
        
    def start_xmpp(self,event):
        print 'start xmpp'
        try:
            self.get_roster()
        except IqError as err:
            pass
        except IqTimeout:
            print ("Error:Request timed out")
        self.send_presence()   
        
        
        #print('Waiting for presence updates...\n')
        self.presences_received.wait(5)
        
        #print('Roster for %s' % self.boundjid.bare)
        groups = self.client_roster.groups()
        for group in groups:
            #print('\n%s' % group)
            #print('-' * 72)
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                print name
                connections = self.client_roster.presence(jid)
                print connections
                for res, pres in connections.items():
                    #show = 'available'
                    print res
                    if pres['show']:
                        show = pres['show']
                        print show
                    #print('   - %s (%s)' % (res, show))

        self.disconnect()
        
    def wait_for_presences(self,pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()
        
    def initChatList(self):
        self.add_event_handler("session_start",self.start_xmpp,threaded=True)
        self.add_event_handler("changed_status",self.wait_for_presences)
        self.received = set()
        self.presences_received = threading.Event()
        print 'chatlist'
            
    def no_login_info(self):
        text = _("Username or password are not set")
        self.SetValue(text)
        self.sound.say(text)
          
    def set_colours(self):
        # Set font,font size, background colour, foreground colour
        font = self.settings.get('window','font')
        font_size = self.settings.get('window','fontsize')
        font_size = int(font_size)
        background_colour = self.settings.get('window','backgroundcolour')
        foreground_colour = self.settings.get('window','foregroundcolour')
        self.font = wx.Font(font_size,wx.DECORATIVE, wx.NORMAL, wx.NORMAL,faceName=font)
        self.SetBackgroundColour(background_colour)
        self.SetForegroundColour(foreground_colour)
        self.SetSize((self.parent.GetSize()))
        self.SetFont(self.font)
        
        
    def onKeyPress(self,event):
        print ''
        
        
    