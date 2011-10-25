import sys
import com.ihsan.foundation.pobjecthelper as phelper

def DAFScriptMain(config, parameter, returnpacket):
    returnpacket.CreateValues(['Is_Error', 1], ['Error_Message', 'Tidak ada aksis'])
    return 1

def CheckForDualControl(config, parameter, returnpacket):
    rec = parameter.FirstRecord
    helper = phelper.PObjectHelper(config)
    
    corporate = helper.CreateObject('Corporate')
    resp = corporate.FunctionAccess(rec.Id_Fungsi)
    Is_Dual_Control = not resp.Is_Err and resp.Is_Dual_Control
    
    returnpacket.CreateValues(
        ['Is_Dual_Control', (Is_Dual_Control == 'T')]
    )
    
    return 1

def GetCredentials(config, parameter, returns):
    rec = parameter.FirstRecord
    helper = phelper.PObjectHelper(config)
    
    corporate = helper.CreateObject('Corporate')
    resp = corporate.FunctionAccess(rec.tx_code)
    if resp.Is_Err:
        returns.CreateValues(
            ['Is_Err', 1],
            ['Err_Message', resp.Err_Message]
        )
    else:
        returns.CreateValues(
            ['Is_Err', 0],
            ['Is_Dual_Control', (resp.Is_Dual_Control == 'T')]
        )

    return 1

def CheckDualControlUser(config, parameter, returnpacket):
    rec = parameter.FirstRecord
    helper = phelper.PObjectHelper(config)
    
    corporate = helper.CreateObject('Corporate')
    resp = corporate.DualControlCheck(
        rec.Id_User,
        rec.Password,
        rec.Id_Fungsi
    )
    
    if resp.Is_Err:
        Err_Message = resp.Err_Message
    else:
        Err_Message = ''
    
    returnpacket.CreateValues(
        ['Is_Err', resp.Is_Err], 
        ['Err_Message', Err_Message]
    )
    
    return 1

def CheckOverride(config, parameter, returnpacket):
    rec = parameter.FirstRecord
    helper = phelper.PObjectHelper(config)
    
    corporate = helper.CreateObject('Corporate')
    resp = corporate.OverrideCheck(
        rec.Id_User,
        rec.Password,
        rec.Id_Fungsi
    )
    
    if resp.Is_Err:
        Err_Message = resp.Err_Message
    else:
        Err_Message = ''

    returnpacket.CreateValues(
        ['Is_Err', resp.Is_Err],
        ['Err_Message', Err_Message]
    )
    
    return 1
