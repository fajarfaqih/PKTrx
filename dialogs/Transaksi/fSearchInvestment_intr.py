class fSearchInvestment:
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    
  def ShowData(self):
    self.GetDataInvestmentNE()
    self.GetDataInvestmentE()
    st = self.FormContainer.Show()
    if st == 1:
      return 1
    else:
      return 0

  def GridDoubleClick(self,sender):
    self.bSelectClick(self.pAction_bSelect)
    
  def bSelectClick(self,sender):
    sender.ExitAction = 1

  def bFilterClick(self,sender):
    self.GetDataInvestmentNE()

  def bFilterEClick(self,sender):
    self.GetDataInvestmentE()

  def NameOnExit(self,sender):
    Nama = self.uipFilter.Nama or ''
    if Nama == '': return
    self.GetDataManager(Nama)
    
  def GetDataInvestmentNE(self):
    app = self.app
    uipFilter = self.uipFilter

    lsParam = []

    Name = uipFilter.InvesteeName or ''
    if Name != '' :
      lsParam.append(" LInvestee.InvesteeName LLIKE '%s' " % (Name))

    strParam = ' and '.join(lsParam)

    self.form.SetDataFromQuery('uipInvestmentNE',strParam, '')

  def GetDataInvestmentE(self):
    app = self.app
    uipFilter = self.uipFilter

    lsParam = []

    Name = uipFilter.EmployeeName or ''
    if Name != '' :
      lsParam.append(" LEmployee.EmployeeName LLIKE '%s' " % (Name))

    strParam = ' and '.join(lsParam)

    self.form.SetDataFromQuery('uipInvestmentE',strParam, '')
