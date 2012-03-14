class fLongScriptTest :
    def __init__(self, formObj, parentForm):
        self.app = formObj.ClientApplication
        self.oPrint = self.app.GetClientClass('PrintLib','PrintLib')()

    def RunClick(self,sender):
        app = self.app
        uipInput = self.uipInput

        script = uipInput.Script or ''
        if script == '': raise 'Warning','Please fill the script file to run'
        
        pid = app.ExecuteScriptTrackable(uipInput.Script, app.CreateValues(['run',0]))

        pcConsole = self.pcConsole
        pcConsole.ConsoleFilterName = 'ExecutePackage_' + str(pid)
        pcConsole.ShowStatusBar = 0
        pcConsole.Headerless = 1
        pcConsole.Activate()
        
