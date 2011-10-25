import pyFlexcel

# request
save     = 0
preview  = 1
printout = 2

class PrintLib:
  def __init__(self):
    # set default request
    self.default_request = preview

  def doProcess(self,app,packet,request=-1):
    # handle packet and request type :
    # 0 = Save As
    # 1 = Preview
    # 2 = Print
    if request not in [0,1,2] : request = self.default_request
    #request = int(request)
    if packet.StreamWrapperCount > 0:
      streamWrapper = packet.GetStreamWrapper(0)
      self.doRequest(request,app,streamWrapper)
    else:
      app.ShowMessage("Download stream not found")

  def doProcessByStreamName(self,app,packet,streamName,request=-1):

    if request not in [0,1,2] : request = self.default_request
    #request = int(request)
    if packet.StreamWrapperCount > 0:
      streamWrapper = packet.GetStreamWrapperByName(streamName)
      self.doRequest(request,app,streamWrapper)
    else:
      app.ShowMessage("Download stream not found")

  def doRequest(self,request,app,streamWrapper):
    # handle packet and request type :
    # 0 = Save As
    # 1 = Preview
    # 2 = Print
    if request == 0:
        self.doSaveAs(app, streamWrapper)
    elif request == 1:
      self.doPreview(app, streamWrapper)
    elif request == 2:
      self.doPrint(app, streamWrapper)

  def doSaveAs(self, app, streamWrapper):
    # handle "Save as" request
    sFilter = "All files (*.*)|*.*"
    fileExt = app.GetExtensionFromMIMEType(streamWrapper.MIMEType)
    if fileExt != "":
      sFilter = streamWrapper.MIMEType + " files (*" + fileExt + ")|*" + fileExt + \
        "|" + sFilter
    fileName = app.SaveFileDialog("Save as..", sFilter)
    if fileName != "":
      streamWrapper.SaveToFile(fileName)
    return


  def doPreview(self, app, streamWrapper):
    # handle "view" request
    sFileName = app.GetTemporaryFileName("dl")
    fileExt = app.GetExtensionFromMIMEType(streamWrapper.MIMEType)
    if fileExt != "":
      sFinalFileName = sFileName + fileExt
      streamWrapper.SaveToFile(sFinalFileName);
      app.DeleteFile(sFileName)
      #if fileExt.upper() == ".HTM" or fileExt.upper() == ".HTML":
      #  frmWebViewer = app.CreateForm("fWebViewer", "fWebViewer", 0, None, None)
      #  frmWebViewer.showWebPage("file://" + sFinalFileName)
      #else:
      app.ShellExecuteFile(sFinalFileName)
    else:
      app.ShowMessage("File extension cannot be identified")
    return

  def doPrint(self, app, streamWrapper):
    # handle "print" request
    if self.CheckMinVersion(app,app.GetVersion(), [3, 5, 0, 30]):
        streamWrapper.PrintRawText()
    else:
        #streamWrapper.PrintText("Courier New", 8)
        sFileName = app.GetTemporaryFileName("dl")
        streamWrapper.SaveToFile(sFileName)
        #app.PrintTextFile(sFileName, "Lucida Console", 8)
        #app.ExecuteLocalProgram("prfile.exe",sFileName)
        app.PrintTextFile(sFileName, "Courier New", 9)
    return

  def CheckMinVersion(self,app,aVersion, aReqVersion):
    return (
        aVersion[0] > aReqVersion[0] or aVersion[0] == aReqVersion[0] and (
            aVersion[1] > aReqVersion[1] or aVersion[1] == aReqVersion[1] and (
                aVersion[2] > aReqVersion[2] or aVersion[2] == aReqVersion[2] and
                    aVersion[3] >= aReqVersion[3]
            )
        )
    )

  def CheckTemplate(self,app,filename,ForceDownload=0):
    if ForceDownload:
      app.DeleteFile(filename)

    if not app.CheckFileExist(filename):
      param = app.CreateValues(['templatename',filename])
      returns = app.ExecuteScript('Report/S_GetTemplate',param)

      status = returns.FirstRecord
      if status.Is_Err : raise 'ERROR','Gagal download file template laporan\n' + status.Err_Message

      sw = returns.packet.GetStreamWrapper(0)
      sw.SaveToFile(filename)
    # end if

  def OpenExcelTemplate(self,app,filename):
    #pathtemplates = 'reports\\templates\\'
    self.CheckTemplate(app,filename,ForceDownload=1)
    return pyFlexcel.Open(filename)

  def ConfirmDestinationPath(self,app,fileExtension):
    Extension = {
      'ext' : fileExtension,
      'EXT' : fileExtension.upper()
    }
    filename = app.SaveFileDialog('Simpan file data hasil download', \
      'File %(ext)s (*.%(ext)s)|*.%(ext)s' % Extension)

    if len(filename) <= 0 :
      return

    if filename.find('.%(ext)s' % Extension) < 0 and filename.find('.%(EXT)s' % Extension) < 0:
      filename += '.%(ext)s' % Extension

    if app.CheckFileExist(filename):
      if not app.ConfirmDialog('Name file yang akan disimpan sudah ada.\nAnda akan melakukan overwrite ?'):
        return ''

      app.DeleteFile(filename)
    # end if

    return filename

