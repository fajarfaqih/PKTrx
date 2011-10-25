def ViewClick(sender, context):
  try:
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    aform = app.GetFormWithData('userman/fa06a_branch_view', 'fa06a', 0, key, 'BranchLocation')

    aform.Show()
  finally:
    app = None
    aform = None

def CreateClick(sender, context):
  try:
    app = context.OwnerForm.ClientApplication
    aform = app.GetForm('userman/fa06b_branch_new', 'fa06b_branch_new', 0)
    aform.Show()
  finally:
    app = None
    aform = None

def EditClick(sender, context):
  try:
    app = context.OwnerForm.ClientApplication
    key = context.KeyObjConst
    aform = app.GetFormWithData('userman/fa06c_branch_edit', 'fa06c', 0, key, 'BranchLocation')
    aform.Show()
  finally:
    app = None
    aform = None

def DeleteClick(sender, context):
  app = context.OwnerForm.ClientApplication
  try:
    dlg = app.ConfirmDialog('Anda yakin akan menghapus data ini?')
    if dlg:
      key = context.KeyObjConst
      app.DeletePObj(key)
      app.ShowMessage('Data was succesfully deleted')    
      context.DeleteRow()
  finally:
    app = None
    
  return 1
