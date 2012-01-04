class fScriptTest :
    def __init__(self, formObj, parentForm):
        self.app = formObj.ClientApplication
        self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    def RunClick(self,sender):
        app = self.app
        uipInput = self.uipInput

        script = uipInput.Script or ''
        if script == '': raise 'Warning','Please fill the script file to run'
        
        response = app.ExecuteScript(uipInput.Script,app.CreateValues(['run',0]))
        
        resp = response.FirstRecord
        
        if response.packet.StreamWrapperCount > 0:
          self.oPrint.doProcess(self.app,response.packet,1)

        if resp.Is_Error :
           raise 'ERROR',resp.Error_Message
           
        app.ShowMessage('Script Finish')
        
