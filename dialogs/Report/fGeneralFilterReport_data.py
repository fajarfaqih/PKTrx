import com.ihsan.foundation.pobjecthelper as phelper

def FormSetDataEx(uideflist, parameter) :
  rec = uideflist.uipData.Dataset.AddRecord()
  rec.ID = parameter.FirstRecord.ID
  rec.mode = parameter.FirstRecord.mode
  rec.TglAwal = int(uideflist.config.Now())
  rec.TglAkhir = rec.TglAwal
