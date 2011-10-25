class fCARGL:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication

  def GetData(self,editmode=0,data=None):
    uipData = self.uipData

    uipData.Edit()
    if editmode:
      uipData.SetFieldValue('LLedger.Account_Code',data.AccountId)
      uipData.SetFieldValue('LLedger.Account_Name',data.AccountName)
      uipData.Amount = data.Amount
      uipData.Description = data.Description
      #uipData.BudgetCode = data.BudgetCode
      uipData.SetFieldValue('LBudget.BudgetCode',data.BudgetCode)
      uipData.SetFieldValue('LBudget.LOwner.OwnerName',data.BudgetOwner)
    else:
      uipData.SetFieldValue('LLedger.Account_Code','')
      uipData.SetFieldValue('LLedger.Account_Name','')
      uipData.Amount = 0.0
      uipData.Description = ''
      uipData.BudgetCode = ''
      uipData.SetFieldValue('LBudget.BudgetCode','')
      uipData.SetFieldValue('LBudget.LOwner.OwnerName','')
    # end if
    
    st = self.FormContainer.Show()
    if st == 1 : return 1

    return 0

  def GLAfterLookup(self,sender,linkUI):
    self.uipData.Edit()
    self.uipData.Description = self.uipData.GetFieldValue('LLedger.Account_Name')
    
  def CheckInput(self):
    uipData = self.uipData
    if uipData.Amount <= 0.0 :
      raise 'PERINGATAN','Nilai Transaksi tidak boleh < 0.0'

  def OKClick(self,sender):
    self.CheckInput()
    self.form.CommitBuffer()
    sender.ExitAction = 1
    
