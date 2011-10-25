def TambahUserGroupClick(sender, context):
  try:
    app = context.OwnerForm.ClientApplication
    aform = app.GetForm('userman/um07_entry_usergroup', 'UserGroup', 0)
    aform.Show()  
  finally:
    aform = None

  return 1

def KoreksiUserGroupClick(sender, context):
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
  try:
    aform = app.GetFormWithData('userman/um08_edit_usergroup', 'UserGroup', 0, key, 'UserGroup')
    aform.Show()
  finally:
    aform = None
    app = None
  return 1

def DeleteUserGroupClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan menghapus data ini?')
    if dlg:   
      key = context.KeyObjConst
      app.DeletePObj(key)

      app.ShowMessage('Penghapusan user group berhasil')
      context.DisplayData()
  finally:
    app = None

  return 1

def LihatUserGroupClick(sender, context):
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
  try:
    aform = app.GetFormWithData('userman/um09_view_usergroup', 'UserGroup', 0, key, 'UserGroup')
    aform.Show()
  finally:
    aform = None
    app = None
  return 1

def HakAksesMenuClick (sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    datapacket = app.CreateUIDataPacketHolder()

    record = datapacket.packet.CreateSimpleDataPacket()
    record.data = context.GetFieldValue('UserGroup.group_id')

    return_datapacket = app.ExecuteScript('SRep_GroupMenu', datapacket)
    return_filename = return_datapacket.packet.GetDataset(0).GetRecord(0).data
    app.DownloadItem(return_filename, 'v')
  finally:
    aform = None
    app = None
