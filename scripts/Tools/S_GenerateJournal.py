import sys
import com.ihsan.foundation.pobjecthelper as phelper

def GenerateAll(config, parameters, returnpacket):
    status = returnpacket.CreateValues(["Is_Err", 0], ["Err_Message", ""])

    try:
      rec = parameters.FirstRecord
      helper = phelper.PObjectHelper(config)
      corporate = helper.CreateObject('Corporate')
      
      cabang = config.SecurityContext.GetUserInfo()[4]      
      filename = corporate.GetUserHomeDir() + "kontrolbatch_cabang.txt"

      PrintKontrolCabang(config, cabang, filename)
      
      sw = returnpacket.AddStreamWrapper()
      sw.LoadFromFile(filename)
      sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

    except:
      status.Is_Err = 1
      status.Err_Message = str(sys.exc_info()[1])

def KontrolPusat(config, parameters, returnpacket):
    status = returnpacket.CreateValues(["Is_Err", 0], ["Err_Message", ""])

    try:
      rec = parameters.FirstRecord
      helper = phelper.PObjectHelper(config)
      corporate = helper.CreateObject('Corporate')
      
      filename = corporate.GetUserHomeDir() + "kontrolbatch_pusat.txt"

      PrintKontrolPusat(config, filename)
      
      sw = returnpacket.AddStreamWrapper()
      sw.LoadFromFile(filename)
      sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(filename)

    except:
      status.Is_Err = 1
      status.Err_Message = str(sys.exc_info()[1])


def PrintKontrolCabang(config, cabang, filename):
    fh = open(filename, "w")
    try:
        fh.write("DAFTAR TRANSAKSI BELUM OTORISASI DALAM BATCH\n")
        fh.write("--------------------------------------------\n\n")
        
        res = config.CreateSQL("select b.BatchNo, b.Inputer, count(*),b.Description \
          from Transaction a, TransactionBatch b \
          where a.BatchId = b.BatchId \
            and a.AuthStatus = 'F' and b.BranchCode = '%s' \
            group by b.BatchNo, b.Inputer, b.Description" % cabang).rawresult
            
        fh.write("%20s %20s %7s %s\n" % ("nomor batch", "user", "jumlah", "Nama Batch"))
        while not res.Eof:
            fh.write("%20s %20s %7d %s\n" % (res.BatchNo, res.Inputer,
              res.GetFieldValueAt(2),res.GetFieldValueAt(3)))
        
            res.Next()
        #-- while
    finally:
        fh.close()

def PrintKontrolPusat(config, filename):
    fh = open(filename, "w")
    try:
        fh.write("DAFTAR TRANSAKSI BELUM OTORISASI\n")
        fh.write("--------------------------------\n\n")
        
        res = config.CreateSQL("select kode_cabang_transaksi, count(*) \
          from transaksi where status_otorisasi = 0 \
          group by kode_cabang_transaksi \
          order by kode_cabang_transaksi").rawresult
            
        fh.write("%10s %10s\n" % ("cabang", "jumlah"))
        while not res.Eof:
            fh.write("%10s %10d\n" % (res.kode_cabang_transaksi,
              res.GetFieldValueAt(1)))
        
            res.Next()
        #-- while
    finally:
        fh.close()

    