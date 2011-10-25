
import com.ihsan.foundation.pobjecthelper as phelper
import sys

def DAFScriptMain(config,parameters,returnpacket):
  status = returnpacket.CreateValues(
        ['Is_Err',0],
        ['Err_Message','']
      ) 
  helper = phelper.PObjectHelper(config)
  Obj = config.AccessPObject(parameters.FirstRecord.key)
  if Obj.IsNull :
    raise 'PERINGATAN','Data tidak ditemukan'
  config.BeginTransaction()
  try :
    sCheckBudget = ' \
      select count(budgetid) \
      from transaction.budget a \
         where exists ( \
             select 1 \
             from transaction.budgetperiod b \
             where (b.periodid=%d or b.parentperiodid=%d ) \
                   and a.periodid=b.periodid \
      )' % (Obj.PeriodId,Obj.PeriodId)

    rsCheckBudget = config.CreateSQL(sCheckBudget).RawResult
    if rsCheckBudget.GetFieldValueAt(0) > 0 :
       raise '','Data periode anggaran ini tidak dapat dihapus karena telah digunakan sebagai referensi'
     
    sDelete = 'delete from budgetperiod where parentperiodid=%d or periodid=%d ' % (Obj.PeriodId,Obj.PeriodId)
    #raise '',sDelete
    config.ExecSQL(sDelete)
    #Obj.Delete()
    #rec = helper.LoadScript('GeneralModule.S_ObjectEditor').\
    config.Commit()
  except:
    config.Rollback()
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  # end try


