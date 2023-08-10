import sys
import os
import time
import json
rel_lib_path = os.environ["VERDI_HOME"] + "/share/NPI/python"
sys.path.append(os.path.abspath(rel_lib_path))
from pynpi import npisys
from pynpi import waveform

npisys.init(sys.argv)

def create_json_file( out_file_name,input_dict):
    with open(out_file_name , 'w') as json_file:
        print('--------------------------------------------------------------------------------')
        print('FSDB_API :: ','#---------------- Generating FSDB DUMP json file ----------------')
        print('FSDB_API :: ','Generated  file: ',out_file_name)
        json.dump(input_dict, json_file)

def generate_csv( signal_dict, out_file_name):
    output_csv_file = open(out_file_name + '.csv' , 'w')
    time_list = []
    for signal in signal_dict:
        for time in signal_dict[signal]:
            time_list.append(time)
        break
    header = 'Time'
    for time in time_list:
        header += ',' + str(time)
    output_csv_file.write(header + '\n')
    for signal in signal_dict:
        print_line = signal
        for time in time_list:
            print_line += ',' + signal_dict[signal][time]
        output_csv_file.write(print_line + '\n')


def open_fsdb(fsdb_file_path):
    print('Start to load FSDB.....')
    fileHandle = waveform.open(fsdb_file_path)
    print('FSDB loading successfully')
    min_time = fileHandle.min_time()
    max_time = fileHandle.max_time()
    print("min time:"+str(min_time), "max time:"+str(max_time))
 
    return fileHandle, min_time, max_time

def process_signals(fileHandle, signals_list, start_time, end_time, max_no_of_txn):
    signal_db_dict = {}
    signal_name_dict = {}
    time_list = []
    count = 1

    #---- add signals -----
    for sigName in signals_list:
        tb = waveform.SigBasedHandle()
        signal = fileHandle.sig_by_name(sigName)
        tb.add(signal)

        tb.iter_start( start_time, end_time)
        #----- get signals time and value -----
        no_of_txn = 1
        print(sigName)
        while True:
            idx,time = tb.iter_next()
            if idx == 0:
                break
            if no_of_txn == max_no_of_txn + 1:
                print('Skip signal : ', sigName)
                break
            if time not in time_list:
                time_list.append(time)
            #print(sigName, time)
            if sigName not in signal_db_dict:
                signal_db_dict[sigName] = {}
            if time not in signal_db_dict[sigName]:
                signal_db_dict[sigName][time] = tb.get_value()
            no_of_txn += 1

        tb.iter_stop()
    #print(signal_db_dict)
    signal_db_dict_update = {}
    time_list.sort()
    index = 0
    for sigName in signal_db_dict:
        print(index)
        index += 1
        if sigName not in signal_db_dict_update:
            signal_db_dict_update[sigName] = {}
        for time in time_list:
            if time in signal_db_dict[sigName]:
                value = signal_db_dict[sigName][time]
            signal_db_dict_update[sigName][time] = value

    #print(signal_db_dict_update)
            
    create_json_file('signal.json', signal_db_dict_update)
    generate_csv(signal_db_dict_update, 'signal.json')






def process_signals_old(fileHandle, signals_list, start_time, end_time):
    signal_db_dict = {}
    signal_name_dict = {}
    time_list = []
    tb = waveform.SigBasedHandle()
    count = 1

    #---- add signals -----
    for sigName in signals_list:
        signal = fileHandle.sig_by_name(sigName)
        tb.add(signal)
        signal_name_dict[count] = sigName
        count += 1

    tb.iter_start( start_time, 142862500)
    #----- get signals time and value -----
    no_of_txn = 0
    while True:
        idx,time = tb.iter_next()
        if time not in time_list:
            time_list.append(time)
        if idx == 0:
            break
        print('No of signals process : ',idx, '/', count, time)
        sigName = signal_name_dict[idx]
        if sigName not in signal_db_dict:
            signal_db_dict[sigName] = {}
        if time not in signal_db_dict[sigName]:
            signal_db_dict[sigName][time] = tb.get_value()

    tb.iter_stop()
    #print(signal_db_dict)
    signal_db_dict_update = {}
    time_list.sort()
    index = 0
    for sigName in signal_db_dict:
        print(index)
        index += 1
        if sigName not in signal_db_dict_update:
            signal_db_dict_update[sigName] = {}
        for time in time_list:
            if time in signal_db_dict[sigName]:
                value = signal_db_dict[sigName][time]
            signal_db_dict_update[sigName][time] = value

    #print(signal_db_dict_update)
            
    create_json_file('signal.json', signal_db_dict_update)
    generate_csv(signal_db_dict_update, 'signal.json')













def main():
    start = time.time()
    
    fsdb_file_path = "/tmp/k10/fullchip_trace.fsdb"
    fileHandle, min_time, max_time = open_fsdb(fsdb_file_path)

    scope = fileHandle.scope_by_name("soc_tb.soc.par_atom0")
    signalList = scope.sig_list()
    sig_list = []
    for i in range(len(signalList)):
        sig_list.append(signalList[i].full_name())
        #print(signalList[i].name(),signalList[i].left_range(), signalList[i].right_range(),signalList[i].direction(), signalList[i].assertion_type() )
        print('k10',signalList[i].name(), str(signalList[i].direction()), str(signalList[i].is_param()),str(signalList[i].composite_type()))
 
    #sig_list = ['soc_tb.soc.par_atom0.c2u_inf_qaccept_b_zxnfwh', "soc_tb.soc.par_atom0.atom_u2c_vccvinfaon_powergood_rst_b_untimed_xyxfxh"]
    process_signals(fileHandle, sig_list, min_time, max_time, 1)
    

    done = time.time()
    time_delta = done - start
    print('FSDB API :: Total time taken by script : ', time_delta, ' sec')

    #---- do not delete
    waveform.close(fileHandle)
    npisys.end()


if __name__ == "__main__":
    main()




