import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson as json

class RData:
  def __init__(self, sData=None):
    def convert(data):
      # convert json load format to native python dictionary
      if isinstance(data, unicode):
        return str(data)
      elif isinstance(data, dict):
        return dict(map(convert, data.iteritems()))
      elif isinstance(data, (list, tuple)):
        return type(data)(map(convert, data))
      else:
        return data
    
    if sData != None:
      self.__dict__ = convert(json.loads(sData))

  def GetString(self):
    return json.dumps(self.__dict__)

def GetInfoTransaction(config, params, returns):
  #status = returns.CreateValues(
  #  ['Is_Error',0],
  #  ['Error_Message',''],
  #  ['TransactionNo', ''],
  #  ['Response' , '']
  #)
  response = RData()
  response.Is_Error = 0
  response.Error_Message = ''

  config.BeginTransaction()
  try:
    helper = phelper.PObjectHelper(config)

    # init variable for response
    

    JournalBlockId = params.FirstRecord.id_journalblock
    oTransaction = helper.GetObjectByNames('Transaction',{'JournalBlockId' : JournalBlockId})

    if oTransaction.isnull : raise '','Info Transaksi Tidak Ditemukan'
    
    response.TransactionNo = oTransaction.TransactionNo
    response.Description = oTransaction.Description
    response.ActualDate = oTransaction.GetAsTDateTime('ActualDate')
    response.Inputer = oTransaction.Inputer
    response.JournalBlockId = oTransaction.JournalBlockId
    
    response.list_transitems = []

    oItems = oTransaction.Ls_TransactionItem
    #aSQLText = " select transactionitemid from transactionitem \
    #                 where transactionid=%d " % self.TransactionId        

    #oRes = self.Config.CreateSQL(aSQLText).RawResult
    
    while not oItems.EndOfList:
      itemElmt = oItems.CurrentElement
      
      transitem = {}
      transitem['TransactionItemId'] = itemElmt.TransactionItemId
      transitem['Amount'] = itemElmt.Amount
      transitem['RefAccountNo'] = itemElmt.RefAccountNo
      transitem['RefAccountName'] = itemElmt.RefAccountName
      transitem['MutationType'] = itemElmt.MutationType
      transitem['Amount'] = itemElmt.Amount
      transitem['CurrencyCode'] = itemElmt.LCurrency.Short_Name
      transitem['Description'] = itemElmt.Description
      transitem['Rate'] = itemElmt.Rate
      transitem['EkuivalenAmount'] = itemElmt.EkuivalenAmount
      

      response.list_transitems.append(transitem)

      oItems.Next()
    # end while


    #response.Response = response.GetString()

  except:
    config.Rollback()
    response.Is_Error = 1
    response.Error_Message = str(sys.exc_info()[1])
    #config.SendDebugMsg(status.Error_Message)

  returns.CreateSimpleDataPacket().data = response.GetString()