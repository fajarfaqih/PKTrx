class fPrintVoucherDonation:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self,SPVMode=0):
    self.uipData.Edit()
    self.uipData.BeginItemNo = 1
    self.uipData.DateCategory = 1
    self.uipData.SortCategory = 1
    self.uipData.IsAllCabang = 'F'
    self.uipData.SearchCategory = 0
    self.uipData.IsSPV = SPVMode
    self.uipData.LimitData = 50
    self.pBatch_SearchText.enabled = 0
    self.pBatch_SearchText.Color=-2147483624

    #if SPVMode :
    #  self.pTranAction_bDeleteTrans.visible = 0

    if self.uipData.BranchCode != '001' or not SPVMode:
      self.pBatch_IsAllCabang.visible = 0
      self.pBatch_LBranch.enabled = 0

    return self.FormContainer.Show()

  def AllCabangClick(self,sender):
    self.pBatch_LBranch.enabled = sender.Checked == 0
    if sender.Checked == 1 :
      self.uipData.SetFieldValue('LBranch.Kode_Cabang','')
      self.uipData.SetFieldValue('LBranch.Nama_Cabang','')
      
  def CategoryOnChange(self,sender):
    self.pBatch_SearchText.enabled = sender.ItemIndex != 0
    if sender.ItemIndex == 0:
      self.pBatch_SearchText.Color=-2147483624
    else:
      self.pBatch_SearchText.Color=16777215
      self.uipData.Edit()
      self.uipData.SearchText = ''
    # end if else

  def bLihatTransaksiClick(self, sender):
    uipData = self.uipData
#    beginNo = self.uipData.BeginItemNo
    BeginDate = uipData.BeginDate
    EndDate = uipData.EndDate
    IsAllBranch = uipData.IsAllCabang
    SearchCategory = uipData.SearchCategory
    SearchText = uipData.SearchText or ''
    IsSPV = uipData.IsSPV
    BranchCode = uipData.GetFieldValue('LBranch.Kode_Cabang') or ''
    DateCategory = uipData.DateCategory
    SortCategory = uipData.SortCategory
    LimitData = uipData.LimitData or 0
    #if beginNo <=0 :
    #  raise 'PERINGATAN' , 'Nomor awal yang ditampilkan tidak boleh 0 atau negatif'

    ph = self.app.CreateValues(
#        ['BeginNo', beginNo],
      ['BeginDate',BeginDate],
      ['EndDate',EndDate],
      ['IsAllCabang',IsAllBranch],
      ['BranchCode',BranchCode],
      ['SearchCategory',SearchCategory],
      ['SearchText',SearchText],
      ['IsSPV',IsSPV],
      ['DateCategory',DateCategory],
      ['SortCategory',SortCategory],
      ['LimitData',LimitData],
      )

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

  def bPrintKwitansiClick(self,sender):
    transactionId = self.uipTransaction.TransactionId
    if transactionId != None:
      ph = self.app.CreateValues(
        ['TransactionId', transactionId])

      ph = self.form.CallServerMethod('PrintKwitansi', ph)

      st = ph.FirstRecord
      if st.Is_Err == 1:
        raise 'PERINGATAN', st.Err_Message
      #-- if
      
      # Print Slip Transaksi
      oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
      self.app.ShowMessage("Masukkan Aplikasi ke Printer")
      oPrint.doProcessByStreamName(self.app,ph.packet,st.Stream_Name)
    #--if

  def ViewDetailClick(self,sender):
    self.ViewTransaksiDetail()

  def EditTransClick(self,sender):
    self.EditTransaction()

  def DeleteTransClick(self,sender):
    self.DeleteTransaction()
    
  def PrintVoucherClick(self,sender):
    self.PrintVoucher()

  #**** Private Method

  def GridDoubleClick(self,sender):
    self.PrintVoucher()
    
  def ViewTransaksiDetail(self):
    app = self.app
    form = self.form

    formname = 'transaksi/fTransactionHistoryView'
    TransactionId = self.uipTransaction.TransactionId or 0#form.GetPanelByName('qTransaction').GetFieldValue('Transaction.TransactionId')

    if TransactionId == 0 : return
    ph = app.CreateValues(['TransactionId',TransactionId])

    dlg = app.CreateForm(formname,formname,0,ph,None)
    st = dlg.FormContainer.Show()

  def EditTransaction(self):
    app = self.app
    form = self.form
    uipTran = self.uipTransaction

    #qTransaction = form.GetPanelByName('qTransaction')

    #if uipTran.AuthStatus == 'T' :
    #  raise 'PERINGATAN','Transaksi ini tidak dapat diubah karena telah di otorisasi'
      
    if uipTran.BranchCode != self.uipData.BranchCode :
      raise 'PERINGATAN','Anda tidak dapat mengubah transaksi milik cabang lain'

    TransactionId = uipTran.TransactionId or 0 #qTransaction.GetFieldValue('Transaction.TransactionId')

    if TransactionId == 0 : return
    #ph = app.CreateValues(
    #   ['TransactionId',TransactionId],
    #   ['Modus_SetData',1])

    ph = app.CreatePacket()

    ds = ph.Packet.AddNewDatasetEx(
        'trparam',
        ';'.join(
        ['TransactionId:integer' ,
         'Modus_SetData:integer',
        ])
    )
    rec = ds.AddRecord()
    rec.TransactionId = TransactionId
    rec.Modus_SetData = 1

    rph = app.ExecuteScript('Transaction/S_GetTransactionForm',ph)

    resp = rph.FirstRecord
    if resp.Is_Err : raise 'Error',resp.Err_Message

    formname = resp.FormName

    dlg = app.CreateForm(formname,formname,0,ph,None)
    dlg.Show(mode=2)

  def DeleteTransaction(self):
    app = self.app
    form = self.form
    uipTran = self.uipTransaction

    if uipTran.BranchCode != self.uipData.BranchCode :
      raise 'PERINGATAN','Anda tidak dapat menghapus transaksi milik cabang lain'
      
    if uipTran.AuthStatus == 'T' and not self.uipData.IsSPV:
      raise 'PERINGATAN','Transaksi ini tidak dapat dihapus karena telah di otorisasi.\nSilahkan hubungi supervisor cabang anda'

    if app.ConfirmDialog('Yakin Hapus Transaksi'):
      TransactionId = uipTran.TransactionId or 0

      if TransactionId == 0 : return
      ph = app.CreateValues(['TransactionId',TransactionId])

      rph = app.ExecuteScript('Transaction/S_DeleteTransaction',ph)

      resp = rph.FirstRecord
      if resp.Is_Err : raise 'Error',resp.Err_Message

      self.app.ShowMessage('Transaksi telah berhasil dihapus')
      uipTran.Delete()
      #qTransaction.DeleteRow()
      
  def PrintVoucher(self):
    uipTran = self.uipTransaction
    transactionId = uipTran.TransactionId or 0
    
    if uipTran.BranchCode != self.uipData.BranchCode :
      raise 'PERINGATAN','Anda tidak dapat mencetak kwitansi milik cabang lain'
      
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
