def RevisionClick(sender,context):
  app = context.OwnerForm.ClientApplication
  form = context.OwnerForm
  formname = 'budget/fBudgetRevision'
  BudgetId = form.PyFormObject.GetBudgetId() #form.GetPanelByName('qBudget').GetFieldValue('Budget.BudgetId')
  
  if BudgetId == 0 : return
  ph = app.CreateValues(['BudgetId',BudgetId])

  dlg = app.CreateForm(formname,formname,0,ph,None)
  st = dlg.FormContainer.Show()
  
  if st == 1:
    form.PyFormObject.UpdateAmount(dlg.RevisionAmount)
    
  
  

