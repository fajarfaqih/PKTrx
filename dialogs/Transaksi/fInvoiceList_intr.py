class fInvoiceList:

  # --- FORM EVENT ----
  
  def __init__(self,formObj,parentObj):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.fInvoice = None
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()


  def bViewClick(self,sender):
    self.__ViewList()

  def bPrintVoucherClick(self,sender):
    self.__PrintVoucher()
    
  def bPrintClick(self,sender):
    app = self.app
    
    InvoiceId = self.uipInvoice.InvoiceId or 0

    if InvoiceId == 0 : return

    resp = self.form.CallServerMethod('PrintInvoice',
      app.CreateValues(['InvoiceId',InvoiceId])
    )
    
    status = resp.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message

    self.oPrint.doProcessByStreamName(app,resp.packet,status.StreamName,1)

  def bDeleteClick(self,sender):
    app = self.app

    InvoiceId = self.uipInvoice.InvoiceId or 0
    InvoiceNo = self.uipInvoice.InvoiceNo or ''

    if InvoiceId == 0 : return


    if app.ConfirmDialog('Yakin Hapus Invoice No. %s ?' % InvoiceNo):
    
      resp = self.form.CallServerMethod('DeleteInvoice',
        app.CreateValues(['InvoiceId',InvoiceId])
      )

      status = resp.FirstRecord
      if status.Is_Err : raise 'PERINGATAN',status.Err_Message

      self.uipInvoice.Delete()
      app.ShowMessage('Invoice No. %s berhasil dihapus' % InvoiceNo)
    # end if

  def bEditClick(self,sender):
    app = self.app

    InvoiceId = self.uipInvoice.InvoiceId or 0
    InvoiceNo = self.uipInvoice.InvoiceNo or ''

    if InvoiceId == 0 : return
    
    if self.uipInvoice.InvoicePaymentStatus == 'T' :
      raise "PERINGATAN","Data invoice tidak dapat dihapus karena telah memiliki transaksi pembayaran. \nSilahkan hapus dahulu transaksi pembayarannya"
    
    if self.fInvoice == None :
      form = self.app.CreateForm(
          'Transaksi/fInvoice',
          'Transaksi/fInvoice',
           0, None, None)
      self.fInvoice = form
    else:
      form = self.fInvoice
    # end if
    if form.Show(InvoiceId):
      uipInvoice = self.uipInvoice
      uipInvoice.Edit()
      uipInvoice.InvoiceId = form.uipInvoice.InvoiceId
      uipInvoice.InvoiceNo = form.uipInvoice.InvoiceNo
      uipInvoice.InvoiceDate = form.uipInvoice.InvoiceDate
      uipInvoice.InvoicePaymentStatus = 'F'
      uipInvoice.InvoiceAmount = form.uipInvoice.Amount
      uipInvoice.SponsorId = form.uipInvoice.SponsorId
      uipInvoice.SetFieldValue('LSponsor.Id',form.uipInvoice.SponsorId)
      uipInvoice.SetFieldValue('LSponsor.Full_Name',form.uipInvoice.SponsorName)
      uipInvoice.SetFieldValue('LProductAccount.AccountNo',form.uipInvoice.ProductAccountNo)
      uipInvoice.SetFieldValue('LProductAccount.AccountName',form.uipInvoice.ProgramName)
      uipInvoice.Description = form.uipInvoice.Description
      uipInvoice.Post()
    # end if
    
    
  def bNewInvoiceClick(self,sender):
    if self.fInvoice == None :
      form = self.app.CreateForm(
          'Transaksi/fInvoice',
          'Transaksi/fInvoice',
           0, None, None)
      self.fInvoice = form
    else:
      form = self.fInvoice
    # end if
    if form.Show():
      return
      uipInvoice = self.uipInvoice
      uipInvoice.Edit()
      uipInvoice.Append()
      uipInvoice.InvoiceId = form.uipInvoice.InvoiceId
      uipInvoice.InvoiceNo = form.uipInvoice.InvoiceNo
      uipInvoice.InvoiceDate = form.uipInvoice.InvoiceDate
      uipInvoice.InvoicePaymentStatus = 'F'
      uipInvoice.InvoiceAmount = form.uipInvoice.InvoiceAmount
      uipInvoice.SponsorId = form.uipInvoice.SponsorId
      uipInvoice.SetFieldByName('LSponsor.Id',form.uipInvoice.SponsorId)
      uipInvoice.SetFieldByName('LSponsor.Full_Name',form.uipInvoice.SponsorName)
      uipInvoice.SetFieldByName('LProductAccount.AccountNo',form.uipInvoice.ProductAccountNo)
      uipInvoice.SetFieldByName('LProductAccount.AccountName',form.uipInvoice.ProgramName)
      uipInvoice.Description = form.uipInvoice.Description
    #AccountNo = self.qFixedAsset.GetFieldValue('FixedAsset.AccountNo')
    #form.Show(AccountNo)
    
  def bExcelClick(self,sender):
    app = self.app
    uipFilter = self.uipFilter

    BeginDate = uipFilter.BeginDate or 0
    EndDate = uipFilter.EndDate or 0
    IsShowPaidInvoice = uipFilter.IsShowPaidInvoice or 'F'
    
    ph = self.app.CreateValues(
       ['BeginDate',BeginDate],
       ['EndDate',EndDate],
       ['IsShowPaidInvoice',IsShowPaidInvoice]
       )

    resp = self.form.CallServerMethod('GetExcelInvoice',ph)

    status = resp.FirstRecord

    if status.Is_Err :
      raise 'PERINGATAN',status.Err_Message

    sw = resp.Packet.GetStreamWrapper(0)

    fileName = self.oPrint.ConfirmDestinationPath(app,'xls')

    if fileName in ['',None,0] :
      return

    sw.SaveToFile(fileName)
    self.app.ShellExecuteFile(fileName)
    
  #---- OTHER METHOD ------

  def GenerateParams(self):

    uipFilter = self.uipFilter
    BeginDate = uipFilter.BeginDate or 0
    EndDate = uipFilter.EndDate or 0
    IsShowPaidInvoice = uipFilter.IsShowPaidInvoice or 'F'

    if BeginDate == 0 or EndDate == 0 :
      raise '','Masukkan periode transaksi terlebih dahulu'

    params = self.app.CreateValues(
       ['BeginDate',BeginDate],
       ['EndDate',EndDate],
       ['IsShowPaidInvoice',IsShowPaidInvoice]
       )

    return params
  def Show(self):
    self.uipFilter.Edit()
    self.uipFilter.IsShowPaidInvoice = 'F'
    self.__ViewList()
    self.FormContainer.Show()

  def __PrintVoucher(self):
    uipInvoice = self.uipInvoice
    transactionId = uipInvoice.TransactionId or 0

    if transactionId != 0:
      ph = self.app.CreateValues(
        ['TransactionId', transactionId])

      ph = self.app.ExecuteScript('Transaction/S_Kwitansi.Print', ph)

      st = ph.FirstRecord
      if st.Is_Err == 1:
        raise 'PERINGATAN', st.Err_Message
      #-- if

      # Print Slip Transaksi
      #self.app.ShowMessage("Masukkan Kertas Kwitansi ke Printer")
      self.oPrint.doProcessByStreamName(self.app,ph.packet,st.Stream_Name)
    #--if
  
  def __ViewList(self):
    self.form.CommitBuffer()

    uipFilter = self.uipFilter
    BeginDate = uipFilter.BeginDate or 0
    EndDate = uipFilter.EndDate or 0
    IsShowPaidInvoice = uipFilter.IsShowPaidInvoice or 'F'

    if BeginDate == 0 or EndDate == 0 :
      raise '','Masukkan periode transaksi terlebih dahulu'

    ph = self.app.CreateValues(
       ['BeginDate',BeginDate],
       ['EndDate',EndDate],
       ['IsShowPaidInvoice',IsShowPaidInvoice]
       )

    self.FormObject.SetDataWithParameters(ph)
    self.uipInvoice.First()
    
