import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter):
    config = uideflist.config

    helper = phelper.PObjectHelper(config)

    if parameter.DatasetCount != 0 :
      rec = parameter.FirstRecord
      OwnerId = rec.OwnerId
      
      sSQL = "\
             select * from transaction.budgetperiod a \
             where exists \
                (select 1 from transaction.budget b \
                where a.periodid=b.periodid  \
                      and b.OwnerId=%d ) \
             and ParentPeriodID is not null \
             " % (OwnerId)

      res = config.CreateSQL(sSQL).rawresult

      uipBudgetPeriod = uideflist.uipBudgetPeriod.Dataset
      while not res.Eof:
        recBP = uipBudgetPeriod.AddRecord()
        PeriodId = res.PeriodId
        oBP = helper.GetObject('BudgetPeriod',PeriodId)
        recBP.SetFieldAt(0, 'PObj:BudgetPeriod#PeriodId=%d' % PeriodId)
        recBP.PeriodId = PeriodId
        recBP.PeriodValue = res.PeriodValue
        recBP.Tahun= oBP.LParent.PeriodValue

        res.Next()
      #-- while
