import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config, parameter, returnpacket):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  
  pass
  
def Print(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(
    ["Is_Err",0],
    ["Err_Message",""],
    ["Stream_Name",""])

  data = params.FirstRecord
  oTran = helper.GetObject('Transaction', data.TransactionId)
  
  try:
    filename = oTran.GetKwitansi()
    sw = returns.AddStreamWrapper()
    sw.Name = 'Kwitansi'
    sw.LoadFromFile(filename)
    #sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)
    sw.MIMEType = 'application/msword'

    status.Stream_Name = sw.Name

  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])


    