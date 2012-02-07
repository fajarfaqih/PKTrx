import com.ihsan.foundation.pobjecthelper as phelper
import sys
import pyFlexcel
import os


def FormSetDataEx(uideflist, parameter) :

  rec = uideflist.uipData.Dataset.AddRecord()

  BranchCode = str(uideflist.config.SecurityContext.GetUserInfo()[4])
  BranchName = str(uideflist.config.SecurityContext.GetUserInfo()[5])

  rec.SetFieldByName('LBranch.BranchCode', BranchCode)
  rec.SetFieldByName('LBranch.BranchName', BranchName)

def GetSummaryBeginBalance(config,params,returns):

  status = returns.CreateValues(
    ['Is_Err',0],
    ['Err_Message','']
  )

  try :
    helper = phelper.PObjectHelper(config)
    corporate = helper.CreateObject('Corporate')
    PrintHelper = helper.CreateObject('PrintHelper')
    workbook = PrintHelper.LoadExcelTemplate('tplBBalanceSummary')
    
    rec = params.FirstRecord
    BranchCode = rec.BranchCode
    
    oBranch = helper.GetObject('Branch', BranchCode)


    # -- PIUTANG KARYAWAN ----
    workbook.ActivateWorksheet('PiutangKaryawan')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-EMP-' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)
    
    # -- INVESTASI KARYAWAN ----
    workbook.ActivateWorksheet('InvestasiKaryawan')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-EMPINVS' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)

    # -- INVESTASI NON KARYAWAN ----
    workbook.ActivateWorksheet('InvestasiNonKaryawan')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-EXTINVS' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)
    
    # -- PROJECT ----
    workbook.ActivateWorksheet('Project')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-PROJ' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)
    
    # -- PROGRAM ----
    workbook.ActivateWorksheet('Program')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-PROG' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)
    
    # -- PIUTANG EKSTER ----
    workbook.ActivateWorksheet('PiutangEksternal')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-EXT-' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, ds.Amount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)

    # -- KAS / BANK ----
    workbook.ActivateWorksheet('KasBank')

    sOQL = "select from AccountTransactionItem \
        [ LTransaction.TransactionNo LLIKE 'BB-CB' \
          and BranchCode = :BranchCode \
        ] \
        ( \
         TransactionItemId, \
         AccountNo, \
         LFinancialAccount.AccountName, \
         Amount, \
         EkuivalenAmount, \
         CurrencyCode, \
         LCurrency.Short_Name, \
         self \
        ) then order by AccountNo;"

    oql = config.OQLEngine.CreateOQL(sOQL)
    oql.SetParameterValueByName('BranchCode', BranchCode)
    oql.ApplyParamValues()

    oql.active = 1
    ds  = oql.rawresult

    TotalSaldo = 0.0
    i = 0

    while not ds.Eof:
      row = i + 6

      workbook.SetCellValue(row, 1, str(i+1))
      workbook.SetCellValue(row, 2, ds.AccountNo)
      workbook.SetCellValue(row, 3, ds.AccountName)
      workbook.SetCellValue(row, 4, "%s - %s" % (ds.CurrencyCode, ds.Short_Name))
      workbook.SetCellValue(row, 5, ds.Amount)
      workbook.SetCellValue(row, 6, ds.EkuivalenAmount)

      TotalSaldo += ds.EkuivalenAmount

      ds.Next()
      i += 1

    # end while

    workbook.SetCellValue(2, 3, oBranch.BranchName)
    workbook.SetCellValue(3, 3, TotalSaldo)
    
    #--- SAVE FILE TO RESULT DIR
    FileName = 'BeginBalanceSummary.xls'

    FullFileName = corporate.GetUserHomeDir() + '\\' + FileName
    if os.access(FullFileName, os.F_OK) == 1:
        os.remove(FullFileName)
    workbook.SaveAs(FullFileName)
    

    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(FullFileName)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(FullFileName)

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])

