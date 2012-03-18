class fScriptTest :
    def __init__(self, formObj, parentForm):
        self.app = formObj.ClientApplication
        self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    def Show(self):
        self.FormContainer.Show()

    def RunClick(self,sender):
        app = self.app
        form = self.FormObject
        
        uipInput = self.uipInput

        response = form.CallServerMethod('PrintKontrolSaldoAwal',app.CreateValues())
        
        resp = response.FirstRecord

        if resp.Is_Error :
           raise 'ERROR',resp.Error_Message
           
        if response.packet.StreamWrapperCount > 0:
          self.oPrint.doProcess(self.app,response.packet,1)

        
