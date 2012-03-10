import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist, parameter) :
  config = uideflist.Config
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.UserBranchCode = str(config.SecurityContext.GetUserInfo()[4])
  rec.UserBranchName = str(config.SecurityContext.GetUserInfo()[5])
  rec.HeadOfficeCode = config.SysVarIntf.GetStringSysVar('OPTION','HeadOfficeCode')
  
  Now = config.Now()

  y = config.ModLibUtils.DecodeDate(Now)[0]
  rec.BeginDate = config.ModLibUtils.EncodeDate(y,1,1)
  rec.EndDate = int(Now)


def AsDateTime(config,tdate):
  utils = config.ModLibUtils
  return utils.EncodeDate(tdate[0], tdate[1], tdate[2])


def SummaryEmpCA(config,params,returns):
  status = returns.CreateValues(
     ['Is_Err',0],['Err_Message',''],
     ['PeriodStr',''],['BranchName',''],
     ['BeginDateStr',''],['EndDateStr',''],
     ['BeginBalanceEkuiv',0.0],
     ['TotalDebetEkuiv',0.0],
     ['TotalCreditEkuiv',0.0],
     ['EndBalanceEkuiv',0.0],
     ['TotalDebetHist',0.0],
     ['TotalCreditHist',0.0],
  )
  
  param = params.FirstRecord
  BranchCode = param.GetFieldByName('LBranch.BranchCode')
  IsAllBranch = param.IsAllBranch
  BeginDate = param.BeginDate
  EndDate = param.EndDate
  UserBranchCode = param.UserBranchCode
  HeadOfficeCode = param.HeadOfficeCode
  MasterBranchCode = param.MasterBranchCode
  
  try:
    helper = phelper.PObjectHelper(config)
    
    # Set BranchName
    if BranchCode not in ['',None] :
      corporate = helper.CreateObject('Corporate')
      CabangInfo = corporate.GetCabangInfo(BranchCode)

      status.BranchName = CabangInfo.Nama_Cabang

    
    status.BeginDateStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    status.EndDateStr = config.FormatDateTime('dd-mm-yyyy',EndDate)
    if BeginDate == EndDate :
      status.PeriodStr = config.FormatDateTime('dd-mm-yyyy',BeginDate)
    else:
      status.PeriodStr = "%s s/d %s" % (
                   config.FormatDateTime('dd-mm-yyyy',BeginDate),
                   config.FormatDateTime('dd-mm-yyyy',EndDate)
                 )
    # end if
    
    # Set DATE SQL PARAM
    sqlBeginDateParam = config.FormatDateTime('yyyy-mm-dd',BeginDate)
    sqlEndDateParam = config.FormatDateTime('yyyy-mm-dd',EndDate + 1)
    
    dsSummary = returns.AddNewDatasetEx(
     'summary',
     ';'.join([
       'NomorKaryawan: string',
       'NamaKaryawan: string',
       'BranchCode: string',
       'BranchName: string',
       'Debet: float',
       'DebetEkuiv: float',
       'Kredit: float',
       'KreditEkuiv: float',
       'TotalMutasi: float',
       'SaldoAwal: float',
       'SaldoAwalEkuiv: float',
       'SaldoAkhir: float',
       'SaldoAkhirEkuiv: float',
       'CurrencyName: string'
     ])
    )

    
    # Set BranchCodeParam
    BranchCodeParam = ''
    if IsAllBranch == 'F' :
      BranchCodeParam = " and br.branchcode='%s' " % BranchCode
    else:
      IsHeadOffice = (UserBranchCode == HeadOfficeCode)

      # Jika Bukan Kantor Pusat maka branchcode dari user login ditambah konsolidasi dengan KCPnya
      if not IsHeadOffice :
        BranchCodeParam = "and ( br.BranchCode='%(BranchCode)s'  \
                           or br.MasterBranchCode='%(BranchCode)s' ) " \
                           % {'BranchCode' : UserBranchCode}

      #end if
    # end if

    strSQL = " \
              select b.employeeidnumber, a.accountno, a.accountname, a.currencycode, c.short_name, \
              br.branchcode, br.branchname , \
              ( select sum(case when d.mutationtype='D' then d.Amount \
                           else -d.Amount \
                      end) \
              from transactionitem d, transaction e, accounttransactionitem f\
              where d.transactionid=e.transactionid \
                 and d.transactionitemid=f.transactionitemid \
                 and f.accountno = a.accountno and e.actualdate < '%(BEGINDATE)s' ) as BeginBalance, \
              ( select sum(case when d.mutationtype='D' then d.EkuivalenAmount \
                           else -d.EkuivalenAmount \
                      end) \
              from transactionitem d, transaction e, accounttransactionitem f\
              where d.transactionid=e.transactionid \
                 and d.transactionitemid=f.transactionitemid \
                 and f.accountno = a.accountno and e.actualdate < '%(BEGINDATE)s' ) as BeginBalanceEkuiv, \
                 (select sum(d.Amount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='D') as Debet, \
                 (select sum(d.EkuivalenAmount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='D') as DebetEkuiv, \
                 (select sum(d.Amount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='C') as Kredit, \
                 (select sum(d.EkuivalenAmount) \
                     from transaction.transaction c, \
                          transaction.transactionitem d, \
                          transaction.accounttransactionitem e \
                     where c.transactionid = d.transactionid and d.transactionitemid = e.transactionitemid \
                         and c.actualdate between '%(BEGINDATE)s' and '%(ENDDATE)s'  and e.accountno=a.accountno \
                         and d.mutationtype='C') as KreditEkuiv \
              from transaction.financialaccount a, transaction.accountreceivable b, transaction.currency c, branch br \
              where a.accountno = b.accountno \
                  and a.currencycode = c.currency_code \
                  and b.AccountReceivableType = 'C' \
                  and a.BranchCode = br.BranchCode \
                  %(BRANCHCODEPARAM)s \
                 order by br.branchcode, a.accountname \
                " % {
                  'BRANCHCODEPARAM' : BranchCodeParam ,
                  'BEGINDATE' : sqlBeginDateParam,
                  'ENDDATE' : sqlEndDateParam
               }

    res = config.CreateSQL(strSQL).RawResult

    while not res.Eof:
      recSum = dsSummary.AddRecord()
      #recSum.NomorKaryawan = res.AccountNo
      recSum.NomorKaryawan = str(res.EmployeeIdNumber)
      recSum.NamaKaryawan = res.AccountName
      recSum.BranchCode = res.BranchCode
      recSum.BranchName = res.BranchName
      
      recSum.CurrencyName = res.Short_Name
      recSum.Debet = res.Debet or 0.0
      recSum.DebetEkuiv = res.DebetEkuiv or 0.0
      recSum.Kredit = res.Kredit or 0.0
      recSum.KreditEkuiv = res.KreditEkuiv or 0.0
      recSum.TotalMutasi = (res.Debet or 0.0 ) - ( res.Kredit or 0.0)
      
      
      #AccountR = helper.GetObject('AccountReceivable',res.AccountNo)
      SaldoAwal = res.BeginBalance or 0.0 #AccountR.GetBalanceByDate(BeginDate)

      recSum.SaldoAwal = SaldoAwal
      recSum.SaldoAkhir = SaldoAwal + recSum.TotalMutasi
      
      status.BeginBalanceEkuiv += res.BeginBalanceEkuiv or 0.0
      status.TotalDebetEkuiv += res.DebetEkuiv or 0.0
      status.TotalCreditEkuiv += res.KreditEkuiv or 0.0
      status.EndBalanceEkuiv += (res.BeginBalanceEkuiv or 0.0) + (res.DebetEkuiv or 0.0) - (res.KreditEkuiv or 0.0)
      
      res.Next()
      
    # end while
    
    
    #--- GET HISTORI TRANSAKSI
    dsHist = returns.AddNewDatasetEx(
      'historitransaksi',
      ';'.join([
        'TransactionItemId: integer',
        'TransactionDate: datetime',
        'TransactionDateStr: string',
        'TransactionCode: string',
        'MutationType: string',
        'Amount: float',
        'AmountEkuivalen: float',
        'CurrencyName: string',
        'Rate: float',
        'Debet: float',
        'Kredit: float',
        'ReferenceNo: string',
        'Description: string',
        'Inputer: string',
        'TransactionNo:string',
        'Total:float',
        'AuthStatus:string',
        'AccountName:string',
        'ReturnStatus:string',
        'ReturnTransactionNo:string',
        'BranchName:string',
      ])
    )


    strSQL = "SELECT A.TRANSACTIONITEMID, C.TRANSACTIONDATE, C.TRANSACTIONCODE, C.ACTUALDATE, B.MUTATIONTYPE, \
        B.AMOUNT, B.EKUIVALENAMOUNT, C.REFERENCENO, C.DESCRIPTION, C.INPUTER, C.TRANSACTIONNO, \
        C.AUTHSTATUS, B.CURRENCYCODE, B.RATE, E.SHORT_NAME, C.CURRENCYCODE, C.RATE, D.SHORT_NAME, \
        BR.BRANCHCODE, BR.BRANCHNAME,  \
        G.ACCOUNTNAME, A.TRANSACTIONITEMID,  a.returntransactionitemid, \
          (select transactionno from \
             transaction.transaction tr, transaction.transactionitem ti \
             where tr.transactionid=ti.transactionid and ti.transactionitemid=a.returntransactionitemid) \
           as return_transactionno \
        FROM \
        transaction.ACCOUNTTRANSACTIONITEM A, \
        transaction.TRANSACTIONITEM B, \
        transaction.TRANSACTION C, \
        transaction.CURRENCY D, \
        transaction.CURRENCY E, \
        transaction.ACCOUNTRECEIVABLE F, \
        transaction.FINANCIALACCOUNT G, \
        transaction.BRANCH BR \
        WHERE A.ACCOUNTTITYPE = 'C' AND \
        A.TransactionItemId = B.TransactionItemId AND \
        B.TRANSACTIONID = C.TRANSACTIONID AND \
        C.CURRENCYCODE = D.CURRENCY_CODE AND \
        B.CURRENCYCODE = E.CURRENCY_CODE AND \
        A.ACCOUNTNO = F.ACCOUNTNO AND \
        F.AccountNo = G.AccountNo AND \
        BR.BranchCode = B.BranchCode AND \
        ( C.ACTUALDATE BETWEEN '%(BEGINDATE)s' AND '%(ENDDATE)s' %(BRANCHCODEPARAM)s ) \
        ORDER BY C.ACTUALDATE ASC, A.TRANSACTIONITEMID ASC \
        " % { 'BRANCHCODEPARAM' : BranchCodeParam ,
              'BEGINDATE' : sqlBeginDateParam,
              'ENDDATE' : sqlEndDateParam
        }

    ds = config.CreateSQL(strSQL).RawResult

    ds.First()

    # dict untuk status otorisasi
    stAuth = {'T':'Sudah Otorisasi','F':'Belum Otorisasi'}

    # dict untuk status pengembalian LPJ
    stReturn = {0 : 'Belum ada LPJ', 1 : 'Sudah Ada LPJ' }
    
    while not ds.Eof:
      recHist = dsHist.AddRecord()
      recHist.TransactionItemId = ds.TransactionItemId
      recHist.TransactionDate = AsDateTime(config, ds.ActualDate)
      recHist.TransactionDateStr = config.FormatDateTime('dd-mmm-yyyy',recHist.TransactionDate)
      recHist.TransactionCode = ds.TransactionCode
      recHist.MutationType = ds.MutationType

      TranCurrencyCode = ds.CurrencyCode_1
      TranCurrencyName = ds.Short_Name_1
      TransRate        = ds.Rate_1

      if ds.CurrencyCode != TranCurrencyCode and ds.CurrencyCode == '000':
        CurrencyCode = TranCurrencyCode
        CurrencyName = TranCurrencyName
        Rate = TransRate
        Amount      = ds.Amount / Rate
      else :
        CurrencyCode = ds.CurrencyCode
        CurrencyName = ds.Short_Name
        Rate = ds.Rate
        Amount = ds.Amount
      # end if

      recHist.Amount = Amount
      recHist.AmountEkuivalen = ds.EkuivalenAmount
      recHist.Rate = Rate
      recHist.CurrencyName = TranCurrencyName

      if ds.MutationType == 'D' :
        recHist.Debet = ds.EkuivalenAmount
        #recSaldo.TotalBalance += ds.EkuivalenAmount
        status.TotalDebetHist += ds.EkuivalenAmount
      else:
        recHist.Kredit = ds.EkuivalenAmount
        #recSaldo.TotalBalance -= ds.EkuivalenAmount
        status.TotalCreditHist += ds.EkuivalenAmount
      # endif

      recHist.ReferenceNo = ds.ReferenceNo
      recHist.Description = ds.Description
      recHist.Inputer = ds.Inputer
      recHist.TransactionNo = ds.TransactionNo
      recHist.AccountName = ds.AccountName
      recHist.AuthStatus = stAuth[ds.AuthStatus]
      recHist.ReturnStatus = stReturn[ds.ReturnTransactionItemid not in [0,None,'']]
      recHist.ReturnTransactionNo = ds.return_transactionno
      recHist.BranchName = ds.BranchName

      ds.Next()
    #-- while
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
