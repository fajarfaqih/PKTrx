import com.ihsan.foundation.pobjecthelper as phelper
import os,sys

def DAFScriptMain(config, params, returns):
  # config: ISysConfig object
  # parameter: TPClassUIDataPacket
  # returnpacket: TPClassUIDataPacket (undefined structure)
  status = returns.CreateValues(
    ['Is_Err',0],['Err_Message','']
  )
  helper = phelper.PObjectHelper(config)    
  param = params.FirstRecord
  
  try :
    PrintHelper = helper.CreateObject('PrintHelper')
    Corporate = helper.CreateObject('Corporate') 
    FileName = param.templatename
    
    #workbook = PrintHelper.LoadExcelTemplate(FileName)  
    #try :
      #FullFileName = Corporate.GetUserHomeDir() + '\\' + FileName
      #if os.access(FullFileName, os.F_OK) == 1:
      #  os.remove(FullFileName)
      
        
      #workbook.SaveAs(FullFileName)
      # end if
        
    #finally :
      #workbook = None
    
    FullFileName = PrintHelper.GetExcelTemplatePath(FileName)
    sw = returns.AddStreamWrapper()
    sw.LoadFromFile(FullFileName)
    sw.MIMEType = config.AppObject.GetMIMETypeFromExtension(FullFileName)
    
  except:
    status.Is_Err = 1
    status.Err_Message = str(sys.exc_info()[1])
  return 1
  
