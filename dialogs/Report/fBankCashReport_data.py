
import sys

def CetakData(config,parameters,returns):
  ret = returns.CreateValues(
    ['IsErr', 0],
    ['ErrMessage','']
  )
  
  try:


  except:
    ret.IsErr = 1
    ret.ErrMessage = str(sys.exc_info()[1])
