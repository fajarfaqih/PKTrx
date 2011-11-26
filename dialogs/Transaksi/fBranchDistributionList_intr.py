class fBranchDistributionList:
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
    self.fReturnTrans = None
    self.fCADetail = None

  def GetTransaction(self,BranchCode):
    self.uipFilter.Edit()
    self.DisplayTransaction()
    
    st = self.FormContainer.Show()
    if st == 1 :
      return 1

    return 0

  def Show(self):
    uipFilter = self.uipFilter
    uipFilter.Edit()
    uipFilter.IsReportedShow = 'F'

    IsHeadOffice = (uipFilter.BranchCode == uipFilter.HeadOfficeCode)
    self.MasterBranchCode = ''
    if not IsHeadOffice :
      uipFilter.MasterBranchCode = uipFilter.BranchCode

    self.DisplayTransaction()
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction()

  def CreateReturnTransactionClick(self,sender):
    app = self.app
    form = self.form
    
    TransactionNo = self.uipDistributionList.TransactionNo or ''
    
    if TransactionNo == '' : return
    
    if self.fReturnTrans == None :
      form = app.CreateForm('Transaksi/fBranchDistributionReturn',
                            'Transaksi/fBranchDistributionReturn',
                            0,None,None)
      self.fReturnTrans = form
    else:
      form = self.fReturnTrans
    # end if
    
    if form.CreateReturnTrans(TransactionNo):
      pass
    # end if
    
  def DetilUMClick(self,sender):
    DistributionId = self.uipDistributionList.DistributionId or 0
    
    if DistributionId == 0 : return
    
    if self.fCADetail == None :
      form = self.app.CreateForm('Transaksi/fDistCADetail',
                            'Transaksi/fDistCADetail',
                            0,None,None)
      self.fCADetail = form
    else:
      form = self.fCADetail
    # end if


    form.ShowDetail(DistributionId)


  def DisplayTransaction(self):
    app = self.app
    uipFilter = self.uipFilter
    
    SourceBranchCode = self.uipFilter.GetFieldValue('LSourceBranch.BranchCode') or ''
    DestBranchCode = self.uipFilter.GetFieldValue('LDestBranch.BranchCode') or ''
    IsReportedShow = self.uipFilter.IsReportedShow
    ph = app.CreateValues(
      ['BeginDate',uipFilter.BeginDate],
      ['EndDate',uipFilter.EndDate],
      ['SourceBranchCode',SourceBranchCode],
      ['DestBranchCode',DestBranchCode],
      ['IsReportedShow',IsReportedShow]
    )
    
    self.form.SetDataWithParameters(ph)
    
    """
    BeginY, BeginM, BeginD = uipFilter.BeginDate[:3]
    EndY, EndM, EndD = uipFilter.EndDate[:3]
    intBeginDate = app.ModDateTime.EncodeDate(BeginY,BeginM,BeginD)
    sBegin = '%s-%s-%s' % (str(BeginM).zfill(2),str(BeginD).zfill(2),str(BeginY))
    intEndDate = app.ModDateTime.EncodeDate(EndY,EndM,EndD)
    sEnd = '%s-%s-%s' % (str(EndM).zfill(2),str(EndD).zfill(2),str(EndY))

    self.form.SetDataFromQuery('uipCATransactItem',
         " \
         LTransaction.BranchCode = '%s'  \
         and LTransaction.TransactionDate >= '%s' \
         and LTransaction.TransactionDate <= '%s' \
         and MutationType = 'D' \
         and LTransaction.TransactionCode = 'DT'  \
         " % (uipFilter.BranchCode,sBegin,sEnd), '')

    return"""

  def DisplayInfoList(self):
    qDistTransferInfo = self.qDistributionTransferInfo

    sOQL = " \
      select from DistributionTransferInfo \
       [LTransaction.BranchCode = :BranchCode and \
        LTransaction.ActualDate >= :BeginDate and \
        LTransaction.ActualDate <= :EndDate ] \
      (LTransaction.ActualDate, \
       LTransaction.LBranchDestination.BranchName , \
       LTransaction.Amount , \
       LTransaction.TransactionNo, \
       LTransaction.Description, \
       self) \
       then order by ActualDate ; \
     "

    
  def GridDoubleClick(self,sender):
    self.ProsesClick(self.pAction_bPilih)
    
  def ProsesClick(self,sender):
    self.FormObject.Close(1)
