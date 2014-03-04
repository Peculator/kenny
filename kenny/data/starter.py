#!/usr/bin/env python
import gtk,pynotify, appindicator,commands,sys
import xml.dom.minidom as dom
import os

class starter:
   
    def quit(Event):
      sys.exit (1)

    def showNotify(Event,args):
      try:
          pynotify.init('  ---- kenny ----  ')
          n = pynotify.Notification(' ---- kenny ---- '," "+args+" started","/opt/extras.ubuntu.com/kenny/share/kenny/media/kenny_filled.svg")
          n.show()
      except:
          pass
    
    def runScript(Event,args):
      os.system(args)
    
    def startKenny(Event):
      os.system("/opt/extras.ubuntu.com/kenny/bin/kenny");
      

     #	---------------       Main		-------------------
    if __name__ == "__main__":

      ind = appindicator.Indicator ("Kenny","/opt/extras.ubuntu.com/kenny/share/kenny/media/kenny.svg", appindicator.CATEGORY_APPLICATION_STATUS);ind.set_status (appindicator.STATUS_ACTIVE)
     
      # create a menu
      menu = gtk.Menu()
      
      menu_header = gtk.MenuItem("---- kenny ----");menu.append(menu_header);menu_header.show()             
      menu_header.connect("activate", startKenny);
      global d
      d = {} 
    
      tree = dom.parse(os.getenv("HOME")+'/.kenny/'+'kenny_data.xml')

      for script in tree.firstChild.childNodes: 
          if script.nodeName == "script": 
              name = value = ""

              for node in script.childNodes: 
                  if node.nodeName == "name" and node.firstChild != None: 
                    name = node.firstChild.data.strip() 
                  elif node.nodeName == "value" and node.firstChild != None: 
                    value = node.firstChild.data.strip() 

              d[name] = value
              print value

      for i in d:
        script = gtk.MenuItem(i);
        script.connect("activate", runScript,d[i]);
        menu.insert(script,1);
        script.show()
        script.connect("activate", showNotify,i);

    seperator = gtk.SeparatorMenuItem();menu.append(seperator);seperator.show();
    image = gtk.ImageMenuItem(gtk.STOCK_QUIT);image.connect("activate", quit);image.show();menu.append(image)
    ind.set_menu(menu);
    gtk.main()
