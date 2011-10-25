# formtransaksi.py

import com.ihsan.foundation.mobject as mobject

class record: pass

class FormTransaksi(mobject.MObject):

    def mobject_init(self):
        pass

    def SetDataEx(self, uideflist, parameter, dsname=''):
        helper = self.Helper
        if dsname == '':
            rec = parameter.FirstRecord
        else:
            rec = parameter.GetDatasetByName(dsname).GetRecord(0)

        if rec.Modus_SetData == 1:
          oTransaksi = helper.GetObject(
            'Transaction',rec.TransactionId
          )

          Inbox = helper.GetObjectByNames(
                'InboxTransaction',
                {'TransactionId':oTransaksi.TransactionId}
            )
          ph = Inbox.LoadDataPacket()
          uideflist.SetCustomReturnDataset(ph)

          # uipart must have TransactionNo member
          uipTran = uideflist.uipTransaction.Dataset.GetRecord(0)
          uipTran.TransactionNo = oTransaksi.TransactionNo

          return 1
        else:
          return 0

