# -*- coding: utf-8 -*-
"""
Plot graph according to the DAT file 
@author: Danil Borchevkin
"""

import csv
import glob
import os
import matplotlib.pyplot as plt
import scipy.signal as signal
import numpy as np
import math

def read_raw_file_data(filepath):
    '''
    Read data in list
    '''

    raw_data = list()

    # Get raw data
    with open(filepath, 'r') as dest_f:
        raw_data = dest_f.readlines()

    return raw_data

def process_file(data, out_filepath, window, step):
    line_cursor = 0

    while (line_cursor < (len(data) - window)):
        with open(out_filepath + '_c' + "{:08d}".format(line_cursor) + '_w' + str(window) + '_s' + str(step) + ".dat", 'w') as dest_f:
            for i in range(window):
                dest_f.write(data[line_cursor + i])
        line_cursor += step

def read_file_data(filepath):
    '''
    Read data in [[val,time],[val, time]] format
    '''

    raw_data = None
    data = list()

    # Get raw data
    with open(filepath, 'r') as dest_f:
        data_iter = csv.reader(dest_f,delimiter="\t")
        raw_data = [raw_data for raw_data in data_iter]

    # Filter data with not-valid values or empty values
    for raw_val in raw_data:
        try:
            amp = float(raw_val[0])
            time = float(raw_val[1])
            data.append([amp, time])
        except:
            pass
        finally:
            pass

    return data

def save_to_ascii_file(data_list, out_filepath, header=[]):
    '''
    Save data in format [[],[]] into DAT file 
    - CSV 
    - with \t delimeter 
    - \n line endings
    '''
    write_list = []

    for data in data_list:
        output_str = ""
        for val in data:
            output_str += str(val) + "\t"
        output_str = output_str[:-1]
        output_str += "\n"
        write_list.append(output_str)

    with open(out_filepath,"w") as f:
        f.writelines(write_list)

def plot_graph(data, out_filepath, lb_freq_start=0.01, lb_freq_end=4.0, lb_freq_num=100000, to_display=False, save_to_disk=True):
    '''
    Plot grapth and return its data

    Params
    data - input data in list of lists with pair value and time
    out_filepath - out file name path for create
    lb_freq_start - start frequency of lombscargle graph
    lb_freq_end - end frequency of lombscargle graph
    lb_freq_num - number of points in lombscargle graph
    to_display - if set to true then graph will be shown on the display
    save_to_disk - if set to true then graph will be saved on the disk

    Return
    List of lists of graph values in form [freq, pgram_value]
    '''

    output_data = list()

    x = list()
    y = list()

    for val_pair in data:
        x.append(val_pair[1])
        y.append(val_pair[0])

    # Define the array of frequencies for which to compute the periodogram:
    f = np.linspace(lb_freq_start, lb_freq_end, lb_freq_num)

    #Calculate Lomb-Scargle periodogram:
    pgram = signal.lombscargle(x, y, f, normalize=False)

    # Create figure with 2 subplots
    fig = plt.figure()
    source_ax = fig.add_subplot(211)
    pgram_ax = fig.add_subplot(212)

    #Now make a plot of the input data:
    source_ax.plot(x, y, 'b+')

    #Then plot the normalized periodogram:
    pgram_ax.plot(f, pgram)

    if to_display:
        plt.show()

    if save_to_disk:
        plt.savefig(out_filepath)

    # Generate output
    for idx, freq in enumerate(f):
        period = 2 * math.pi / freq
        output_data.append([freq, period, pgram[idx], x[0]])

    plt.cla()
    plt.clf()
    plt.close(fig)

    return output_data

def process_windowed_files(path, output_file_path, lb_freq_start, lb_freq_end, lb_freq_num):
    files = glob.glob(path + "*.dat")  

    for filepath in files:
        # Reject old merged files
        if "!" in filepath:
            continue

        # Reject old windowed files
        if "windowed" in filepath:
            continue

        print("Process >> " + filepath)

        try:
            read_data = read_file_data(filepath)
            out_dat_filepath = path + os.path.basename(filepath) + "_windowed" + ".dat"
            out_png_filepath = path + os.path.basename(filepath) + "_windowed" + ".png"

            output_data = plot_graph(read_data, 
                                    out_png_filepath,
                                    lb_freq_start=lb_freq_start,
                                    lb_freq_end=lb_freq_end,
                                    lb_freq_num=lb_freq_num)

            print("Saved PNG to >> " + out_png_filepath)
            save_to_ascii_file(output_data, out_dat_filepath)
            print("Saved DAT to >> " + out_dat_filepath)

    
        except Exception as e:
            print("Cannot process >> ", filepath)
            print("Reason >> " + str(e))
            
        finally:
            print()
    
        try:
            os.remove(output_file_path)
        except Exception as e:
            pass
        finally:
            pass
        windowed_files = glob.glob(path + "*_windowed.dat")
        for windowed_file in windowed_files:           
            with open(windowed_file, 'r') as windowed_f:
                data = windowed_f.read()
                with open(output_file_path, 'a') as merged_file:
                    merged_file.write(data)


def main():
    print("Script is started")

    files = glob.glob("./input/*.dat")              # Change path here or write filepath
    OUTPUT_PATH = "./output/"                       # Change output here
    WINDOW = 300                                    # Change window value here
    STEP = 150                                      # Change step value here
    FREQ_START = 0.01                               # Change freq start here
    FREQ_END = 4.0                                  # Change freq end here
    FREQ_NUM = 100000                               # Change freq num here

    for filepath in files:
        print("Process >> " + filepath)

        try:
            read_lines = read_raw_file_data(filepath)
            out_dat_filepath = OUTPUT_PATH + os.path.basename(filepath)
            process_file(read_lines, out_dat_filepath, WINDOW, STEP)
            process_windowed_files(OUTPUT_PATH, f'{OUTPUT_PATH}!{os.path.basename(filepath)}_merged_file.dat', FREQ_START, FREQ_END, FREQ_NUM)

            print(f"<{filepath}> succesful processed by the script")
    
        except Exception as e:
            print("Cannot process >> ", filepath)
            print("Reason >> " + str(e))
            
        finally:
            print()

    print("Script is finished")

if __name__ == "__main__":
    main()