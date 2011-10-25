class fOtorisasi:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    
    self.tag_batch = None

  def Show(self):
    self.uipData.Edit()
    self.uipData.BeginNo   = 1
    self.uipData.TransactionType = 1
    self.uipData.TransactionNumber = 100
    self.uipData.IsAllTransactionType = 'T'
    self.uipData.SearchCategory = 0
    self.FormContainer.Show()

  def IsAllTransCodeClick(self,sender):
    self.form.GetPanelByName('pBatch').GetControlByName('LTransactionType').enabled = not sender.Checked
    
    if sender.Checked :
      self.uipData.Edit()
      self.uipData.SetFieldValue('LTransactionType.TransactionCode','')
      self.uipData.SetFieldValue('LTransactionType.Description','')
    # endif
      
  def SearchCategoryChange(self,sender):
    if sender.ItemIndex == 0 :
      self.uipData.Edit()
      self.uipData.SearchText = ''
      
  def bViewClick(self, sender):
    self.form.CommitBuffer()
    self.uipTransaction.ClearData()
    uipData = self.uipData
    BeginDate = uipData.BeginDate or 0
    EndDate = uipData.EndDate or 0
    TransactionNumber = uipData.TransactionNumber or 0
    TransactionCode = uipData.GetFieldValue('LTransactionType.TransactionCode') or ''
    IsAllTransactionType = uipData.IsAllTransactionType
    SearchCategory = uipData.SearchCategory or 0
    SearchText = uipData.SearchText or ''

    if BeginDate == 0 or EndDate == 0:
      raise 'PERINGATAN','Masukkan tanggal transaksi terlebih dahulu'

    if BeginDate > EndDate :
      raise 'PERINGATAN','Tanggal awal tidak boleh lebih besar dari tanggal akhir'
      
    if IsAllTransactionType == 'F' and TransactionCode == '':
      raise 'PERINGATAN','Jenis transaksi belum dipilih'

    if TransactionNumber == 0 :
      TransactionNumber = 100
      uipData.Edit()
      uipData.TransactionNumber = TransactionNumber
      
    ph = self.app.CreateValues(
       ['BeginDate',BeginDate],
       ['EndDate',EndDate],
       ['TransactionNumber', TransactionNumber],
       ['TransactionCode',TransactionCode],
       ['IsAllTransactionType',IsAllTransactionType],
       ['SearchCategory',SearchCategory],
       ['SearchText',SearchText],
       )

    self.FormObject.SetDataWithParameters(ph)
    self.uipTransaction.First()

  def bSelectClick(self,sender):
    self.SetStatusProses()

  def bRejectClick(self,sender):
    self.SetStatusBatal()

  def bResetClick(self,sender):
    self.ResetStatus()

  def bSelectAllClick(self,sender):
    uipTran = self.uipTransaction
    TotalRow = uipTran.RecordCount
    uipTran.First()
    for i in range(TotalRow):
      self.SetStatusProses()
      uipTran.Next()

  def bRejectAllClick(self,sender):
    uipTran = self.uipTransaction
    TotalRow = uipTran.RecordCount
    uipTran.First()
    for i in range(TotalRow):
      self.SetStatusBatal()
      uipTran.Next()
      
  def bResetAllClick(self,sender):
    uipTran = self.uipTransaction
    TotalRow = uipTran.RecordCount
    uipTran.First()
    for i in range(TotalRow):
      self.ResetStatus()
      uipTran.Next()
    
  def SetStatusBatal(self):
    uipTransaction = self.uipTransaction
    if uipTransaction.RecordCount > 0 :
      uipTransaction.Edit()
      uipTransaction.Proses = "B"
    #-- if
      
  def SetStatusProses(self):
    uipTransaction = self.uipTransaction
    if uipTransaction.RecordCount > 0 :
      uipTransaction.Edit()
      uipTransaction.Proses = "O"
    #-- if

  def ResetStatus(self):
    uipTransaction = self.uipTransaction
    if uipTransaction.RecordCount > 0 :
      uipTransaction.Edit()
      uipTransaction.Proses = "N"
    #-- if

  def bViewOtorisasiClick(self,sender):
    self.ViewTransaksiDetail()
    
  def ViewTransaksiDetail(self):
    uipTransaction = self.uipTransaction
    if uipTransaction.RecordCount <= 0 :
      return 0

    tranCode = uipTransaction.TransactionCode
    # launch transaction view here...

  def ClearData(self):
    data = self.uipTransaction
    data.First()
    while not data.Eof:
      data.Delete()
    #-- while

  def ClearProsesData(self):
    data = self.uipTransaction
    data.First()
    while not data.Eof:
      if data.Proses != 'N':
        data.Delete()
      else:
        data.Next()
      #-- if.else
    #-- while

  def GetTransactionProcessList(self):
    data = self.uipTransaction
    data.First()
    trList = {}
    while not data.Eof:
      trList[data.TransactionId] = data.Proses
      data.Next()
    #-- while
    
    return trList
    
  def bProsesClick(self,sender):
    if self.app.ConfirmDialog('Yakin Akan Melakukan Proses Otorisasi ?'):
      form = self.form
      form.CommitBuffer()
      # create transaction id list
      ph = self.app.CreateValues(
        ['TransactionList', str(self.GetTransactionProcessList())])
      resph = form.CallServerMethod('ProsesOtorisasi', ph)
        
      st = resph.FirstRecord
      if st.Is_Err == 1:
        raise 'PERINGATAN', st.Err_Message
      #-- if

      sMessage = 'Transaksi yang dipilih telah berhasil di otorisasi!'
      if st.Is_Err == 2:
        sMessage += '\nTetapi gagal dijurnal : '
        sMessage += st.Err_Message
        sMessage += '\nSilahkan lihat file log yang akan ditampilkan dan lakukan jurnal ulang!'
      #-- if

      self.app.ShowMessage(sMessage)

      if st.Is_Err == 2:
        oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
        oPrint.doProcessByStreamName(self.app,resph.packet,st.FileLogJournal,1)
        
      self.ClearProsesData()
    #-- if

  def ViewDetailComplete(self,sender):
    uipTransaction = self.uipTransaction
    if uipTransaction.RecordCount <= 0 :
      return 0

    trCode = uipTransaction.TransactionCode
    #formId = 'Transaksi/fDetilTransaksi_Query'
    transactionId = uipTransaction.transactionId
    ph = self.app.CreateValues(['TransactionId', transactionId])
    form = self.app.CreateForm(formId, formId, 0, ph, None)
    if self.userapp.IsHasResource(formId):
        form.FormObject.SetDataWithParameters(ph)
    else: self.userapp.AddResource(formId)
    #form.Show()
    form.DisplayQuery()
