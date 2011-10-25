import com.ihsan.foundation.pobjecthelper as phelper
import sys,os

MAX_TRANSACTION = 20
MAX_DETAIL = 10


def FormSetDataEx(uideflist, parameter):
  config = uideflist.config

  if (parameter.DatasetCount == 0 or
    parameter.GetDataset(0).Structure.StructureName != 'data'):
    rec = uideflist.uipData.Dataset.AddRecord()
    rec.UserId = config.securitycontext.InitUser
    Now = config.Now()
    rec.BeginDate = int(Now)
    rec.EndDate = int(Now)
    rec.SetFieldByName('LBranch.Kode_Cabang',config.securitycontext.GetUserInfo()[4])
    rec.SetFieldByName('LBranch.Nama_Cabang',config.securitycontext.GetUserInfo()[5])
    rec.BranchCode = config.securitycontext.GetUserInfo()[4]
  else:
    #-- routine untuk SetDataWithParameters
    helper = phelper.PObjectHelper(config, 'default')
    data = parameter.FirstRecord

#    batchId = int(data.BatchId)
#    beginNo = int(data.BeginNo)
    BeginDate = data.BeginDate
    EndDate = data.EndDate
    IsAllCabang = data.IsAllCabang
    BranchCode = data.BranchCode
    SearchCategory = data.SearchCategory
    SearchText = data.SearchText
    IsSPV = data.IsSPV
    DateCategory = data.DateCategory
    SortCategory = data.SortCategory
    LimitData = data.LimitData
    try:

      res = RunSQLTransactionList(config ,data)

      uipTransaksi = uideflist.uipTransaction.Dataset

      rownum    = 0
      showCount = 0
      BranchList = {}
      while not res.Eof : #and showCount < MAX_TRANSACTION:
          rownum += 1
#        if rownum >= beginNo :
          showCount += 1
          rec = uipTransaksi.AddRecord()
          transactionId = int(res.TransactionId)
          rec.SetFieldAt(0, 'PObj:Transaction#TransactionId=%d ' % transactionId)
          #rec.rownum = rownum
          rec.TransactionId = transactionId


          rec.TransactionNo = res.TransactionNo
          TglTrans = res.TransactionDate
          rec.TransactionDate = config.ModLibUtils.EncodeDate(TglTrans[0], TglTrans[1], TglTrans[2])
          TglAktual = res.ActualDate
          rec.ActualDate = config.ModLibUtils.EncodeDate(TglAktual[0], TglAktual[1], TglAktual[2])
          rec.Inputer = res.Inputer
          rec.Amount = res.Amount
          rec.DonorNo = res.DonorNo
          rec.DonorName = res.DonorName
          rec.ReferenceNo = res.ReferenceNo
          rec.Description = res.Description
          rec.TransactionCode = res.TransactionCode
          rec.AuthStatus = res.AuthStatus
          rec.IsPosted = res.IsPosted
          rec.IsPostedMir = res.IsPosted
          rec.BranchCode = res.BranchCode
          rec.ChannelName = res.AccountName

          if not BranchList.has_key(rec.BranchCode):
            oBranch = helper.GetObject('Branch',rec.BranchCode)
            if not oBranch.isnull:
              BranchList[rec.BranchCode] = oBranch.BranchName
              
          rec.BranchName = BranchList[rec.BranchCode]
              


          """
          # Get Detil
          resDetil = config.CreateSQL("\
            select * from TransactionItem \
            where TransactionId = %d \
            order by TransactionItemId" % transactionId).rawresult

          detilrownum    = 1
          while not resDetil.Eof and detilrownum <= MAX_DETAIL:
            recDetil = rec.uipTransactionItem.AddRecord()
            ItemId = int(resDetil.TransactionItemId)
            recDetil.SetFieldAt(0, 'PObj:TransactionItem#TransactionItemId=%d' % ItemId)
            recDetil.RefAccountNo = resDetil.RefAccountNo
            recDetil.RefAccountName = resDetil.RefAccountName
            recDetil.TransactionItemId = resDetil.TransactionItemId
            recDetil.CurrencyCode = resDetil.CurrencyCode
            recDetil.MutationType = resDetil.MutationType
            recDetil.Amount = resDetil.Amount
            recDetil.Rate = resDetil.Rate
            recDetil.Description = resDetil.Description
            recDetil.ParameterJournalId = resDetil.ParameterJournalId

            detilrownum += 1
            resDetil.Next()
          # -- end while
          """

        #-end if
          res.Next()

      #-- end while
    except:
      raise
  #--if.else

def RunSQLTransactionList(config ,param):

  BeginDate = param.BeginDate
  EndDate = param.EndDate
  IsAllCabang = param.IsAllCabang
  BranchCode = param.BranchCode
  SearchCategory = param.SearchCategory
  SearchText = param.SearchText
  IsSPV = param.IsSPV
  DateCategory = param.DateCategory
  SortCategory = param.SortCategory
  LimitData = param.LimitData
  RangeAmountFrom = param.RangeAmountFrom
  RangeAmountTo = param.RangeAmountTo
  
  sBeginDate = config.FormatDateTime('yyyy-mm-dd',BeginDate)
  sEndDate = config.FormatDateTime('yyyy-mm-dd',EndDate)
  
  addParam = ''
  orderBy = ''

  if DateCategory == 1:
    addParam += " ActualDate >= '%s' and ActualDate <='%s' " % (sBeginDate,sEndDate)
  else :
    addParam += " TransactionDate >= '%s' and TransactionDate <='%s' " % (sBeginDate,sEndDate)
  # end if else

  addParam += " and Amount between %s and %s " % (str(RangeAmountFrom),str(RangeAmountTo))
  
  
  if IsAllCabang == 'F' :
    addParam += " and a.BranchCode='%s' " % BranchCode
  # end if

  if not IsSPV :
    addParam += " and Inputer='%s' " % config.securitycontext.InitUser
  # end if

  if SearchCategory != 0:
    SearchCategoryList = {
      1 : 'TransactionNo',
      2 : 'DonorNo',
      3 : 'DonorName',
      4 : 'Description',
      5 : 'ReferenceNo',
    }
    addParam += " and upper(%s) like '%%%s%%'" %(SearchCategoryList[SearchCategory],SearchText.upper())
  # end if

  OrderCategoryList = {
    1 : 'ActualDate',
    2 : 'TransactionDate',
    3 : 'TransactionNo',
    4 : 'DonorNo',
    5 : 'DonorName',
    6 : 'AccountName',
  }

  orderBy = OrderCategoryList[SortCategory]

  sSQL = "\
    select a.*,b.accountname from Transaction a \
    left outer join financialaccount b \
    on (a.channelaccountno=b.accountno) \
    where %s \
    order by %s asc \
    Limit %d " % (addParam,orderBy,LimitData)
    
  return config.CreateSQL(sSQL).rawresult

def GetTransactionList(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""])

  dsTransaction = returns.AddNewDatasetEx(
        'transaction',
        ';'.join(
        ['TransactionDate : string' ,
         'ActualDate : string' ,
         'Inputer : string' ,
         'Amount : float',
         'DonorNo : string',
         'DonorName : string',
         'ReferenceNo : string',
         'Description : string',
         'TransactionCode : string',
         'TransactionNo : string',
         'AuthStatus : string',
         'BranchCode : string',
         'ChannelName : string',
         'IsPosted : string',
         'BranchName : string',
        ])
    )

  try:
    param = params.FirstRecord

    res = RunSQLTransactionList(config ,param)
         
    rownum    = 0
    showCount = 0
    BranchList = {}
    while not res.Eof :
      rec = dsTransaction.AddRecord()

      rec.TransactionNo = res.TransactionNo
      TglTrans = res.TransactionDate
      rec.TransactionDate = '%s-%s-%s' % (TglTrans[2],TglTrans[1],TglTrans[0]) # config.ModLibUtils.EncodeDate(TglTrans[0], TglTrans[1], TglTrans[2])
      TglAktual = res.ActualDate
      rec.ActualDate = '%s-%s-%s' % (TglAktual[2],TglAktual[1],TglAktual[0])  #config.ModLibUtils.EncodeDate(TglAktual[0], TglAktual[1], TglAktual[2])
      rec.Inputer = res.Inputer
      rec.Amount = res.Amount
      rec.DonorNo = res.DonorNo
      rec.DonorName = res.DonorName
      rec.ReferenceNo = res.ReferenceNo
      rec.Description = res.Description
      rec.TransactionCode = res.TransactionCode
      rec.AuthStatus = res.AuthStatus
      rec.IsPosted = res.IsPosted
      rec.BranchCode = res.BranchCode
      rec.ChannelName = res.AccountName
      


      if not BranchList.has_key(rec.BranchCode):
        oBranch = helper.GetObject('Branch',rec.BranchCode)
        if not oBranch.isnull:
          BranchList[rec.BranchCode] = oBranch.BranchName
        # end if
      # end if

      rec.BranchName = BranchList[rec.BranchCode]
      res.Next()
    # end while
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])


def JurnalTransaksi(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""])
    
  data = params.FirstRecord
  try :
    oTran = helper.GetObject('Transaction', data.TransactionId)
    if oTran.IsPosted == 'T':
      status.Is_Err = 1
      status.Err_Message = 'Transaksi sudah diposting'
    else:
      st, errmsg = oTran.CreateJournal()
      status.Is_Err = st
      status.Err_Message = errmsg
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
    
def PrintKwitansi(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""],
    ["Stream_Name",""])

  data = params.FirstRecord
  oTran = helper.GetObject('Transaction', data.TransactionId)
  
  try:
    raise '','tes'
    filename = oTran.GetKwitansi()
    sw = returns.AddStreamWrapper()
    sw.Name = 'Kwitansi'
    sw.LoadFromFile(filename)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)


    status.Stream_Name = sw.Name

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

