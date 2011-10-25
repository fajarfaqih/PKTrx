class fTransactionHistoryView:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self):
    self.uipData.Edit()
    self.uipData.BeginItemNo = 1
    
    return self.FormContainer.Show()


  def bLihatTransaksiClick(self, sender):
    batchId = self.uipData.GetFieldValue('LBatch.BatchId')
    beginNo = self.uipData.BeginItemNo
    if beginNo <=0 :
      raise 'PERINGATAN' , 'Nomor awal yang ditampilkan tidak boleh 0 atau negatif'

    if batchId not in ['',None]:
      #self.FormObject.SetDataFromQuery('uipTransaksi',
      #'LBatchTransaksi.Id_Batch_Transaksi = %d' % int(id), '')
      ph = self.app.CreateValues(
        ['BatchId', batchId],
        ['BeginNo', beginNo])

      self.FormObject.SetDataWithParameters(ph)
      self.uipTransaction.First()
    #--if

  def bPostingClick(self, sender):
    transactionId = self.uipTransaction.TransactionId
    if transactionId != None:
      if self.uipTransaction.IsPosted == 'T':
        raise 'PERINGATAN' , 'Transaksi sudah di posting'

      ph = self.app.CreateValues(
        ['TransactionId', transactionId])

      ph = self.form.CallServerMethod('JurnalTransaksi', ph)

      st = ph.FirstRecord
      if st.Is_Err in [1,2]:
        raise 'PERINGATAN', st.Err_Message

      self.uipTransaction.Edit()
      self.uipTransaction.IsPostedMir = 'T'
      self.app.ShowMessage('Transaksi Berhasil di Posting')
      #-- if
    #--if

  def bViewJournalClick(self,sender):
    uipTran = self.uipTransaction
    if uipTran.RecordCount <= 0 :
      return 0

    #kode = uipTran.Kode_Transaksi
    formId = 'Transaksi/fJournal_View'
    TransactionId = uipTran.TransactionId
    #Id_Journal_Block = uipTransaksi.Id_Blok_Jurnal or 0
    #Nomor_Batch = self.uipInput.GetFieldValue('LBatch.Nomor_Batch')

    ph = self.app.CreateValues(['TransactionId', TransactionId])

    form = self.app.CreateForm(formId, formId, 0, ph, None)

    #if self.userapp.IsHasResource(formId):
    #  form.FormObject.SetDataWithParameters(ph)
    #else: self.userapp.AddResource(formId)
    form.FormContainer.Show()
    
  def bPrintKwitansiClick(self,sender):
    transactionId = self.uipTransaction.TransactionId
    if transactionId != None:
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
