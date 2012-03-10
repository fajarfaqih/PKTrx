class fInvestment:
  def __init__(self, formObj, parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    self.FormView = None
    
  def Show(self):
    
    return self.FormContainer.Show()

  def ShowInvestmentEmpClick(self, sender):
    form = self.FormObject
    app = self.FormObject.ClientApplication

    uipInvestee = self.uipInvestee

    # Clear Grid
    self.uipInvestmentEmployee.ClearData()

    # Get Id
    EmployeeId = uipInvestee.GetFieldValue('LEmployee.EmployeeId')
    
    param = app.CreateValues(['EmployeeId', EmployeeId])
    rph = form.CallServerMethod('GetDataInvestmentEmployee',param)
    
    status = rph.FirstRecord

    if status.IsErr : raise 'PERINGATAN', status.ErrMessage
    
    self.SetGridInvestment('uipInvestmentEmployee', rph.packet.InvestmentList)
    
  def ViewDetailInvestmentE(self):
    AccountNo = self.uipInvestmentEmployee.AccountNo
    self.ViewDetailInvestment(AccountNo)

  def ViewDetailInvestmentNE(self):
    AccountNo = self.uipInvestmentNonEmployee.AccountNo
    self.ViewDetailInvestment(AccountNo)
  
  def ViewDetailInvestment(self):
    InvestmentType = self.mpInvestment.ActivePageIndex
    
    if InvestmentType == 0 :
      AccountNo = self.uipInvestmentEmployee.AccountNo
    else :
      AccountNo = self.uipInvestmentNonEmployee.AccountNo
    # end if
    
    if AccountNo in ['',None] :
      self.app.ShowMessage('Data investasi belum dipilih')
      return
    
    if self.FormView == None :
      form = self.app.CreateForm(
          'rekening/fInvestmentView',
          'rekening/fInvestmentView',
           0, None, None)
      self.FormView = form
    else:
      form = self.FormView
    # end if

    form.Show(AccountNo)

  def ShowInvestmentNonEmpClick(self, sender):
    form = self.FormObject
    app = self.FormObject.ClientApplication
    uipInvestee = self.uipInvestee

    # Clear Grid
    self.uipInvestmentNonEmployee.ClearData()

    # Get Id
    InvesteeId = uipInvestee.GetFieldValue('LInvestee.InvesteeId')

    param = app.CreateValues(['InvesteeId', InvesteeId])
    rph = form.CallServerMethod('GetDataInvestmentNonEmployee',param)

    status = rph.FirstRecord

    if status.IsErr : raise 'PERINGATAN', status.ErrMessage

    self.SetGridInvestment('uipInvestmentNonEmployee', rph.packet.InvestmentList)

  def SetGridInvestment(self, uipartName, dsData):
    uipList = self.FormObject.GetUIPartByName(uipartName)
    
    #dsData = rph.packet.InvestmentList

    TotalData = dsData.RecordCount

    i = 0
    while i < TotalData:
      rec = dsData.GetRecord(i)
      uipList.Append()

      uipList.AccountNo = rec.AccountNo
      uipList.AccountName = rec.AccountName
      uipList.Amount = rec.InvestmentAmount
      uipList.Nisbah = rec.InvestmentNisbah
      uipList.OpeningDate = rec.OpeningDate
      uipList.InvestmentCatName = rec.InvestmentCatName
      uipList.TransactionNo = rec.TransactionNo
      
      i += 1
    # end while
    
