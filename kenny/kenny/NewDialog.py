# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 <Sven Kamieniorz> <svenkamieniorz@gmail.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from gi.repository import Gtk # pylint: disable=E0611
import commands
import os

from kenny_lib.helpers import get_builder

import gettext
from gettext import gettext as _
gettext.textdomain('kenny')

class NewDialog(Gtk.Dialog):
    __gtype_name__ = "NewDialog"
    sname =''

    def __new__(cls):
        builder = get_builder('NewDialog')
        new_object = builder.get_object('new_dialog')
        new_object.finish_initializing(builder)
        return new_object

    def getAppbyIndex(self,index):
        app = ''
        if (index == 1):
            app = 'firefox '
        elif(index==2):
            app='google-chrome '
        elif(index==3):
            app='gedit '
        elif(index==4):
            app='nautilus '
        elif(index==6):
            app='netbeans '
        elif(index==7):
            app='thunderbird '
        elif(index==8):
            app='evolution '
        elif(index==9):
            app='pidgin '
        elif(index==10):
            app='empathy '
        elif(index==11):
            app='skype '
        elif(index==12 or index==5):#gnome - terminal, command, Quickly
            app=''
        elif (index == 13):
            app = 'libreoffice '
        elif (index == 14):
            app = 'rhythmbox '
        elif (index == 15):
            app = 'vlc'
        return app

    def finish_initializing(self, builder):
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self)           

        #--- Building the Grid
#        grid = Gtk.Grid()
        global grid
        grid =  builder.get_object('grid2')
        cell = Gtk.CellRendererText()
        liststoreApplications = Gtk.ListStore(str)
        liststoreApplications.append(['Select an Application'])#0
        liststoreApplications.append(['Firefox'])
        liststoreApplications.append(['Chrome'])
        liststoreApplications.append(['Gedit'])
        liststoreApplications.append(['Nautilus'])
        liststoreApplications.append(['Quickly'])#5
        liststoreApplications.append(['Netbeans'])
        liststoreApplications.append(['Thunderbird'])
        liststoreApplications.append(['Evolution'])#8
        liststoreApplications.append(['Pidgin'])
        liststoreApplications.append(['Empathy'])
        liststoreApplications.append(['Skype'])
        liststoreApplications.append(['Custom'])#12
        liststoreApplications.append(['Libre Office'])#13
        liststoreApplications.append(['Rhythmbox'])#14
        liststoreApplications.append(['VLC Media Player'])#15

        #--- First Row
        grid.attach(Gtk.Label("#"),0,0,1,1)        
        grid.attach(Gtk.Label("Application"),1,0,1,1)   
        grid.attach(Gtk.Label("Parameter"),2,0,1,1)   

        global comboboxes
        comboboxes = {}

        for n in range(5):
            #Number of the row
            grid.attach(Gtk.Label(str(n+1)),0,(n+1),1,1)    
            #Application Combobox
            combobox = Gtk.ComboBox()
            combobox.name="combobox"+str(n)
            combobox.pack_start(cell,False)
            combobox.add_attribute(cell, 'text', 0)    
            combobox.set_wrap_width(1)
            combobox.set_model(liststoreApplications)
            combobox.connect('changed', self.changed_cb,grid,n)
            combobox.set_active(0)
            global comboboxes
            comboboxes[n]=combobox
            global grid
            grid.attach(combobox,1,n+1,1,1)
            button=self.builder.get_object('button'+str(n+1))
            button.connect('clicked', self.test_command,grid,n,combobox)

#The ok-button should only be able to press if a script-name is entered
        self.builder.get_object('btn_ok').set_sensitive(False)
        self.builder.get_object('dialog-vbox1').show_all()

    def on_entry1_changed(self, entry, data=None):
        if(entry.get_text_length()==0):
            self.builder.get_object('btn_ok').set_sensitive(False)
        else:             
            self.builder.get_object('btn_ok').set_sensitive(True)

    def test_command(self, button=None,data=None,row=0,combobox=None):

        index = combobox.get_active()
        parameter = self.builder.get_object('entry'+str(row+2)).get_text()

        app = self.getAppbyIndex(index)


        #Exception for the terminal
#        if index == 12:
#            cmd='gnome-terminal -e '" bash -c \'' + parameter + ' exec bash\'" &'

        if index == 12:
            cmd = parameter          
        elif index == 5: #Quickly
            cmd = "cd "+ str(parameter)+ " ; quickly edit & quickly design & quickly run"+str(' &')
        else:
            cmd = str(app)+ str(parameter)+str(' &')

        os.system(cmd)

    def changed_cb(self, combobox,data=None,row=0):
        model = combobox.get_model()
        index = combobox.get_active()
        if index <= 0: #nothing to show if the default text (0) or nothing (-1) is selected 
            entry = self.builder.get_object('entry'+str(row+2))
            entry.hide()
            Gtk.Entry.set_placeholder_text(entry,"")
            return

        elif (index == 1 or index == 2): #Firefox, Chrome
            entry = self.builder.get_object('entry'+str(row+2))
            entry.show()
            Gtk.Entry.set_placeholder_text(entry,"Enter URL (e.g: www.ubuntu.com)")

        elif index == 4 or index == 13 or index == 14 or index == 15: #Nautilus,openoffice,rythmbox,vlc #with path
            entry = self.builder.get_object('entry'+str(row+2))
            entry.show()
            Gtk.Entry.set_placeholder_text(entry,"Enter Path (e.g: ~/Downloads")

        elif index == 5:#Quickly
            entry = self.builder.get_object('entry'+str(row+2))
            entry.show()
            Gtk.Entry.set_placeholder_text(entry,"Enter Path (e.g:~/workspace/quickly/kenny/")
            
            #Gedit,Netbeans, ,Tunderbird, Evolution,pidgin, empathy,skype #without parameter
        elif index ==3 or index==6  or index == 7 or index == 8 or index == 9 or index == 10 or index == 11 : 
            entry = self.builder.get_object('entry'+str(row+2))
            entry.hide()
        #Gnome-Terminal #custom
        elif index==12 :
            entry = self.builder.get_object('entry'+str(row+2))
            entry.show()            
            Gtk.Entry.set_placeholder_text(entry,"Write terminal command (e.g: java -jar ~/jdownloader/JDownloader.jar")#java -jar ~/jdownloader/JDownloader.jar #e.g: sudo shutdown  40;
        return

    def on_btn_ok_clicked(self, widget, data=None):
        """The user has elected to save the changes.

        Called before the dialog returns Gtk.ResponseType.OK from run().
        """
        global command
        command=''
        NewDialog.sname=self.builder.get_object('entry1').get_text()
        #remove existing &amp;
        NewDialog.sname.replace("&amp;", "");

        for n in range(5):            
            app=''
            args=''
            global comboboxes
            combobox = comboboxes[n]
            if(combobox.get_active()!=0): #if a command is selected
                app = self.getAppbyIndex(combobox.get_active())

            else: 
                continue
            
            if(self.builder.get_object('entry'+str(n+2))!=None):
                args=self.builder.get_object('entry'+str(n+2)).get_text() 

            args.replace("&amp;", "");
            app.replace("&amp;", "");
            #Exception for the terminal
            if combobox.get_active() == 12:
                command+=args  +" & "  
            elif combobox.get_active()== 5: #quickly 
                command = "cd "+ str(args)+ " ; quickly edit & quickly design & quickly run"+str(' &')
            else:
                command +=app + args + " & " 
        self.destroy()
            

    def on_btn_cancel_clicked(self, widget, data=None):
        self.destroy()

    def getCommand(self):
        global command
        return command

    def getName(self):
        return NewDialog.sname


if __name__ == "__main__":
    dialog = NewDialog()
    dialog.show()
    Gtk.main()
