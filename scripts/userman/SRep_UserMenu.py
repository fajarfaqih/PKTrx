import ConfigParser, os, string

def IsAllowedUser(userid, allowedusers):  
  if userid == 'root':
    return 1
  
  ls_allowedusers = allowedusers.split(';')
  for user_id in ls_allowedusers:
    if len(user_id) <> 0:
      if user_id == userid:
        return 1

  return 0

def IsAllowedGroups(config, userid, allowedgroups):
  allowed = 0

  if userid == 'root':
    return 1
  
  userapp = config.CreatePObjImplProxy('UserApp')
  userapp.Key = userid
  ls_usergroup = userapp.Ls_UserGroupApp
  ls_usergroup.First()
  while (not ls_usergroup.EndofList) and (allowed == 0):
    groupid = ls_usergroup.CurrentElement.group_id
    allowed = IsAllowedUser(groupid, allowedgroups)

    ls_usergroup.Next()

  return allowed

def LoadMenuItemsToTblTask (config, amenuitem, TblTask, userid, modulname, prefix, parent_allowed):
  # add self to dataset

  mnucaption = amenuitem.Caption
  allowedusers = str(amenuitem.AllowedUsers)
  allowedgroups = str(amenuitem.AllowedGroups)

  if (IsAllowedUser(userid, allowedusers) == 1) or (IsAllowedGroups(config, userid, allowedgroups) == 1):
    allowed = 1
  else:
    allowed = 0
    
  menuname = prefix + string.replace(mnucaption, '&', '')
  if (allowed == 1) and (mnucaption.strip() <> '-'):
    TblTask.Append()
    TblTask.SetField('modul_name', modulname)
    TblTask.SetField('menu_name', menuname)
    TblTask.Post()

  if allowed:  
    n = amenuitem.ItemCount
    prefix = menuname + '>>'
    for i in range(n):
      amnuitem = amenuitem.GetItem(i)
      LoadMenuItemsToTblTask(config, amnuitem, TblTask, userid, modulname, prefix, allowed)

def DAFScriptMain(config, parameter, returnpacket):
  dataset = parameter.GetDataset(0)
  record = dataset.GetRecord(0)
  user_id = record.data

  homeDir = config.HomeDir
  report_name = homeDir + 'reports\\userman\\daftar_user_menu.htr'
  file_name = 'DaftarHakAksesMenuUser.html'

  TblTask = config.CreateTemporaryTable()
  TblTask.ClearFieldDefs
  TblTask.AddFieldDef('modul_name','string',100)
  TblTask.AddFieldDef('menu_name','string',250)
  TblTask.Active = 1  

  cfgparser = ConfigParser.ConfigParser()
  cfgparser.readfp(open(homeDir + 'menus\\menulist.ini'))
  mnulist = cfgparser.options('MENULIST')

  mnulist.sort()
  mnuholder = config.ModRTMenu.CreateMenuHolder()
  for mnuoption in mnulist:
    menucaption = string.replace(mnuoption, '_', ' ')
    menucaption = string.replace(menucaption, '-', '>>')
    menucaption = string.upper(menucaption)
    mnufilename = cfgparser.get('MENULIST', mnuoption)

    # load menu from file name
    mnuholder.LoadMenu(homeDir + 'menus\\' + mnufilename)
    mnuobject = mnuholder.menuobject

    # load items
    n = mnuobject.ItemCount
    for i in range(n):
      amenuitem = mnuobject.GetItem(i)
      LoadMenuItemsToTblTask(config, amenuitem, TblTask, user_id, menucaption, '', 1)

  XMLName = config.UserHomeDirectory + 'DaftarHakAksesMenuUser.xml'
  TblTask.SaveAsXML(XMLName)   
  
  repholder = config.ModHTMLReport.CreateReportHolder()
  repholder.LoadReport(report_name)
  config.SendDebugMsg('#html report is loaded and prepared')
  htmlreport = repholder.ReportObject
  xmltable = htmlreport.GetDataSource(0)
  xmltable.XMLFileName = XMLName
  htmlreport.PrepareProduce(config.UserHomeDirectory + file_name)

  headingitem = htmlreport.GetItemByName('heading')
  if user_id == 'root':
    struser = user_id
  else:
    userobj = config.CreatePObjImplProxy('UserApp')
    userobj.key = user_id
    struser = user_id + ' - ' + str(userobj.UserName)    
  headingitem.GetVariableByName('userapp').Value = struser

  htmlreport.Produce()

  returnpacket.CreateSimpleDataPacket().data = file_name
  return 1
