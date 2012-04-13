import pyFlexcel
import os
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config, params, returns):
  status = returns.CreateValues(["Is_Error", 0], ["Error_Message", ""])
  app = config.GetAppObject()

  try :
    try:
      helper = phelper.PObjectHelper(config)
      corporate = helper.CreateObject('Corporate')
      PrintHelper = helper.CreateObject('PrintHelper')
      workbook = PrintHelper.LoadExcelTemplate('tplListFaultTrans')

      workbook.ActivateWorksheet('data1')

      # Saldo Accounting
      SQLText = " \
        select t.transactionno, t.actualdate, t.transactiondate, \
          t.description, br.branchname, t.inputer, t.description, \
          refaccountno, refaccountname, ti.ekuivalenamount, \
          accountcode, mutationtype, ty.description as trantypedesc \
        from \
          transaction.transaction t, \
          transaction.branch br, \
          transaction.transactiontype ty, \
          transaction.transactionitem ti \
        where ty.transactioncode = t.transactioncode \
          and t.branchcode = br.branchcode \
          and ty.transactioncode = t.transactioncode \
          and t.transactionid = ti.transactionid \
          and t.transactioncode in ('CO','CI','GT') \
          and exists( \
             select 1 from transaction.transactionitem ti \
             where t.transactionid = ti.transactionid \
              and transactionitemtype ='G' \
              and ( \
                 accountcode like '1%' \
               ) \
            ) \
        order by t.branchcode,t.transactionno, ti.transactionitemid  ; \
       "
      resSQL = config.CreateSQL(SQLText).RawResult

      #oParamCorporateName = helper.GetObject('Parameter', 'CorporateName')
      #CorporateName = oParamCorporateName.GetString()

      workbook.ActivateWorksheet('data1')
      workbook.SetCellValue(1 , 1, '')
      workbook.SetCellValue(3 , 1, '')

      row = 6
      sheet = 1
      BeginBalance = 0.0
      TotalDebet = 0.0
      TotalCredit = 0.0
      PrevTransNo = ''

      while not resSQL.Eof :
        if PrevTransNo != resSQL.TransactionNo :
          if PrevTransNo != '' :
            # Set Saldo Akhir 
            #workbook.SetCellValue(row , 3, "Total")
            #workbook.SetCellValue(row , 4, TotalDebet)
            #workbook.SetCellValue(row , 5, TotalCredit)

            row += 1
          # end if

          #TotalDebet = 0.0
          #TotalCredit = 0.0 

          y, m, d = resSQL.Actualdate[:3]
          TanggalTrans = config.FormatDateTime('dd mmm yyyy',config.ModLibUtils.EncodeDate(y, m, d))

          workbook.SetCellValue(row , 1, str(resSQL.TransactionNo))
          workbook.SetCellValue(row + 1  , 1, "%s (%s)" % (str(resSQL.BranchName), TanggalTrans))
          workbook.SetCellValue(row , 2, resSQL.description)
          workbook.SetCellValue(row , 3, "Inputer : %s" % resSQL.Inputer)
          workbook.SetCellValue(row , 4, "Jenis Transaksi : %s" % resSQL.trantypedesc)

          PrevTransNo = str(resSQL.TransactionNo)
          row += 1
        # end if

        workbook.SetCellValue(row , 2, resSQL.refaccountno)
        workbook.SetCellValue(row , 3, resSQL.refaccountname)
        workbook.SetCellValue(row , 4, resSQL.mutationtype)
        workbook.SetCellValue(row , 5, resSQL.ekuivalenamount)
        #workbook.SetCellValue(row , 6, resSQL.credit_ekuiv)

        #TotalDebet += resSQL.debit_ekuiv
        #TotalCredit += resSQL.credit_ekuiv
        
        row += 1
        
        # Cek Ganti Sheet
        if row >= 65530 :
          sheet += 1
          workbook.SetCellValue(row + 1 , 1, '{ BERSAMBUNG KE SHEET data1%d }' % sheet )

          # Set To Next Sheet
          workbook.ActivateWorksheet('data%d' % sheet )
          row = 2
        # end if
          
        resSQL.Next()
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
    