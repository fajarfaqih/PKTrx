import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)

  helper = phelper.PObjectHelper(config)

  status = returnpacket.CreateValues(
        ['Is_Err',0],
        ['Err_Message',''],
        ['FormName','']
      )

  try:
    param = parameter.trparam.GetRecord(0)
    oInbox = helper.GetObjectByNames('InboxTransaction',{'TransactionId':param.TransactionId})
    
    if oInbox.isnull : raise '','Data Inbox Tidak Ditemukan'
    
    status.FormName = 'Transaksi\\' + oInbox.LParameterInbox.NamaForm

  except :
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  #--end try

  return 1

