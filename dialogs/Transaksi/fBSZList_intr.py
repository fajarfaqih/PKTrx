class fBSZList:
  def __init__(self,formObj,parentForm):
    self.app = formObj.ClientApplication
    self.form = formObj
    self.LockGrid = 1
    self.AmountList = {}
    self.fSearchDonor = None
    self.fSelectTransaction = None
    self.ItemTransaction = {}
    self.fBSZNew = None
    
  # PRIVATE METHOD

  def Show(self,restriction=0):
    #self.pData_bSelectTransaction.Enabled = (not restriction)
    #self.uipData.Edit()
    #self.uipData.Jumlah = 0.0
    #self.uipData.JumlahDetail = 0.0
    #self.PrepareDetail()
    self.FormContainer.Show()

  def PrepareDetail(self):
    self.LockGrid = 0
    ObjekZakat = ['Emas,Perak,Uang',
               'Perdagangan dan Perusahaan',
               'Hasil Pertanian Perkebunan dan Perikanan',
               'Hasil Pertambangan',
               'Hasil Peternakan',
               'Hasil Pendapatan Jasa',
               'Rikaz',
               ]

    uipDetail = self.uipDetail
    
    idx = 0
    for Objek in ObjekZakat :
      uipDetail.Append()
      uipDetail.ObjekZakat = Objek
      uipDetail.TahunPerolehan = 0
      uipDetail.Kadar = 2.5
      uipDetail.DasarPengenaan = 0
      uipDetail.Jumlah = 0
      uipDetail.ItemIdx = idx
      uipDetail.ItemNo = idx + 1
      self.AmountList[idx] = uipDetail.Jumlah
      idx += 1
    # endfor
    self.LockGrid = 1

  def CheckInput(self):
    uipDetail = self.uipDetail
    
    # Cek Donor
    if (self.uipData.DonorId or 0) == 0:
      raise 'PERINGATAN','Data donor belum dipilih'
    
    
    # Cek Nomor BSZ
    if (self.uipData.BSZNo or '') == '':
      self.pData_BSZNo.SetFocus()
      raise 'PERINGATAN','Nomor BSZ belum diinputkan'
    
    if (self.uipData.Jumlah or 0.0) == 0.0:
      raise 'PERINGATAN','Data transaksi belum dipilih'
      
    # Cek Jumlah Detail dan Jumlah Setoran
    Summary = 0
    uipDetail.First()
    while not uipDetail.Eof:
      Summary += uipDetail.Jumlah
      uipDetail.Next()
    #end for
    
    if Summary != self.uipData.Jumlah :
      raise 'PERINGATAN','Jumlah detail tidak sama dengan jumlah setoran'
      
  #------ FORM EVENT
  
  def BSZPrintClick(self,sender):
    uipBSZ = self.uipBSZ
    
    if (uipBSZ.BSZId or 0) == 0 :
      return

    param = self.app.CreateValues(['BSZId',uipBSZ.BSZId])
    rph = self.form.CallServerMethod('BSZPrint',param)

    status = rph.FirstRecord
    if status.IsErr :
      raise 'PERINGATAN',status.ErrMessage

    oPrint = self.app.GetClientClass('PrintLib','PrintLib')()
    oPrint.doProcessByStreamName(self.app,rph.packet,'bsz',1)

  def BSZDeleteClick(self,sender):
    uipBSZ = self.uipBSZ
    
    if (uipBSZ.BSZId or 0) == 0 :
      return
        
    if self.app.ConfirmDialog('Yakin akan hapus BSZ dengan No %s ?' % uipBSZ.BSZNumber):
      param = self.app.CreateValues(['BSZId',uipBSZ.BSZId])
      rph = self.form.CallServerMethod('BSZDelete',param)

      status = rph.FirstRecord
      if status.IsErr :
        raise 'PERINGATAN',status.ErrMessage

      uipBSZ.Delete()
      self.app.ShowMessage('Data BSZ telah berhasil di hapus')
    
    
  def BSZNewClick(self,sender):
    uipBSZ = self.uipBSZ
    
    DonorId = self.uipData.DonorId or 0
    if DonorId == 0 : return
    
    if self.fBSZNew == None :
      form = self.app.CreateForm('Transaksi/fBSZNew','Transaksi/fBSZNew',0,None,None)
      self.fBSZNew = form
    else:
      form = self.fBSZNew
    # endif
    
    if form.CreateNewBSZ(DonorId):
      uipBSZ.Append()
      uipBSZ.BSZNumber = form.uipData.BSZNo
      uipBSZ.BSZDate = form.uipData.BSZDate
      uipBSZ.BSZTotal = form.uipData.Jumlah
      uipBSZ.BSZId = form.uipData.BSZId
  
  def bSelectTransactionClick(self,sender):
    DonorId = self.uipData.DonorId or 0
    if DonorId == 0:
      self.app.ShowMessage('Data donor belum dipilih')
      return

    if self.fSelectTransaction == None :
      formname ='Transaksi/fSelectTransactionByDonor2'
      fTrans = self.app.CreateForm(formname,formname,0,None,None)
      self.fSelectTransaction = fTrans
    else :
      fTrans = self.fSelectTransaction
      
    if fTrans.GetTransaction(DonorId):
      uipDonorTrans = fTrans.uipDonorTrans
      
      uipDonorTrans.First()
      i = 0
      Exist = []
      for i in range(uipDonorTrans.RecordCount):
        if uipDonorTrans.stProses == 'P' :
          if self.ItemTransaction.has_key(uipDonorTrans.TransactionItemId):
            Exist.append(uipDonorTrans.TransactionNo)
          else:
            self.uipTransaction.Append()
            rec = self.uipTransaction
            rec.TransactionItemId = uipDonorTrans.TransactionItemId
            rec.Amount = uipDonorTrans.Amount
            rec.AccountName = uipDonorTrans.GetFieldValue('LFinancialAccount.AccountName')
            rec.TransactionDate = uipDonorTrans.TransactionDate
            rec.Description = uipDonorTrans.Description
            rec.TransactionNo = uipDonorTrans.TransactionNo
            self.ItemTransaction[uipDonorTrans.TransactionItemId] = uipDonorTrans.Amount
            self.uipData.Jumlah += uipDonorTrans.Amount
            self.uipTransaction.Post()
        uipDonorTrans.Next()

      if len(Exist) > 0 :
        self.app.ShowMessage('Transaksi dgn nomor transaksi berikut ini sudah ada dalam daftar :' + '\n'.join(Exist))
        
      return

      #-------------code di bawah ini diabaikan sementara ---------------------
      if self.ItemTransaction.has_key(fTrans.TransactionItemId):
        self.app.ShowMessage('Transaksi yang dipilih sudah ada dalam daftar')
        return 0

      self.uipTransaction.Append()
      rec = self.uipTransaction
      rec.TransactionItemId = fTrans.TransactionItemId
      rec.Amount = fTrans.Amount
      rec.AccountName = fTrans.AccountName
      rec.TransactionDate = fTrans.TransactionDate
      rec.Description = fTrans.Description
      rec.TransactionNo = fTrans.TransactionNo
      self.ItemTransaction[fTrans.TransactionItemId] = fTrans.Amount
      self.uipData.Edit()
      self.uipData.Jumlah += fTrans.Amount
    # end if

  def TransItemBeforeDelete(self,sender):
    del self.ItemTransaction[sender.TransactionItemId]
    self.uipData.Jumlah -= sender.Amount

  def CariDonorClick(self,sender):
    if self.fSearchDonor == None :
      fSearch = self.app.CreateForm('Donatur/fSearchDonor', 'Donatur/fSearchDonor', 0, None, None)
      self.fSearchDonor = fSearch
    else :
      fSearch = self.fSearchDonor

    if fSearch.GetDonorData():
      uipDonor = self.uipData
      uipDonor.Edit()

      uipDonor.DonorId = fSearch.DonorIntId
      uipDonor.NPWZ = fSearch.NPWZ or ''
      uipDonor.NPWP = fSearch.NPWP or ''
      uipDonor.Nama_Muzakki = fSearch.DonorName
      uipDonor.Alamat = fSearch.Address or ''
      self.pData_edAddress.Text = fSearch.Address or ''
      #self.pData_bSelectTransaction.SetFocus()
      self.uipBSZ.ClearData()
      self.GetBSZList()


  def GetBSZList(self):
    app = self.app
    form = self.form
    uipBSZ = self.uipBSZ
    
    params = app.CreateValues(['DonorId',self.uipData.DonorId])
    rph = form.CallServerMethod('GetBSZList',params)
    
    status = rph.FirstRecord
    if status.IsErr :
      raise 'PERINGATAN',status.ErrMessage
      
    ds = rph.packet.bszlist
    i = 0
    while i < ds.RecordCount:
      rec = ds.GetRecord(i)
      uipBSZ.Append()
      uipBSZ.BSZDate = rec.BSZDate
      uipBSZ.BSZNumber = rec.BSZNumber
      uipBSZ.BSZId = rec.BSZId
      uipBSZ.BSZTotal = rec.Total
      i += 1
    # end while

  def bCetakClick(self,sender) :
    form = self.form
    app = self.app
    
    form.CommitBuffer()
    self.CheckInput()
    resp = form.CallServerMethod('CetakBSZ',form.GetDataPacket())
    
    status = resp.FirstRecord
    if status.IsErr : raise '',status.ErrMessage
    
    oPrint = app.GetClientClass('PrintLib','PrintLib')()
    oPrint.doProcessByStreamName(self.app,resp.packet,'bsz',1)
    #oPrint.doProcessByStreamName(self.app,resp.packet,'bsz1')
    #oPrint.doProcessByStreamName(self.app,resp.packet,'bsz2')
    #oPrint.doProcessByStreamName(self.app,resp.packet,'bsz3')

    #sender.ExitAction = 1
    
  def ItemAfterNewRecord(self,sender):
    if self.LockGrid : sender.Delete()

  def ItemBeforePost(self, sender) :
    sender.Edit()
    sender.DasarPengenaan = (sender.Jumlah / (sender.Kadar/100))
    
  def ItemAfterPost(self, sender) :

    Idx = sender.ItemIdx
    if self.AmountList.has_key(Idx):
      amountbefore = self.AmountList[Idx]
    else:
      amountbefore = 0.0
    Jumlah = sender.Jumlah or 0.0

    self.AmountList[Idx] = Jumlah

    self.uipData.Edit()
    self.uipData.JumlahDetail += (Jumlah - amountbefore)


    self.uipData.Post()

  def TesClick(self,sender):
    app = self.app

    rph = app.ExecuteScript('Transaction/S_BSZ',app.CreateValues())

    resp = rph.FirstRecord
    if resp.Is_Err : raise 'Error',resp.Err_Message

