import ConfigParser, os

def GetMenuItem (config, amenu, indexes):
  # return menu item at position marked by indexes
  n = len(indexes)
  if len(indexes) == 0:
    return None
  currentitem = amenu.GetItem(int(indexes[0]) - 1)

  for i in range(1, n):
    currentitem = currentitem.GetItem(int(indexes[i]) - 1)

  return currentitem
 
def DAFScriptMain (config, parameter, returnpacket):
  # print out
  dataset = parameter.GetDataset(0)
  id_dataset = parameter.GetDataset(1)
  menu_id = id_dataset.GetRecord(0).menu_id

  cfgparser = ConfigParser.ConfigParser()
  homeDir = config.homeDir
  cfgparser.readfp(open(homeDir + 'menus\\menulist.ini'))
  mnufilename = cfgparser.get('MENULIST', menu_id)

  # load menu from file name
  mnuholder = config.ModRTMenu.CreateMenuHolder()
  mnuholder.LoadMenu(homeDir + 'menus\\' + mnufilename)
  mnuobject = mnuholder.menuobject

  n = dataset.RecordCount
  for i in range(n):
    recitem = dataset.GetRecord(i)
    ds_users = recitem.allowedusers
    ds_groups = recitem.allowedgroups

    strusers = ''
    for j in range(ds_users.RecordCount):
      user_id = ds_users.GetRecord(j).GetFieldByName('user.user_id')
      if j == 0:
        strusers = user_id
      else:
        strusers = strusers + ';' + user_id

    strgroups = ''
    for j in range(ds_groups.RecordCount):
      group_id = ds_groups.GetRecord(j).GetFieldByName('group.group_id')
      if j == 0:
        strgroups = group_id
      else:
        strgroups = strgroups + ';' + group_id

    mnuindexes = recitem.item_number.split('.')
    mnuitem = GetMenuItem(config, mnuobject, mnuindexes)
    mnuitem.AllowedUsers = strusers
    mnuitem.AllowedGroups = strgroups

  mnuholder.SaveMenu()
  
  return 1
