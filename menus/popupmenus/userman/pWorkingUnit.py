def mnuNewClick(sender, context):
  app = context.OwnerForm.ClientApplication
  basicDlgName = context.Name[3:]
  formname = 'userman/' + basicDlgName + '_new'
  form = app.GetForm(formname, formname, 0)
  form.Show()
  return 1

def mnuEditClick(sender, context):
  app = context.OwnerForm.ClientApplication
  basicDlgName = context.Name[3:]
  formname = 'userman/' + basicDlgName + '_edit'
  form = app.GetFormWithData(formname, formname, 0, context.KeyObjConst, 'uipart')
  form.Show()
  return 1

def mnuViewClick(sender, context):
  app = context.OwnerForm.ClientApplication
  basicDlgName = context.Name[3:]
  formname = 'userman/' + basicDlgName + '_view'
  form = app.GetFormWithData(formname, formname, 0, context.KeyObjConst, 'uipart')
  form.Show()
  return 1

def mnuDeleteClick(sender, context):
  app = context.OwnerForm.ClientApplication
  if (app.ConfirmDialog('Hapus data ?')):
    app.DeletePObj(context.KeyObjConst)
    context.DeleteRow()
  return 1


