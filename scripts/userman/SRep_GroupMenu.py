import ConfigParser, os, string

def LoadMenuItemsToTblTask (config, amenuitem, TblTask, groupid, modulname, prefix, parent_allowed):
  # add self to dataset

  allowed = 0
  mnucaption = amenuitem.Caption
  allowedgroups = str(amenuitem.AllowedGroups)
  #allowedusers = str(amenuitem.AllowedUsers)
  #if (allowedgroups.strip() == '') and (allowedusers.strip() == '') and ((parent_allowed == 1) or (amenuitem.DenyThenAllow == 0)):
  #  allowed = 1
  #else:
  ls_allowedgroups = allowedgroups.split(';')
  for group_id in ls_allowedgroups:
    if len(group_id) <> 0:
      if group_id == groupid:
        allowed = 1
        break

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
      LoadMenuItemsToTblTask(config, amnuitem, TblTask, groupid, modulname, prefix, allowed)

def DAFScriptMain(config, parameter, returnpacket):
  dataset = parameter.GetDataset(0)
  record = dataset.GetRecord(0)
  group_id = record.data

  homeDir = config.HomeDir

  report_name = homeDir + 'reports\\userman\\daftar_group_menu.htr'
  file_name = 'DaftarHakAksesMenuGroup.html'

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
      LoadMenuItemsToTblTask(config, amenuitem, TblTask, group_id, menucaption, '', 1)

  XMLName = config.UserHomeDirectory + 'DaftarHakAksesMenuGroup.xml'
  TblTask.SaveAsXML(XMLName)   
  
  repholder = config.ModHTMLReport.CreateReportHolder()
  repholder.LoadReport(report_name)
  config.SendDebugMsg('#html report is loaded and prepared')
  htmlreport = repholder.ReportObject
  xmltable = htmlreport.GetDataSource(0)
  xmltable.XMLFileName = XMLName
  htmlreport.PrepareProduce(config.UserHomeDirectory + file_name)

  headingitem = htmlreport.GetItemByName('heading')
  groupobj = config.CreatePObjImplProxy('UserGroup')
  groupobj.key = group_id
  strgroup = group_id + ' - ' + str(groupobj.GroupName)    
  headingitem.GetVariableByName('usergroup').Value = strgroup

  htmlreport.Produce()

  returnpacket.CreateSimpleDataPacket().data = file_name
  return 1
