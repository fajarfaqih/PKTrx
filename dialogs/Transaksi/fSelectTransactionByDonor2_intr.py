class fSelectTransactionByDonor:
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

  def GetTransaction(self,DonorId):
    self.uipFilter.Edit()
    self.uipFilter.DonorId = DonorId
    self.DisplayTransaction()
    
    st = self.FormContainer.Show()
    if st == 1 :
      #qTran = self.form.GetPanelByName('qTransaction')
      #self.TransactionItemId = qTran.GetFieldValue('DonorTransactionItem.TransactionItemId')
      #self.TransactionNo = qTran.GetFieldValue('DonorTransactionItem.TransactionNo')
      #self.TransactionDate = qTran.GetFieldValue('DonorTransactionItem.TransactionDate')
      #self.AccountName = qTran.GetFieldValue('DonorTransactionItem.AccountName')
      #self.Amount = qTran.GetFieldValue('DonorTransactionItem.Amount')
      #self.Description = qTran.GetFieldValue('DonorTransactionItem.Description')
      return 1

    return 0

  def Show(self):
    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction()
    
  def PilihClick(self,sender):
    self.ChangeProsesStatus('P')
       
  def BatalClick(self,sender):
    self.ChangeProsesStatus('T')

  def ChangeProsesStatus(self,value) :
    if self.uipDonorTrans.RecordCount > 0 :
       self.uipDonorTrans.Edit()
       self.uipDonorTrans.stProses = value

  def DisplayTransaction(self):
    app = self.app
    uipFilter = self.uipFilter
    
    BeginY, BeginM, BeginD = uipFilter.BeginDate[:3]
    EndY, EndM, EndD = uipFilter.EndDate[:3]
    intBeginDate = app.ModDateTime.EncodeDate(BeginY,BeginM,BeginD)
    sBegin = '%s-%s-%s' % (str(BeginM).zfill(2),str(BeginD).zfill(2),str(BeginY))
    intEndDate = app.ModDateTime.EncodeDate(EndY,EndM,EndD)
    sEnd = '%s-%s-%s' % (str(EndM).zfill(2),str(EndD).zfill(2),str(EndY))

    self.form.SetDataFromQuery('uipDonorTrans',
         " \
         DonorId = %d  \
         and LTransaction.TransactionDate >= '%s' \
         and LTransaction.TransactionDate <= '%s' \
         and FundEntity = 1 \
         " % (uipFilter.DonorId,sBegin,sEnd), '')
    return
    qTransaction = self.qTransaction
    self.qTransaction.OQLText = "select  from DonorTransactionItem \
             [ DonorId=:DonorId \
               and LTransaction.TransactionDate >= :BeginDate \
               and LTransaction.TransactionDate <= :EndDate \
               and FundEntity = 1 \
             ] \
             ( LTransaction.TransactionId, \
               LTransaction.TransactionNo, \
               LTransaction.TransactionDate, \
               LFinancialAccount.AccountName, \
               LTransaction.Description , \
               TransactionItemId, \
               Amount, \
                self) \
               then order by TransactionNo;"

    uipFilter = self.uipFilter

    BeginY, BeginM, BeginD = uipFilter.BeginDate[:3]
    EndY, EndM, EndD = uipFilter.EndDate[:3]
    intBeginDate = app.ModDateTime.EncodeDate(BeginY,BeginM,BeginD)
    intEndDate = app.ModDateTime.EncodeDate(EndY,EndM,EndD)
    
    self.qTransaction.SetParameter('DonorId', uipFilter.DonorId)
    self.qTransaction.SetParameter('BeginDate', intBeginDate)
    self.qTransaction.SetParameter('EndDate', intEndDate)
    self.qTransaction.DisplayData()


