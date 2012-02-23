import sys
import com.ihsan.foundation.pobjecthelper as phelper
import com.ihsan.util.customidgenAPI as customidgenAPI

FundEntity = {
  0 : '',
  1 : 'Zakat',
  2 : 'Infaq',
  3 : 'Wakaf',
  4 : 'Amil',
  5 : 'Non Halal',
}
def FormSetDataEx(uideflist,params):
  config = uideflist.config

  Now = config.Now()
  recData = uideflist.uipData.Dataset.AddRecord()
  recData.TransactionDate = int(Now) - 1
  
def PrintNotaDinas(config,params,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage',''],
    ['Tanggal',''],
    ['TotalAmount',0.0],
    ['BranchCashBalance',0.0],
    ['BankCashBalance',0.0],
    ['OtherBankBalance',0.0],
    ['Nomor','']
  )
  dsData = returns.AddNewDatasetEx(
    'NotaDinas',
    ';'.join([
      'COA: string',
      'BudgetOwner: string',
      'BudgetCode: string',
      'Description: string',
      'FundEntity: string',
      'Nominal: float',
      'TransactionNo: string',
    ])
  )
  
  try :
    helper = phelper.PObjectHelper(config)
    BranchCode = config.SecurityContext.GetUserInfo()[4]
    TransDate = params.FirstRecord.TransactionDate

    filter = {}
    filter['DATE'] = config.FormatDateTime('yyyy-mm-dd', TransDate)
    filter['BRANCHCODE'] = BranchCode

    # Generate Nomor Nota Dinas
    y,m,d = config.ModLibUtils.DecodeDate(config.Now())[:3]
    FormatedDate = str(y) + str(m).zfill(2) + str(d).zfill(2)
#    raise '',FormatedDate
#    BranchCode = config.SecurityContext.GetUserInfo()[4]

#    prefixNumber = 'ND-%s-%s' % (str(y),BranchCode)
#    customid = customidgenAPI.custom_idgen(config)
#    customid.PrepareGetID('NOTADINAS', prefixNumber)
#    config.BeginTransaction()
#    try:
#      id = customid.GetLastID()
#      strID = str(id).zfill(6)
#      customid.Commit()
#      config.Commit()
#    except:
#      customid.Cancel()
#      config.Rollback()
#      raise '', str(sys.exc_info()[1])

#    recData.Nomor = prefixNumber + '-' + strID
    status.Nomor = 'ND-%s-%s' % (FormatedDate,BranchCode)


    status.Tanggal = config.FormatDateTime('dd/mm/yyyy', TransDate)

    # Get Cash Balance
    oBranchCash = helper.GetObjectByNames(
       'BranchCash',
       { 'BranchCode' : BranchCode,
         'CurrencyCode' : '000'}
       )
    if not oBranchCash.isnull :
      status.BranchCashBalance = oBranchCash.GetBalanceByDate(TransDate)

    # Get Bank Balance
    s = " \
      SELECT FROM BankCash \
      [ \
        BranchCode = :BranchCode and \
        CurrencyCode = '000' \
      ] \
      ( \
        AccountNo, \
        AccountName, \
        Balance, \
        Self \
      ) \
      THEN ORDER BY AccountNo;"


    oql = config.OQLEngine.CreateOQL(s)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult
    
    while not ds.Eof :
      oBank = helper.GetObject('BankCash',ds.AccountNo)
      if oBank.CashCode == 'BMD02' :
        status.BankCashBalance += oBank.GetBalanceByDate(TransDate)
      else:
        status.OtherBankBalance += oBank.GetBalanceByDate(TransDate)
      ds.Next()
    # end while
    
    sSQL = "select b.TransactionItemId,b.Amount,b.Description,b.AccountCode,c.FundEntity,a.TransactionNo \
            from Transaction a, TransactionItem b , AccountTransactionItem c \
            where a.TransactionId=b.TransactionId \
              and a.TransactionCode in (select transactioncode from transactiontype where grouptag='EXPENSE') \
              and a.ActualDate = '%(DATE)s' \
              and a.BranchCode = '%(BRANCHCODE)s' \
              and b.TransactionItemId = c.TransactionItemId \
              and b.MutationType = 'D' \
            " % filter
    
    sSQL += "union select b.TransactionItemId,b.Amount,b.Description,b.AccountCode, 4 as FundEntity , a.TransactionNo \
            from Transaction a, TransactionItem b \
            where a.TransactionId=b.TransactionId \
              and a.TransactionCode = 'CO' \
              and a.ActualDate = '%(DATE)s' \
              and a.BranchCode = '%(BRANCHCODE)s' \
              and b.MutationType = 'D' \
            " % filter

    sSQL += " order by TransactionItemId "
    
    resSQL = config.CreateSQL(sSQL).rawresult
    
    if resSQL.Eof :
      raise '','Tidak Ada Data Pengeluaran'

    TotalAmount = 0.0
    while not resSQL.Eof :
      recData = dsData.AddRecord()
      recData.COA = resSQL.AccountCode or ''
      recData.Description = resSQL.Description
      recData.FundEntity = FundEntity[resSQL.FundEntity or 0]
      recData.Nominal = resSQL.Amount
      recData.TransactionNo = resSQL.TransactionNo

      oBudgetTrans = helper.GetObject('BudgetTransaction',resSQL.TransactionItemId)
      if not oBudgetTrans.isnull :
        recData.BudgetOwner = oBudgetTrans.LBudget.LBudgetItem.LOwner.OwnerName
        recData.BudgetCode = oBudgetTrans.LBudget.BudgetCode

      TotalAmount += recData.Nominal
      resSQL.Next()
    # end while
    
    status.TotalAmount = TotalAmount
  except :
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])
