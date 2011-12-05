class fTransactionHistory:

  def __init__(self, formObj, parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication
    self.userapp = self.app.UserAppObject
    self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

  def Show(self,SPVMode=0):
    uipData = self.uipData
    uipData.Edit()
    uipData.BeginItemNo = 1
    uipData.DateCategory = 1
    uipData.SortCategory = 1
    uipData.IsAllCabang = 'F'
    uipData.SearchCategory = 0
    uipData.IsSPV = SPVMode
    uipData.RangeAmountFrom = 0.0
    uipData.RangeAmountTo = 10000000
    uipData.LimitData = 50
    self.pBatch_SearchText.enabled = 0
    self.pBatch_SearchText.Color=-2147483624

    if SPVMode :
      self.form.Caption += ' (Supervisor)'
    else:
      self.pBatch_IsAllCabang.visible = 0
      self.pBatch_LBranch.enabled = 0
    # end if.else
    
    IsHeadOffice = (uipData.BranchCode == uipData.HeadOfficeCode)
    self.MasterBranchCode = ''

    if not IsHeadOffice :
      uipData.MasterBranchCode = uipData.BranchCode
      
    #if not IsHeadOffice or not SPVMode:
    uipData.SetFieldValue('LBranch.BranchCode',uipData.BranchCode)
    uipData.SetFieldValue('LBranch.BranchName',uipData.BranchName)

    return self.FormContainer.Show()

  def AllCabangClick(self,sender):
    self.pBatch_LBranch.enabled = sender.Checked == 0
    if sender.Checked == 1 :
      self.uipData.SetFieldValue('LBranch.BranchCode','')
      self.uipData.SetFieldValue('LBranch.BranchName','')
      
  def CategoryOnChange(self,sender):
    self.pBatch_SearchText.enabled = sender.ItemIndex != 0
    if sender.ItemIndex == 0:
      self.pBatch_SearchText.Color=-2147483624
    else:
      self.pBatch_SearchText.Color=16777215
      self.uipData.Edit()
      self.uipData.SearchText = ''
    # end if else

  def CreateTransactionParam(self):

    uipData = self.uipData
#    beginNo = self.uipData.BeginItemNo
    BeginDate = uipData.BeginDate
    EndDate = uipData.EndDate
    IsAllBranch = uipData.IsAllCabang
    SearchCategory = uipData.SearchCategory
    SearchText = uipData.SearchText or ''
    IsSPV = uipData.IsSPV
    BranchCode = uipData.GetFieldValue('LBranch.BranchCode') or ''
    DateCategory = uipData.DateCategory
    SortCategory = uipData.SortCategory
    LimitData = uipData.LimitData or 0
    RangeAmountFrom = uipData.RangeAmountFrom or 0.0
    RangeAmountTo = uipData.RangeAmountTo or 0.0
    
    # Check Parameter
    if RangeAmountFrom > RangeAmountTo :
      raise 'PERINGATAN','Batas Nominal Awal harus lebih kecil / sama dengan Batas Nominal Akhir'
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
      ['RangeAmountFrom',RangeAmountFrom],
      ['RangeAmountTo',RangeAmountTo],
      )
    return ph

  def bLihatTransaksiClick(self, sender):
    ph = self.CreateTransactionParam()
    
    self.FormObject.SetDataWithParameters(ph)
    self.uipTransaction.First()
    #--if

  def ExportExcelClick(self,sender):
    app = self.app
    form = self.form

    filename = self.oPrint.ConfirmDestinationPath(app,'xls')
    if filename in ['',None] : return

    #ph = self.FormObject.GetDataPacket()
    #ph = self.app.ExecuteScript("Report/S_DailyCash.PrintExcel", ph)

    ph = self.CreateTransactionParam()
    
    rph = form.CallServerMethod('GetTransactionList',ph)

    status = rph.FirstRecord
    if status.Is_Err : raise 'PERINGATAN',status.Err_Message


    workbook = self.oPrint.OpenExcelTemplate(app,'tplHistTransList.xls')
    workbook.ActivateWorksheet('Data')
    try :
      #workbook.SetCellValue(2, 2, status.BranchName)
      #workbook.SetCellValue(3, 2, status.PeriodYear)
      #workbook.SetCellValue(4, 2, uipBudget.GetFieldValue("LBudgetOwner.OwnerName"))

      ds = rph.packet.transaction
      i = 0
      while i < ds.RecordCount:
        rec = ds.GetRecord(i)
        row = i + 4

        workbook.SetCellValue(row, 1, rec.TransactionNo)
        workbook.SetCellValue(row, 2, rec.ChannelName)
        workbook.SetCellValue(row, 3, rec.TransactionDate)
        workbook.SetCellValue(row, 4, rec.ActualDate)
        workbook.SetCellValue(row, 5, rec.Amount)
        workbook.SetCellValue(row, 6, rec.DonorNo)
        workbook.SetCellValue(row, 7, rec.DonorName)
        workbook.SetCellValue(row, 8, rec.ReferenceNo)
        workbook.SetCellValue(row, 9, rec.Description)
        workbook.SetCellValue(row, 10, rec.Inputer)
        workbook.SetCellValue(row, 11, rec.AuthStatus)
        workbook.SetCellValue(row, 12, rec.IsPosted)
        workbook.SetCellValue(row, 13, rec.BranchName)
        

        i += 1
      # end while

      workbook.SaveAs(filename)

    finally:
      workbook = None

    app.ShellExecuteFile(filename)


    
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
    self.ViewTransaksiDetail()
    
  def ViewTransaksiDetail(self):
    app = self.app
    form = self.form

    formname = 'transaksi/fTransactionHistoryView'
    TransactionId = self.uipTransaction.TransactionId or 0#form.GetPanelByName('qTransaction').GetFieldValue('Transaction.TransactionId')

    if TransactionId == 0 : return
    ph = app.CreateValues(['TransactionId',TransactionId])

    dlg = app.CreateForm(formname,formname,0,None,None)
    dlg.Show(TransactionId)

  def CheckSpecialTransaction(self):
    uipTran = self.uipTransaction

    if uipTran.TransactionCode == 'INVC' :
      raise 'PERINGATAN','Transaksi pembuatan invoice tidak dapat diubah / dihapus menggunakan form ini.\n Silahkan gunakan form daftar Invoice'

    if uipTran.TransactionCode == 'SD002' :
      raise 'PERINGATAN','Transaksi ini tidak dapat diubah / dihapus menggunakan form ini karena berasal dari eksternal aplikasi.\n Silahkan gunakan fungsi hapus / ubah dari eksternal aplikasi'

    if uipTran.TransactionCode == 'TB' :
      raise 'PERINGATAN','Transaksi Saldo Awal tidak dapat diubah / dihapus menggunakan form ini .\n Silahkan gunakan form Saldo Awal'

  def EditTransaction(self):
    app = self.app
    form = self.form
    uipTran = self.uipTransaction

    #qTransaction = form.GetPanelByName('qTransaction')

    #if uipTran.AuthStatus == 'T' :
    #  raise 'PERINGATAN','Transaksi ini tidak dapat diubah karena telah di otorisasi'
      
    self.CheckSpecialTransaction()
      
    if uipTran.BranchCode != self.uipData.BranchCode :
      raise 'PERINGATAN','Anda tidak dapat mengubah transaksi milik cabang lain'

    if uipTran.AuthStatus == 'T' and not self.uipData.IsSPV:
      raise 'PERINGATAN','Transaksi ini tidak dapat diubah karena telah di otorisasi.\nSilahkan hubungi supervisor cabang anda'
      
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

    self.CheckSpecialTransaction()
    
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
      #self.oPrint.doProcessByStreamName(self.app,ph.packet,st.Stream_Name,2)
      self.oPrint.doProcessByStreamName(self.app,ph.packet,st.Stream_Name)
    #--if
    
