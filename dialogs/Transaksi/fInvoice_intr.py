class fInvoice:
  def __init__(self, formObj, parentForm) :
    self.app = formObj.ClientApplication
    self.form = formObj
    self.fSelectDonor = None
    self.fSelectProgram = None
    self.Inputer = None
    self.BranchCode = None

  def InitValues(self):
    uipInvoice = self.uipInvoice
    if self.Inputer != None :
      uipInvoice.ClearData()
      uipInvoice.Edit()
      uipInvoice.Inputer = self.Inputer
      uipInvoice.BranchCode = self.BranchCode
    else:
      self.Inputer = uipInvoice.Inputer
      self.BranchCode = uipInvoice.BranchCode
    # end if
    
  def Show(self,InvoiceId=0):
    self.InitValues()

    if InvoiceId == 0 :
      ShowMode = 1
    else:
      ShowMode = 2
    # end if
    
    ph = self.app.CreateValues(
      ['ShowMode', ShowMode],
      ['InvoiceId', InvoiceId],
    )
    self.form.SetDataWithParameters(ph)

    st = self.FormContainer.Show()
    if st == 1 :
      return 1
    else:
      return 0
    
    
  def CreateInvoice(self,TransactionItemId):
    self.uipInvoice.ClearData()

    ph = self.app.CreateValues(
      ['TransactionItemId', TransactionItemId],
    )
    self.form.SetDataWithParameters(ph)

    st = self.FormContainer.Show()
    if st == 1 :
      uipInvoice = self.uipInvoice
      self.InvoiceDate = uipInvoice.InvoiceDate
      self.InvoiceNo = uipInvoice.InvoiceNo
      return 1
    else:
      return 0


  def CariSponsorClick(self,sender):
    if self.fSelectDonor == None:
      fData = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSelectDonor = fData
    else:
      fData = self.fSelectDonor

    if fData.GetDonorData() == 1:
      uipInvoice = self.uipInvoice
      uipInvoice.Edit()
      uipInvoice.SponsorId = fData.DonorIntId
      uipInvoice.SponsorNo = fData.DonorId
      uipInvoice.SponsorName = fData.DonorName
      uipInvoice.SponsorAddress = fData.Address
    # end if
    
  def SelectProjectClick(self,sender):
    if self.fSelectProgram == None:
      fData = self.app.CreateForm('Transaksi/fSelectProductInvoice', 'Transaksi/fSelectProductInvoice', 0, None, None)
      self.fSelectProgram = fData
    else:
      fData = self.fSelectProgram
    # end if

    uipInvoice = self.uipInvoice
    BranchCode = uipInvoice.BranchCode
    SponsorId = uipInvoice.SponsorId
    if fData.GetProgram(BranchCode,SponsorId) == 1:
      if fData.mpProduct.ActivePageIndex == 0 :
        AccountNo = fData.uipFilter.GetFieldValue('LProject.LProjectAccount.AccountNo')
        ProductName = fData.uipFilter.GetFieldValue('LProject.LProjectAccount.AccountName')
        CurrencyCode = fData.uipFilter.GetFieldValue('LProject.LProjectAccount.CurrencyCode')
        CurrencyName = fData.uipFilter.GetFieldValue('LProject.LProjectAccount.LCurrency.Short_Name')
        ProductType = 'J'
        Amount = fData.uipProjectDisbursement.DisbAmountPlan
        DisbId = fData.uipProjectDisbursement.DisbId
        #self.pInvoice_Amount.ReadOnly = 1
        #self.pInvoice_Amount.Color= -2147483624
        self.pInvoice_Amount.ReadOnly = 0
        self.pInvoice_Amount.Color=16777215
        
      else:
        AccountNo = fData.qProgram.GetFieldValue('VProduct.AccountNo')
        ProductName = fData.qProgram.GetFieldValue('VProduct.AccountName')
        CurrencyCode = '000'
        CurrencyName = 'IDR'
        ProductType = 'G'
        Amount = 0.0
        DisbId = 0
        self.pInvoice_Amount.ReadOnly = 0
        self.pInvoice_Amount.Color=16777215
      # endif
      
      uipInvoice.Edit()
      uipInvoice.ProductAccountNo = AccountNo
      uipInvoice.ProgramName = ProductName
      uipInvoice.Description = ProductName
      uipInvoice.ProductType = ProductType
      uipInvoice.Amount = Amount
      uipInvoice.DisbId = DisbId
      uipInvoice.SetFieldValue('LCurrency.Currency_Code',CurrencyCode)
      uipInvoice.SetFieldValue('LCurrency.Short_Name',CurrencyName)

  def CheckRequired(self):
    uipInvoice = self.uipInvoice

    if uipInvoice.ActualDate in [0, None] :
      raise 'PERINGATAN','Tanggal Transaksi belum diinputkan'

    if uipInvoice.SponsorId in [0, None] :
      raise 'PERINGATAN','Nama Sponsor belum diinputkan'
      
    if uipInvoice.InvoiceDate in [0, None] :
      raise 'PERINGATAN','Tanggal Invoice belum diinputkan'

    if uipInvoice.ProductAccountNo in [0, None] :
      raise 'PERINGATAN','Nama Program belum diinputkan'

    if (uipInvoice.Amount or 0.0) <= 0.0:
      raise 'PERINGATAN','Jumlah Tagihan tidak boleh <= 0.0 '

      
  def PrintInvoiceClick(self,sender):
    app = self.app
    form = self.form
    uipInvoice = self.uipInvoice

    self.CheckRequired()
    form.CommitBuffer()
    
    if uipInvoice.ShowMode == 1:
      rph = form.CallServerMethod('ProsesVoucherNew',form.GetDataPacket())
    else:
      rph = form.CallServerMethod('ProsesVoucherUpdate',form.GetDataPacket())
    # end if else

    status = rph.FirstRecord

    if status.Is_Err : raise 'PERINGATAN',status.Err_Message

    oPrint = app.GetClientClass('PrintLib','PrintLib')()
    oPrint.doProcessByStreamName(app,rph.packet,status.StreamName,1)
    oPrint.doProcessByStreamName(app,rph.packet,status.VoucherName,1)
    
    self.uipInvoice.Edit()
    self.uipInvoice.InvoiceId = status.InvoiceId

    sender.ExitAction = 1
