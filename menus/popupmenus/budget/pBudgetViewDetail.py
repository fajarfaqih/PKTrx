def DetailClick(sender,context):
  app = context.OwnerForm.ClientApplication
  form = context.OwnerForm
  formname = 'budget/fBudgetViewDetail'
  BudgetId = form.PyFormObject.GetBudgetId() #form.GetPanelByName('qBudget').GetFieldValue('Budget.BudgetId')
  
  if BudgetId == 0 : return
  ph = app.CreateValues(['BudgetId',BudgetId])

  dlg = app.CreateForm(formname,formname,0,ph,None)
  dlg.FormContainer.Show()
  
