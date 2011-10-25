import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  
  helper = phelper.PObjectHelper(config)

  status = returnpacket.CreateValues(
        ['Is_Err',0],
        ['Err_Message','']
      )
  
  formatstr = 'dd-mm-yyyy'
  strDate = config.FormatDateTime(formatstr,config.Now())
  strSQL = " \
    select sum(case when b.mutationtype='D' then b.Amount \
               else 0.0 end) as Debet, \
           sum(case when b.mutationtype='C' then b.Amount \
               else 0.0 end) as Credit, \
           c.accountno \
    from transaction.transaction a, transaction.transactionitem b, transaction.accounttransactionitem c \
    where a.transactionid=b.transactionid \
          and b.transactionitemid = c.transactionitemid \
          and transactiondate=to_date('%s','%s') \
          group by c.accountno " % (strDate,formatstr) ;
  
  rsListAccount = config.CreateSQL(strSQL).RawResult
  config.BeginTransaction()
  try:
    while not rsListAccount.Eof:
      oAccount = helper.GetObject('FinancialAccount',rsListAccount.AccountNo)
      oLastDailyBalance = oAccount.GetLastDailyBalance()
      if oLastDailyBalance.GetAsTDateTime('BalanceDate') == int(config.Now()):
        oLastDailyBalance.CloseDay(rsListAccount.Debet,rsListAccount.Credit)
      rsListAccount.Next()         
    # end while
    
    # Pastikan seluruh dailybalance ditutup
    config.ExecSQL('Update DailyBalance set IsClosed=\'T\' where IsClosed = \'F\'')
    config.Commit()
  except :
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])  
  #--end try
  return 1
