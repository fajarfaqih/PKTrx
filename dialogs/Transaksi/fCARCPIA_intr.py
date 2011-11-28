KodeTransaksi = ['KK','KM']

class fCARCPIA :
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.fSearchBudget = None
    
  def GetData(self ,editmode=0,data=None):
    uipData = self.uipData
    uipData.Edit()
    if editmode :
      uipData.SetFieldValue('LCPIACategory.CPIACatCode',data.CPIACatCode)
      uipData.SetFieldValue('LCPIACategory.CPIACatName',data.CPIACatName)
      uipData.SetFieldValue('LCPIACategory.CPIACatId',data.CPIACatId)
      uipData.SetFieldValue('LCostAccount.Account_Code',data.AccountId)
      uipData.SetFieldValue('LCostAccount.Account_Name',data.AccountName)

      uipData.Amount = data.Amount
      uipData.Description = data.Description
      uipData.HasContract = data.CPIAHasContract
      uipData.ContractEndDate = data.CPIAContractEndDate
      uipData.ContractNo = data.CPIAContractNo
      uipData.BudgetCode = data.BudgetCode
      uipData.BudgetOwner = data.BudgetOwner

    else :
      uipData.SetFieldValue('LCPIACategory.CPIACatCode', '')
      uipData.SetFieldValue('LCPIACategory.CPIACatName', '')
      uipData.SetFieldValue('LCPIACategory.CPIACatId', 0)
      uipData.SetFieldValue('LCostAccount.Account_Code', '')
      uipData.SetFieldValue('LCostAccount.Account_Name', '')
      
      uipData.Amount = 0.0
      uipData.Description = ''
      uipData.ContractEndDate = 0
      uipData.HasContract = 'F'
      uipData.ContractNo = ''
      uipData.BudgetCode = ''
      uipData.BudgetOwner = ''
    # end if

    st = self.FormContainer.Show()
    if st == 1 : return 1
    return 0

  def bBudgetClick(self,sender):
    uipData = self.uipData
    if self.fSearchBudget == None:
      #formname = 'Transaksi/fSelectBudgetYear'
      formname = 'Transaksi/fSelectBudgetCode'
      form = self.app.CreateForm(formname,formname,0,None,None)
      self.fSearchBudget = form
    else:
      form = self.fSearchBudget
    # end if

    BranchCode = uipData.BranchCode
    PeriodId = uipData.PeriodId
    if form.GetBudget(PeriodId) == 1:
      uipData.Edit()
      uipData.BudgetCode = form.BudgetCode
      uipData.BudgetOwner = form.BudgetOwner
      uipData.BudgetId = form.BudgetId
    # end if
