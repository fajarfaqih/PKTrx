
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
             from transaction.budgetowner b \
             where (b.ownerid=%d ) \
                   and a.ownerid=b.ownerid \
      )' % (Obj.OwnerId)

    rsCheckBudget = config.CreateSQL(sCheckBudget).RawResult
    if rsCheckBudget.GetFieldValueAt(0) > 0 :
       raise '','Data Budget tidak dapat dihapus karena telah digunakan sebagai referensi'
     
    sDelete = 'delete from budgetowner where ownerid=%d' % (Obj.OwnerId)
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


