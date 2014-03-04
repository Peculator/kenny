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

import gettext
from gettext import gettext as _
gettext.textdomain('kenny')

from gi.repository import Gio,Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('kenny')

from kenny_lib import Window
from kenny.AboutKennyDialog import AboutKennyDialog
from kenny.PreferencesKennyDialog import PreferencesKennyDialog
from kenny.NewDialog import NewDialog

from xml.dom.minidom import Document
import os
import shutil
import xml.dom.minidom as dom

# See kenny_lib.Window.py for more details about how this class works
class KennyWindow(Window):
    __gtype_name__ = "KennyWindow"


    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(KennyWindow, self).finish_initializing(builder)
        self.AboutDialog = AboutKennyDialog
        self.PreferencesDialog = PreferencesKennyDialog

        # Code for other initialization actions should be added here.

        #setting management
        self.settings = Gio.Settings("net.launchpad.kenny")
        self.language = self.settings.get_int("language") # refreshing of the language 
        #set english as default language

        switch = builder.get_object("switch3")
        value = self.settings.get_int("export-unity")
        switch.set_active(value) 

        switch = builder.get_object("switch1")
        value = self.settings.get_int("export-indicator")
        switch.set_active(value)

        #set default settings

        toolbar = builder.get_object("toolbar1")
        context = toolbar.get_style_context()
        context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        #Show the existing scripts in a new treeview

        self.treeview = Gtk.TreeView()
        self.liststore = Gtk.ListStore(str, str)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.treeview.set_model(self.liststore)

        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        
        builder.get_object("vbox1").add(self.treeview)

        #test if personal .kenny folder existsts        
        self.path_dir = os.getenv("HOME")+'/.kenny/'
        if not os.path.exists(self.path_dir):
            os.makedirs(self.path_dir)
            print("directiory created")
            #copy starter file
            shutil.copy2('/opt/extras.ubuntu.com/kenny/share/kenny/starter.py', self.path_dir+'starter.py')

        self.__fill_liststore()
        self.__create_columns()

        self.show_all()

    def __fill_liststore(self):

       path_xml = os.getenv("HOME")+'/.kenny/kenny_data.xml'
       if not os.path.exists(path_xml):
        return

       tree = dom.parse(os.getenv("HOME")+'/.kenny/'+'kenny_data.xml')

       for script in tree.firstChild.childNodes: 
          if script.nodeName == "script": 
              name = value = ""

              for node in script.childNodes: 
                 if node.nodeName == "name" and node.firstChild != None: 
                    name = node.firstChild.data.strip() 
                 elif node.nodeName == "value" and node.firstChild != None: 
                    value = node.firstChild.data.strip() 
              iter = self.liststore.append([name,value])
        
       for row in self.liststore:
    # Print values of all columns
            print row[:]
    
    def on_tree_selection_changed(self,selection):
        self.model, treeiter = selection.get_selected()
        self.iter =treeiter


    def __create_columns(self):
        cell = Gtk.CellRendererText()
        
        column = Gtk.TreeViewColumn("Name",cell,text=0)#the current column
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn("Script",cell,text=1)
        self.treeview.append_column(column)         

    def on_switch3_notify(self,widget,data=None):
        self.settings = Gio.Settings("net.launchpad.kenny")
        self.settings.set_int("export-unity",widget.get_active())    

    def on_switch1_notify(self,widget,data=None):
        self.settings = Gio.Settings("net.launchpad.kenny")
        self.settings.set_int("export-indicator",widget.get_active())  

    def on_toolbutton5_clicked(self,widget,data=None):#delete
        print "delete"
        #actually delete it from the liststore, if something is selected
        try:
            self.liststore.remove(self.iter)
        except AttributeError:
            pass
        

    def on_mnu_new_activate(self,builder,data=None):
        print("new")
        newD = NewDialog()
        result = newD.run()

        if result != Gtk.ResponseType.OK:
            print ("abort")
            newD.destroy()
            return
        else:
            print ("ok")
            print(newD.getCommand())
            self.liststore.append([newD.getName(),newD.getCommand()])
        newD.destroy()

    def on_mnu_preferences_activate(self,builder,data=None):# settings
        preferencesD = PreferencesKennyDialog()
        result = preferencesD.run()

        if result != Gtk.ResponseType.OK:
            print ("abort")
            preferencesD.destroy()
            return
        else:
            print ("ok")
            print (self.settings.get_int("language"))
        preferencesD.destroy()

    def on_toolbutton4_clicked(self,builder,data=None): #Apply
        print ("apply")

        if(len(self.liststore) == 0):
            print("nix")
            return

        self.settings = Gio.Settings("net.launchpad.kenny")

        ind_command = "python %s &" %(self.path_dir+'starter.py')

        widget = self.builder.get_object('switch3')#Unity
        widget2 = self.builder.get_object('switch1')#Applicator

        # Write autostart file
        f = open(os.getenv("HOME")+'/.config/autostart/kenny.desktop', 'w')
        f.write ("#!/usr/bin/env xdg-open\n[Desktop Entry]\nEncoding=UTF-8\nType=Application\n"+
                "GenericName=kenny\nComment=Manage your scripts integrated in Unity\nStartupNotify=true\n"+
                "Terminal=false\nName=kenny\nExec=")

        if(widget2.get_active()==1):#Indicator-Export is on
            f.write(ind_command)

        f.write( "\nIcon=")
        f.write("/opt/extras.ubuntu.com/kenny/share/kenny/media/kenny_filled.svg")
        f.write("\nCategories=Application;GNOME;GTK;Utility;\n"+
                "TargetEnvironment=Unity")
        f.close()
        

        if widget.get_active()==1: #on
            f = open(os.getenv("HOME")+'/.local/share/applications/kenny.desktop', 'w')
            f.write ("[Desktop Entry]\nEncoding=UTF-8\nType=Application\n"+
                    "GenericName=kenny\nComment=Manage your scripts integrated in Unity\nStartupNotify=true\n"+
                    "Terminal=false\nName=kenny\nExec=")
            f.write("/opt/extras.ubuntu.com/kenny/bin/kenny" + "\nTargetEnvironment=Unity\nIcon=")
            f.write("/opt/extras.ubuntu.com/kenny/share/kenny/media/kenny_filled.svg")           
            f.write("\nCategories=Application;GNOME;GTK;Utility;\nX-Ayatana-Desktop-Shortcuts=");
            for k in self.liststore:
                f.write(str(k[0]).replace(" ","_")+';')

            for k in self.liststore:
                f.write("\n\n["+ str(k[0]).replace(" ","_")+" Shortcut Group]\n")
                f.write("Name = "+ str(k[0]).replace("_"," ")+"\n")
                f.write('Exec = gnome-terminal -e "bash -c \'' + str(k[1]).replace("&",";") + ' exec bash\'"exit\n')
                f.write("OnlyShowIn=GNOME;Unity;")

            f.close()

        if widget2.get_active()==1: #on
            print ("on2")
            #Write XML

            # Create the minidom document
            doc = Document()

            # Create the <wml> base element
            root = doc.createElement("kenny")
            doc.appendChild(root)


            for k in self.liststore:
                # Create the main <script> element
                maincard = doc.createElement("script")
                
                root.appendChild(maincard)
                # Create a name element
                paragraph1 = doc.createElement("name")
                maincard.appendChild(paragraph1)

                # Give the name elemenet some text
                ptext = doc.createTextNode(k[0])
                paragraph1.appendChild(ptext)

                # Create a value element
                paragraph2 = doc.createElement("value")
                maincard.appendChild(paragraph2)

                # Give the value elemenet some text
                ptext = doc.createTextNode(k[1])
                paragraph2.appendChild(ptext)

            # Print our newly created XML
            print doc.toprettyxml(indent="  ")
            #and store it
            f = open(self.path_dir+'kenny_data.xml', "w") 
            doc.writexml(f, "", "\t", "\n") 
            f.close()
            #kill previous indicator
            os.system('killall python '+ os.getenv("HOME")+'/.kenny/starter.py')
            #run script
            os.system('python %s &' %(self.path_dir+'starter.py'))
                
class Script():

    def get_script(self):
        return self.script

    def __init__(self,name=0):
        self.name = name
        self.settings = Gio.Settings("net.launchpad.kenny")
        self.script = self.settings.get_string("script"+str(name))


