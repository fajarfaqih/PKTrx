import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter):
    config = uideflist.config
    uip = uideflist.uipBudgetOwner
    helper = phelper.PObjectHelper(config)

    if parameter.DatasetCount != 0 :
      rec = parameter.FirstRecord
      ItemCode = rec.ItemCode
      PeriodId = rec.PeriodId

      sSQL = "\
             select * from transaction.budgetowner a \
             where exists \
                (select 1 from transaction.budget b,transaction.budgetperiod c \
                where a.ownerid=b.ownerid and b.periodid=c.periodid \
                      and c.periodid=%d ) \
             " % (PeriodId)

      res = config.CreateSQL(sSQL).rawresult

      uipData = uideflist.uipBudgetOwner.Dataset
      while not res.Eof:
        oTran = uipData.AddRecord()
        OwnerId = res.OwnerId
        oTran.SetFieldAt(0, 'PObj:BudgetOwner#OwnerId=%d' % OwnerId)
        oTran.OwnerId = OwnerId
        oTran.OwnerName = res.OwnerName

        res.Next()
      #-- while
