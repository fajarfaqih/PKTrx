

def FormSetDataEx(uideflist,parameters):
  config = uideflist.Config
  
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.BranchCode = str(config.SecurityContext.GetUserInfo()[4])

  Now = config.Now()
  bulan = int(config.FormatDateTime('m',Now))
  tahun = int(config.FormatDateTime('yyyy',Now))
  rsPeriod = config.CreateSQL(' \
       select a.periodid from budgetperiod a , budgetperiod b \
       where a.parentperiodid=b.periodid \
           and a.periodvalue=%d and b.periodvalue=%d' % (bulan,tahun)).RawResult
  rec.PeriodId = (rsPeriod.GetFieldValueAt(0) or 0)
