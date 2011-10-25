import com.ihsan.foundation.pobjecthelper as phelper
import sys
import simplejson


def CreateBudgetPeriod(config, params, returns):
  helper = phelper.PObjectHelper(config)
  status = returns.CreateValues(['IsErr', 0], ['ErrMessage', ''])
  config.BeginTransaction()
  try :
    PeriodValue = params.FirstRecord.PeriodValue

    oPeriodYear = helper.GetObjectByNames(
                'BudgetPeriod',
               {'PeriodValue' : PeriodValue}
               )
    if not oPeriodYear.isnull :
       raise '','Data Tahun Periode %d sudah ada' % PeriodValue
       
    oPeriodYear = helper.CreatePObject('BudgetPeriod')
    oPeriodYear.PeriodValue = PeriodValue
    oPeriodYear.IsOpen = 'T'
    
    for i in range(12):
      oPeriodMonth = helper.CreatePObject('BudgetPeriod')
      oPeriodMonth.PeriodValue = i + 1
      oPeriodMonth.ParentPeriodId = oPeriodYear.PeriodId
      oPeriodMonth.IsOpen = 'T'

    # enf for
    config.Commit()
  except :
    config.Rollback()
    status.IsErr = 1
    status.ErrMessage = str(sys.exc_info()[1])

