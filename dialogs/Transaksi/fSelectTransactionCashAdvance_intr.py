class fSelectTransactionCashAdvance:
  def __init__(self,formObj,parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.TransactionItemId = 0
    self.Amount = 0.0
    self.Description = ''
    self.Tgl = None
    self.TransactionItemId = None
    self.TransactionNo = None
    self.TransactionDate = None
    self.Amount = None
    self.Description = None

  def GetTransaction(self,EmployeeId):
    self.uipFilter.Edit()
    self.uipFilter.EmployeeId = EmployeeId
    self.DisplayTransaction()
    
    st = self.FormContainer.Show()
    if st == 1 :
      return 1

    return 0

  def Show(self):
    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction()

  def DisplayTransaction(self):
    app = self.app
    uipFilter = self.uipFilter
    
    BeginY, BeginM, BeginD = uipFilter.BeginDate[:3]
    EndY, EndM, EndD = uipFilter.EndDate[:3]
    intBeginDate = app.ModDateTime.EncodeDate(BeginY,BeginM,BeginD)
    sBegin = '%s-%s-%s' % (str(BeginM).zfill(2),str(BeginD).zfill(2),str(BeginY))
    intEndDate = app.ModDateTime.EncodeDate(EndY,EndM,EndD)
    sEnd = '%s-%s-%s' % (str(EndM).zfill(2),str(EndD).zfill(2),str(EndY))

    self.form.SetDataFromQuery('uipCATransactItem',
         " \
         LCashAdvanceAccount.EmployeeIdNumber = %d  \
         and LTransaction.TransactionDate >= '%s' \
         and LTransaction.TransactionDate <= '%s' \
         " % (uipFilter.EmployeeId,sBegin,sEnd), '')
    return

  def GridDoubleClick(self,sender):
    self.ProsesClick(self.pAction_bPilih)
    
  def ProsesClick(self,sender):
    TransactionItemId = self.uipCATransactItem.TransactionItemId or 0
    if TransactionItemId == 0 : return
    
    if self.uipCATransactItem.ReturnStatus == 'T' : raise 'PERINGATAN','Transaksi yang dipilih telah memiliki LPJ'
    
    #if self.uipCATransactItem.AuthStatus == 'F' : raise 'PERINGATAN','Transaksi yang dipilih belum diotorisasi'

    self.FormObject.Close(1)
