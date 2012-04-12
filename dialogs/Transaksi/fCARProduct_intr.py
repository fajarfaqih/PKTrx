class fCARProduct:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def GetData(self,editmode=0,data=None):
    uipData = self.uipData
    uipData.Edit()
    if editmode :
      uipData.SetFieldValue('LProductAccount.AccountNo',data.AccountId)
      uipData.SetFieldValue('LProductAccount.AccountName',data.AccountName)
      uipData.Amount = data.Amount
      uipData.Ashnaf = data.Ashnaf
      uipData.FundEntity = data.FundEntity
      uipData.Description = data.Description
      uipData.BudgetCode = data.BudgetCode
      uipData.SetFieldValue('LBudget.BudgetCode',data.BudgetCode)
      uipData.SetFieldValue('LBudget.LOwner.OwnerName',data.BudgetOwner)
    else :
      uipData.SetFieldValue('LProductAccount.AccountNo','')
      uipData.SetFieldValue('LProductAccount.AccountName','')
      uipData.Ashnaf = 'F'
      uipData.FundEntity = 1
      uipData.Amount = 0.0
      uipData.Description = ''
      uipData.BudgetCode = ''
      uipData.SetFieldValue('LBudget.BudgetCode','')
      uipData.SetFieldValue('LBudget.LOwner.OwnerName','')
    # end if

    st = self.FormContainer.Show()
    if st == 1 : return 1
    return 0

  def ProdukAfterLookup(self,sender,linkUI):
    self.uipData.Edit()
    self.uipData.Description = self.uipData.GetFieldValue('LProductAccount.AccountName')

  def CheckInput(self):
    uipData = self.uipData

    self.form.CommitBuffer()
    if uipData.Amount <= 0.0 :
      raise 'PERINGATAN','Nilai Transaksi tidak boleh < 0.0'

    if uipData.FundEntity == 1 and uipData.Ashnaf == 'L' :
      raise 'PERINGATAN', "Untuk Jenis Dana Zakat, pemilihan Ashnaf Tidak Boleh Memilih 'Lainnya' "

    if uipData.FundEntity != 1 :
      uipData.Edit()
      uipData.Ashnaf = 'L'

  def OKClick(self,sender):
    self.CheckInput()
    self.form.CommitBuffer()
    sender.ExitAction = 1
    
