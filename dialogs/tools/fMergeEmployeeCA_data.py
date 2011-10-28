import com.ihsan.foundation.pobjecthelper as phelper
import sys

def FormSetDataEx(uideflist,params):
  config = uideflist.config
  
  recData1 = uideflist.uipData1.Dataset.AddRecord()
  recData1.BranchCode = config.SecurityContext.GetUserInfo()[4]
  recData2 = uideflist.uipData2.Dataset.AddRecord()
  recData2.BranchCode = config.SecurityContext.GetUserInfo()[4]
  
def ExecuteSQL(config,sSQL):
  sqlRes = config.ExecSQL(sSQL)

  if sqlRes == -9999:
    raise "SQL Error", config.GetDBConnErrorInfo()
def MergeEmployeeCashAdvance(config,params,returns):
  status = returns.CreateValues(
    ['IsErr',0],
    ['ErrMessage','']
  )

  config.BeginTransaction()
  try :
    param = params.FirstRecord
    
    helper = phelper.PObjectHelper(config)
    
    SourceAccountNo = param.SourceAccountNo
    ToAccountNo = param.ToAccountNo

    oSourceEmployeeCA = helper.GetObject("EmployeeCashAdvance",SourceAccountNo)
    oEmployee = helper.GetObject("VEmployee",oSourceEmployeeCA.EmployeeIdNumber)


    if not oEmployee.isnull:
      message = "Proses tidak dapat dilanjutkan karena data karyawan yang akan digabungkan masih ada pada database php."
      message += "\nSilahkan hubungi administrator database untuk menghapus atau menggabungkan data karyawan dengan data berikut :"
      message += "\n- ID\t: %d" % oSourceEmployeeCA.EmployeeIdNumber
      message += "\n- Nama\t: %s" % oEmployee.EmployeeName
      raise 'PERINGATAN', message
    
    
    oToEmployeeCA = helper.GetObject("EmployeeCashAdvance",ToAccountNo)
    
    sBackup = "\
         insert into logmergeaccount (transactionitemid,oldaccount,newaccount,mergedate) \
         select transactionitemid,accountno,'%s','%s' \
         from accounttransactionitem where accountno='%s' " % ( ToAccountNo,config.FormatDateTime('yyyy-mm-dd',config.Now()),SourceAccountNo)
         
    ExecuteSQL(config,sBackup)
    
    sUpdate = "update accounttransactionitem set accountno='%s' where accountno='%s' " % (ToAccountNo,SourceAccountNo)
    ExecuteSQL(config,sUpdate)

    oToEmployeeCA.Balance += oSourceEmployeeCA.Balance
    
    oSourceEmployeeCA.Delete()

    config.Commit()
  except:
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

