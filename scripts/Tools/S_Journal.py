import sys
import com.ihsan.foundation.pobjecthelper as phelper

def GenerateAll(config, parameters, returnpacket):
  status = returnpacket.CreateValues(["Is_Err", 0], ["Err_Message", ""])
  app = config.GetAppObject()
  app.ConCreate('DJournal')
  helper = phelper.PObjectHelper(config)
  corporate = helper.CreateObject('Corporate')
      
  filename = corporate.GetUserHomeDir() + "GenerateJournalLog.txt"
  
  try:
    fh = open(filename,'w')
    try:
                  
      sSQL = "select TransactionId \
              from transaction \
              where branchcode='%s' \
                  and AuthStatus='T' \
                  and IsPosted='F' " % config.SecurityContext.GetUserInfo()[4]
      
      oRes = config.CreateSQL(sSQL).RawResult
      
      oRes.First()
      while not oRes.Eof:
        logmessage = "Proses TransactionId %d : " % oRes.TransactionId
        app.ConWrite(logmessage ,'DJournal')
        fh.write(logmessage)
        
        oTran = helper.GetObject('Transaction', oRes.TransactionId)
        st, errmsg = oTran.CreateJournal()
        if st == 2 :
          logmessage = 'Gagal ' + errmsg 
        else:
          logmessage = 'Berhasil'
        # end if
        
        app.ConWriteln(logmessage ,'DJournal')
        fh.write(logmessage + '\n')

        oRes.Next()
      # end while
                
    except:
      status.Is_Err = 1
      status.Err_Message = str(sys.exc_info()[1])
  
  finally:
    fh.close()  
  
  sw = returnpacket.AddStreamWrapper()
  sw.LoadFromFile(filename)
  sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)        