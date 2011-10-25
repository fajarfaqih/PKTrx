def TambahUserClick(sender, context):
  try:
    app = context.OwnerForm.ClientApplication
    aform = app.GetForm('userman/um01_entry_user', 'entry_user', 0)
    aform.Show()  
  finally:
    aform = None

  return 1

def ActionUser1Click(sender, context):
  dialogname = sender.StringTag
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
  try:
    aform = app.GetFormWithData('userman/' + dialogname, dialogname, 0, key, 'UserApp')
    aform.Show()
  finally:
    aform = None
    app = None
  return 1

def DeleteUserClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    key = context.KeyObjConst
    dlg = app.ConfirmDialog('Anda yakin akan menghapus data ini?')
    if dlg:
      app.DeletePObj(key)

      app.ShowMessage('Penghapusan user berhasil')
      context.DisplayData()
  finally:
    app = None

  return 1

def ClearPasswordClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan menghapus password user ini?')
    if dlg:   
      key = context.KeyObjConst
      datapacket = app.CreateUIDataPacketHolder()
      record = datapacket.packet.CreateSimpleDataPacket()
      record.data = key
      r_result = app.ExecuteScript('S_ClearPassword', datapacket)
      dataset = r_result.packet.GetDataset(0)
      record = dataset.GetRecord(0)
      if record.IsErr:
        raise record.ErrMessage
      app.ShowMessage('Penghapusan password user berhasil.')
  finally:
    app = None

  return 1

def HakAksesMenuClick (sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    datapacket = app.CreateUIDataPacketHolder()

    record = datapacket.packet.CreateSimpleDataPacket()
    record.data = context.GetFieldValue('UserApp.UserID')

    return_datapacket = app.ExecuteScript('SRep_UserMenu', datapacket)
    return_filename = return_datapacket.packet.GetDataset(0).GetRecord(0).data
    app.DownloadItem(return_filename, 'v')
  finally:
    aform = None
    app = None
  
  return 1

def LockUserClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan mengunci login user ini?')
    if dlg:   
      key = context.KeyObjConst
      datapacket = app.CreateUIDataPacketHolder()
      record = datapacket.packet.CreateSimpleDataPacket()
      record.data = key
      r_result = app.ExecuteScript('S_LockLogin', datapacket)
      dataset = r_result.packet.GetDataset(0)
      record = dataset.GetRecord(0)
      if record.IsErr:
        raise record.ErrMessage
      app.ShowMessage('Penguncian login user berhasil.')
  finally:
    app = None

  return 1

def LockAllUserClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan mengunci semua login user?')
    if dlg:   
      datapacket = None
      r_result = app.ExecuteScript('S_LockAllLogin', datapacket)
      dataset = r_result.packet.GetDataset(0)
      record = dataset.GetRecord(0)
      if record.IsErr:
        raise record.ErrMessage
      app.ShowMessage('Penguncian semua login user berhasil.')
  finally:
    app = None

  return 1

def UnLockUserClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan membebaskan kuncian login user ini?')
    if dlg:   
      key = context.KeyObjConst
      datapacket = app.CreateUIDataPacketHolder()
      record = datapacket.packet.CreateSimpleDataPacket()
      record.data = key
      r_result = app.ExecuteScript('S_UnLockLogin', datapacket)
      dataset = r_result.packet.GetDataset(0)
      record = dataset.GetRecord(0)
      if record.IsErr:
        raise record.ErrMessage
      app.ShowMessage('Pembebasan penguncian login user berhasil.')
  finally:
    app = None

  return 1

def UnLockAllUserClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan membebaskan penguncian semua login user?')
    if dlg:   
      datapacket = None
      r_result = app.ExecuteScript('S_UnLockAllLogin', datapacket)
      dataset = r_result.packet.GetDataset(0)
      record = dataset.GetRecord(0)
      if record.IsErr:
        raise record.ErrMessage
      app.ShowMessage('Pembebasan penguncian semua login user berhasil.')
  finally:
    app = None

  return 1
