import explorer

def DAFScriptMain(config, parameter, returnpacket):
  dataset = parameter.GetDataset(0)
  record = dataset.GetRecord(0)
  actual_path = record.data

  result_def = 'fd_name: string; fd_size: integer; fd_type: integer; fd_type_char: string; fd_mdate: string'
  record = returnpacket.CreateDataPacketStructure(result_def)
  dataset = record.DataSet

  first_loop = 1
  for rec_dir in explorer.browsedir(actual_path):
    if first_loop:
      first_loop = 0
    else:
      record = dataset.AddRecord()
    record.fd_name = rec_dir[0]
    record.fd_type = rec_dir[3]
    if record.fd_type == 0:
      record.fd_size = explorer.sz_kb(rec_dir[1])
    record.fd_type_char = rec_dir[2]
    record.fd_mdate = rec_dir[4]
  
  return 1
