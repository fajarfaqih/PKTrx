import com.ihsan.foundation.pobjecthelper as phelper
import sys
import win32com.client

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  
  helper = phelper.PObjectHelper(config)

  status = returnpacket.CreateValues(
        ['Is_Err',1],
        ['Err_Message','tes']
      )
  
  
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
    
  except :
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])  
  #--end try
  return 1
