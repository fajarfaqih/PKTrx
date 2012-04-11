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

  def GetTransaction(self,EmployeeId, IsRAKReturn = 0):
    self.uipFilter.Edit()
    self.uipFilter.EmployeeId = EmployeeId
    self.uipFilter.IsRAKReturn = IsRAKReturn
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
    
    AddParam = ''
    if self.uipFilter.IsRAKReturn == 1 :
      AddParam += " and ( DistributionTransferId is not null or DistributionTransferId = 0 ) "

    self.form.SetDataFromQuery('uipCATransactItem',
         " \
         LCashAdvanceAccount.EmployeeIdNumber = %d  \
         and LTransaction.ActualDate >= '%s' \
         and LTransaction.ActualDate <= '%s' \
         %s " % ( uipFilter.EmployeeId, sBegin, sEnd, AddParam) ,
         '')
    return

  def GridDoubleClick(self,sender):
    self.ProsesClick(self.pAction_bPilih)
    
  def ProsesClick(self,sender):
    TransactionItemId = self.uipCATransactItem.TransactionItemId or 0
    if TransactionItemId == 0 : return
    
    if self.uipCATransactItem.ReturnStatus == 'T' : raise 'PERINGATAN','Transaksi yang dipilih telah memiliki LPJ'
    
    #if self.uipCATransactItem.AuthStatus == 'F' : raise 'PERINGATAN','Transaksi yang dipilih belum diotorisasi'
    
    if self.uipFilter.IsRAKReturn == 0 and self.uipCATransactItem.DistributionTransferId not in ['',0,None]:
      raise 'PERINGATAN','Transaksi yang dipilih harus diproses melalui LPJ RAK'

    #if IsRAKReturn and self.uipCATransactItem.DistributionTransferId in ['',0,None]:
    #  pass
    
    self.FormObject.Close(1)
