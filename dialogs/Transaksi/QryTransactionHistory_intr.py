class QryTransactionHistory:
  def __init__(self,formObj,parentForm):
    self.form = formObj
    self.app = formObj.ClientApplication

  def Show(self):
    self.DisplayTransaction(
        self.uipFilter.BeginDate,
        self.uipFilter.EndDate
    )
    
    self.FormContainer.Show()
    
  def bApplyClick(self,sender):
    self.DisplayTransaction(
        self.uipFilter.BeginDate,
        self.uipFilter.EndDate
    )
    

  def DisplayTransaction(self,begindate,enddate):
    app = self.app
    
    qTransaction = self.qTransaction
    self.qTransaction.OQLText = "select  from Transaction \
             [ BranchCode=:BranchCode and Inputer=:UserId \
               and TransactionDate >= :BeginDate and TransactionDate <= :EndDate \
             ] \
             ( TransactionId, \
               TransactionNo as Nomor_Transaksi, \
               TransactionDate as Tanggal_Transaksi, \
               ActualDate as Tanggal_Aktual, \
               Amount as Nilai_Transaksi, \
               DonorNo as No_Donor, \
               DonorName as Nama_Donor, \
               Description as Keterangan, \
               AuthStatus as Status_Otorisasi, \
               IsPosted as Status_Posting, self) \
               then order by ASC TransactionId ;"

    uipFilter = self.uipFilter

    BeginY, BeginM, BeginD = uipFilter.BeginDate[:3]
    EndY, EndM, EndD = uipFilter.EndDate[:3]
    intBeginDate = app.ModDateTime.EncodeDate(BeginY,BeginM,BeginD)
    intEndDate = app.ModDateTime.EncodeDate(EndY,EndM,EndD)
    
    self.qTransaction.SetParameter('BranchCode', uipFilter.BranchCode)
    self.qTransaction.SetParameter('BeginDate', intBeginDate)
    self.qTransaction.SetParameter('EndDate', intEndDate)
    self.qTransaction.SetParameter('UserId', uipFilter.UserId)
    self.qTransaction.DisplayData()

  def ViewDetailClick(self,sender):
    self.ViewTransaksiDetail()
    
  def EditTransClick(self,sender):
    self.EditTransaction()
    

  def DeleteTransClick(self,sender):
    self.DeleteTransaction()


  #**** Private Method
  
  def ViewTransaksiDetail(self):
    app = self.app
    form = self.form

    formname = 'transaksi/fTransactionHistoryView'
    TransactionId = form.GetPanelByName('qTransaction').GetFieldValue('Transaction.TransactionId')

    if TransactionId == 0 : return
    ph = app.CreateValues(['TransactionId',TransactionId])

    dlg = app.CreateForm(formname,formname,0,ph,None)
    st = dlg.FormContainer.Show()

  def EditTransaction(self):
    app = self.app
    form = self.form

    qTransaction = form.GetPanelByName('qTransaction')
    
    if qTransaction.GetFieldValue('Transaction.Status_Otorisasi') == 'T' :
      raise 'PERINGATAN','Transaksi ini tidak dapat diubah karena telah di otorisasi'

    TransactionId = qTransaction.GetFieldValue('Transaction.TransactionId')

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
    qTransaction = form.GetPanelByName('qTransaction')

    if qTransaction.GetFieldValue('Transaction.Status_Otorisasi') == 'T' :
      raise 'PERINGATAN','Transaksi ini tidak dapat dihapus karena telah di otorisasi'
    
    if app.ConfirmDialog('Yakin Hapus Transaksi'):
      TransactionId = qTransaction.GetFieldValue('Transaction.TransactionId')

      if TransactionId == 0 : return
      ph = app.CreateValues(['TransactionId',TransactionId])

      rph = app.ExecuteScript('Transaction/S_DeleteTransaction',ph)
      
      resp = rph.FirstRecord
      if resp.Is_Err : raise 'Error',resp.Err_Message

      self.app.ShowMessage('Transaksi telah berhasil dihapus')
      qTransaction.DeleteRow()
