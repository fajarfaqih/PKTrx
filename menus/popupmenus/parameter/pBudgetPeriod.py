def NewClick(sender,context):
  app = context.OwnerForm.ClientApplication
  formname = 'parameter/fBudgetPeriodNew'
  dlg = app.CreateForm(formname,formname,0,None,None)
  dlg.FormContainer.Show()

def DeleteClick(sender,context):
  app = context.OwnerForm.ClientApplication
  key = context.KeyObjConst
  
  resp = app.ExecuteScript('Parameter/DeleteBudgetPeriod',app.CreateValues(['key',key]))
  
  status = resp.FirstRecord
  if status.Is_Err :
     raise 'PERINGATAN',status.Err_Message

  app.ShowMessage('Data Budget Period berhasil di hapus')

  queryform = app.FindForm('parameter/fDaftarBudgetPeriod')
  query = queryform.FormObject.GetPanelByName('qBudgetPeriod')
  query.DeleteRow()
