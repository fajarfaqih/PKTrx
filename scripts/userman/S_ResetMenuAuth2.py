import ConfigParser, os, sys

def ResetMenuitem(config, amenuitem):
  amenuitem.AllowedUsers = ''
  amenuitem.AllowedGroups = ''
  
  n = amenuitem.ItemCount
  for i in range(n):
    amnuitem = amenuitem.GetItem(i)
    ResetMenuitem(config, amnuitem)

def DAFScriptMain(config, parameter, returnpacket):
  IsErr = 0
  ErrMessage = ''
  try:
    cfgparser = ConfigParser.ConfigParser()
    homeDir = config.HomeDir
    cfgparser.readfp(open(homeDir + 'menus\\menulist.ini'))
    mnulist = cfgparser.options('MENULIST')

    mnulist.sort()
    ModRTMenu = config.ModRTMenu
    for mnuoption in mnulist:
      mnufilename = cfgparser.get('MENULIST', mnuoption)
      
      mnuholder = ModRTMenu.CreateMenuHolder()
      # load menu from file name
      mnuholder.LoadMenu(homeDir + 'menus\\' + mnufilename)
      mnuobject = mnuholder.menuobject

      # load items
      n = mnuobject.ItemCount
      for i in range(n):
        amenuitem = mnuobject.GetItem(i)
        ResetMenuitem(config, amenuitem)
      mnuobject.DenyThenAllow = 1
      mnuholder.SaveMenu()
      mnuholder = None
  except:
    IsErr = 1
    ErrMessage = str(sys.exc_info()[1])

  result_def = 'IsErr: integer; ErrMessage: string'
  record = returnpacket.CreateDataPacketStructure(result_def)
  record.IsErr = IsErr
  record.ErrMessage = 'Server side error : ' + ErrMessage

  return 1
