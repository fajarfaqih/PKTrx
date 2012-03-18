import pyFlexcel
import os
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def PrintKontrolSaldoAwal(config, params, returns):
  status = returns.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()

  try :
    try:
      helper = phelper.PObjectHelper(config)
      corporate = helper.CreateObject('Corporate')
      PrintHelper = helper.CreateObject('PrintHelper')
      workbook = PrintHelper.LoadExcelTemplate('tplBBalanceCheck')

      workbook.ActivateWorksheet('data')

      # Saldo Accounting
      SQLText = " \
         select \
            ji.fl_account , \
            ai.branch_code, \
            sum(CASE \
                WHEN ac.account_type in ('A', 'X') THEN (ji.amount_debit - ji.amount_credit) * nilai_kurs \
                ELSE (ji.amount_credit - ji.amount_debit) * nilai_kurs \
                 END )AS net_amount \
         from \
                accounting.account ac, \
                accounting.accountinstance ai, \
                accounting.journal j, \
                accounting.journalitem ji , \
                accounting.accounthierarchy ah \
         where ai.accountinstance_id=ji.accountinstance_id \
              and ac.account_code = ai.account_code \
              and j.journal_no = ji.fl_journal \
              and ah.fl_childaccountcode=ai.account_code \
              and ah.fl_parentaccountcode in ('1110101','1110201') \
              and j.journal_date < '2011-01-01' \
           group by ji.fl_account ,ai.branch_code \
       "
      ds = config.CreateSQL(SQLText).RawResult

      LsAccountBalance = {}
      while not ds.Eof:
        LsAccountBalance[ds.fl_account, ds.branch_code] = ds.net_amount or 0.0
        ds.Next()

      # Saldo BANK
      row = 3
      workbook.SetCellValue(row, 1, 'SALDO AWAL BANK')
      SQLText = "select br.branchcode,branchname, tran.saldo from transaction.branch br \
          left outer join ( \
            select f.branchcode , \
            sum(case when ti.mutationtype ='D' then ti.ekuivalenamount \
                else (-1 * ti.ekuivalenamount) end) as saldo \
            from transaction.financialaccount f, \
                transaction.cashaccount c, \
                transaction.accounttransactionitem ac, \
                transaction.transactionitem ti, \
                transaction.transaction t \
            where financialaccounttype = 'C' \
            and f.accountno = c.accountno \
            and ac.accountno = f.accountno \
            and ti.transactionitemid = ac.transactionitemid \
            and t.transactionid = ti.transactionid \
            and t.actualdate < '2011-01-01' \
            and c.cashaccounttype = 'A' \
            group by f.branchcode) tran \
          on (tran.branchcode = br.branchcode) \
          order by branchcode"

      ds = config.CreateSQL(SQLText).RawResult
      
      accountcode = '1110201'
      while not ds.Eof:
        row += 1
        branchcode = ds.branchcode
        workbook.SetCellValue(row, 2, branchcode)
        workbook.SetCellValue(row, 3, ds.branchname)
        workbook.SetCellValue(row, 4, ds.saldo)
        if LsAccountBalance.has_key((accountcode, branchcode )):
          workbook.SetCellValue(row, 5, LsAccountBalance[accountcode, branchcode])
        else:
          workbook.SetCellValue(row, 5, 0.0)
        #end if else
        
        ds.Next()
      # end while

      # Saldo Kas
      row += 1
      workbook.SetCellValue(row, 1, 'SALDO AWAL KAS')
      SQLText = "select br.branchcode,branchname, tran.saldo from transaction.branch br \
          left outer join ( \
            select f.branchcode , \
            sum(case when ti.mutationtype ='D' then ti.ekuivalenamount \
                else (-1 * ti.ekuivalenamount) end) as saldo \
            from transaction.financialaccount f, \
                transaction.cashaccount c, \
                transaction.accounttransactionitem ac, \
                transaction.transactionitem ti, \
                transaction.transaction t \
            where financialaccounttype = 'C' \
            and f.accountno = c.accountno \
            and ac.accountno = f.accountno \
            and ti.transactionitemid = ac.transactionitemid \
            and t.transactionid = ti.transactionid \
            and t.actualdate < '2011-01-01' \
            and c.cashaccounttype = 'R' \
            group by f.branchcode) tran \
          on (tran.branchcode = br.branchcode) \
          order by branchcode"

      ds = config.CreateSQL(SQLText).RawResult

      accountcode = '1110101'
      while not ds.Eof:
        row += 1
        branchcode = ds.branchcode
        workbook.SetCellValue(row, 2, branchcode)
        workbook.SetCellValue(row, 3, ds.branchname)
        workbook.SetCellValue(row, 4, ds.saldo)
        if LsAccountBalance.has_key((accountcode, branchcode )):
          workbook.SetCellValue(row, 5, LsAccountBalance[accountcode, branchcode])
        else:
          workbook.SetCellValue(row, 5, 0.0)
        #end if else

        ds.Next()
      # end while
      #--- SAVE FILE TO RESULT DIR
      FileName = 'BeginBalanceCheck.xls'

      FullFileName = corporate.GetUserHomeDir() + '\\' + FileName
      if os.access(FullFileName, os.F_OK) == 1:
          os.remove(FullFileName)
      workbook.SaveAs(FullFileName)

    finally:
      workbook = None


    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(FullFileName)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(FullFileName)

  except:
    status.Is_Error = 1
    status.Error_Message = str(sys.exc_info()[1])
    
