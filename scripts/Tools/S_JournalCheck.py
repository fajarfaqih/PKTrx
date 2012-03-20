import pyFlexcel
import os
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def PrintRekapMutasiKasBank(config, params, returns):
  status = returns.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()

  try :
    try:
      helper = phelper.PObjectHelper(config)
      corporate = helper.CreateObject('Corporate')
      PrintHelper = helper.CreateObject('PrintHelper')
      workbook = PrintHelper.LoadExcelTemplate('tplMutationSummary')

      workbook.ActivateWorksheet('datatransaksi')

      # TOTAL MUTASI TRANSAKSI
      SQLText = " \
         select \
              t.transactioncode, ty.description, ti.branchcode, br.branchname, \
              sum (case when ti.mutationtype ='D' then ti.ekuivalenamount else 0.0 end) as saldo_debit, \
              sum (case when ti.mutationtype ='C' then ti.ekuivalenamount else 0.0 end) as saldo_credit \
              from transaction.financialaccount f, \
                  transaction.cashaccount c, \
                  transaction.accounttransactionitem ac, \
                  transaction.transactionitem ti, \
                  transaction.transaction t, \
                  transaction.transactiontype ty, \
                  transaction.branch br \
              where financialaccounttype = 'C' \
              and f.accountno = c.accountno \
              and ac.accountno = f.accountno \
              and ti.transactionitemid = ac.transactionitemid \
              and t.transactionid = ti.transactionid \
              and ty.transactioncode = t.transactioncode \
              and ti.branchcode = br.branchcode \
              and t.actualdate >= '2011-01-01' and t.actualdate < '2012-01-01' \
              group by ti.branchcode, t.transactioncode,ty.description,br.branchname \
              order by ti.branchcode, t.transactioncode \
      "

      ds = config.CreateSQL(SQLText).RawResult
      
      PrevBranchCode = ""
      PrevBranchName = ""
      BranchTotalDebit = 0.0
      BranchTotalCredit = 0.0
      row = 3
      while not ds.Eof:
        BranchCode = ds.BranchCode
        BranchName = ds.BranchName
        
        if PrevBranchCode != BranchCode :
          if PrevBranchCode != '' :
            workbook.SetCellValue(row, 2, "Total Cabang %s-%s" % (PrevBranchCode, PrevBranchName))
            workbook.SetCellValue(row, 3, BranchTotalDebit)
            workbook.SetCellValue(row, 4, BranchTotalCredit)
            workbook.SetCellValue(row, 5, BranchTotalDebit - BranchTotalCredit)
          
          BranchTotalDebit = 0.0
          BranchTotalCredit = 0.0
          PrevBranchCode = BranchCode
          PrevBranchName = BranchName

          row += 2
        # end if  

        Debit = ds.saldo_debit
        Credit = ds.saldo_credit
        BranchTotalDebit += Debit
        BranchTotalCredit += Credit

        workbook.SetCellValue(row, 2, "%s - %s" % (ds.transactioncode, ds.description ))
        workbook.SetCellValue(row, 3, Debit)
        workbook.SetCellValue(row, 4, Credit)

        row += 1
        ds.Next()

      # end while

      workbook.SetCellValue(row, 2, "Total Cabang %s-%s" % (BranchCode, BranchName))
      workbook.SetCellValue(row, 3, BranchTotalDebit)
      workbook.SetCellValue(row, 4, BranchTotalCredit)
      workbook.SetCellValue(row, 5, BranchTotalDebit - BranchTotalCredit)


      # TOTAL MUTASI ACCOUNTING
      workbook.ActivateWorksheet('dataaccounting')
      SQLText = " \
        select \
          tran.transactioncode,tran.trandescription, ji.branch_code, br.branchname, \
          sum(ji.amount_debit * nilai_kurs) as saldo_debit , \
          sum(ji.amount_credit * nilai_kurs) as saldo_credit \
          from  \
                accounting.account ac,  \
                accounting.accountinstance ai,  \
                accounting.journal j, \
                accounting.accounthierarchy ah , \
                accounting.branchlocation br, \
                accounting.journalitem ji \
                left outer join ( \
                 select t.transactionid,t.transactionno,t.transactioncode,  \
              ti.amount,ti.ekuivalenamount, t.journalblockid, \
              ti.transactionitemid, ty.description as trandescription \
                 from transaction.transaction t, transaction.transactionitem ti, \
              transaction.transactiontype ty \
                 where t.transactionid = ti.transactionid \
              and ty.transactioncode = t.transactioncode \
                 ) tran \
                on (ji.source_key_id = tran.transactionitemid) \
            where ai.accountinstance_id=ji.accountinstance_id  \
              and ac.account_code = ai.account_code  \
              and j.journal_no = ji.fl_journal  \
              and ah.fl_childaccountcode=ai.account_code  \
              and br.branch_code = ji.branch_code \
              and ah.fl_parentaccountcode in ('1110201','1110101') \
              and j.journal_date >= '2011-01-01' and j.journal_date < '2012-01-01' \
            group by tran.transactioncode,tran.trandescription,ji.branch_code,br.branchname  \
            order by ji.branch_code, tran.transactioncode \
      "

      ds = config.CreateSQL(SQLText).RawResult
      
      PrevBranchCode = ""
      PrevBranchName = ""
      BranchTotalDebit = 0.0
      BranchTotalCredit = 0.0
      row = 3
      while not ds.Eof:
        BranchCode = ds.Branch_Code
        BranchName = ds.BranchName
        
        if PrevBranchCode != BranchCode :
          if PrevBranchCode != '' :
            workbook.SetCellValue(row, 2, "Total Cabang %s-%s" % (PrevBranchCode, PrevBranchName))
            workbook.SetCellValue(row, 3, BranchTotalDebit)
            workbook.SetCellValue(row, 4, BranchTotalCredit)
            workbook.SetCellValue(row, 5, BranchTotalDebit - BranchTotalCredit)
          
          BranchTotalDebit = 0.0
          BranchTotalCredit = 0.0
          PrevBranchCode = BranchCode
          PrevBranchName = BranchName

          row += 2
        # end if  

        Debit = ds.saldo_debit
        Credit = ds.saldo_credit
        BranchTotalDebit += Debit
        BranchTotalCredit += Credit

        workbook.SetCellValue(row, 2, "%s - %s" % (ds.transactioncode, ds.trandescription ))
        workbook.SetCellValue(row, 3, Debit)
        workbook.SetCellValue(row, 4, Credit)

        row += 1
        ds.Next()

      # end while

      workbook.SetCellValue(row, 2, "Total Cabang %s-%s" % (BranchCode, BranchName))
      workbook.SetCellValue(row, 3, BranchTotalDebit)
      workbook.SetCellValue(row, 4, BranchTotalCredit)
      workbook.SetCellValue(row, 5, BranchTotalDebit - BranchTotalCredit)


      # Mutasi Tranasaksi
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
