"""
The entrance of the project.
TODO: docstring with more details

Create by Weida Zhong, on July 02 2018
version 1.0
Python 3.x
"""

import textwrap
import sys
import os
import argparse

from unzip import decompress_file
from clean import clean_file
from preprocess import preprocess
from backup import backup
from size_cmd import size_cmd
from new_cmd import new_cmd
from calibration import calibration_cmd

from utils import remove_files_matching

debug = True

commands_dict = {"clean": "move 'bad' trip (based on the input criteria) to a temporary location for manual inspection or delete immediately as requst."}
commands_dict["help cmd"] = "displays the syntax and description for the command."
commands_dict["size"] = "display overall size, and size for each user"
commands_dict["new"] = "show newly added data since last time running this command or specified time point"
commands_dict["backup"] = "backup data. Ask for backup location if [-d] is not specified, and save it for future use."
commands_dict["exit"] = "exits the program"
commands_dict["unzip"] = "decompress the specified file, or compressed files under specified directory."
commands_dict["preprocess"] = "preprocess the files in the specified directory."
commands_dict["rm"] = "remove files meeting specified conditions from the given directory"
commands_dict["calibration"] = "Get coordinates alignment parameters for trips"

cmd_list = {"clean": clean_file, "size": size_cmd, "new": new_cmd,
            "backup": backup, "unzip": decompress_file, "preprocess": preprocess,
            "calibration": calibration_cmd}


def helper():
    """
    Displays the functions of individual commands. This is invoked when user enters "help" in the command-line.
    """
    print("Usage: \"help [cmd]\" or simply \"cmd\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")

    longest_cmd = max(commands_dict.keys(), key=len)

    for command in sorted(commands_dict):
        prefix = " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent=prefix,
                                    width=preferredWidth, subsequent_indent=' '*(len(longest_cmd) + 4))
        print("{0:<{1}s} {2:<}".format(command, len(longest_cmd) + 2, wrapper.fill(commands_dict[command])))


def cmd_help(cmd):
    """
    Performs "help cmd", i.e, displays the syntax of individual command.

    Parameters
    -----------
        cmd: str
            The command to show more help information.
    """
    print()

    if cmd not in cmd_list:
        print("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")
    else:
        print("Description:", commands_dict[cmd], "\n")
        print("Usage:")
        cmd_list[cmd]("syntax")


def load_config(dir):
    """
    Load the configuration for basic setting

    Parameters
    ----------
    dir : str
        The folder that contains the config file

    Returns
    -------
    configs : dict
        Configs
    """
    config_file = os.path.join(dir, 'config.txt')

    if not os.path.isfile(config_file):
        return {}

    configs = {}
    with open(config_file, 'r') as fp:
        for line in fp:
            line = line.rstrip()
            line = line.replace(" ", "")
            segs = line.split(",")
            configs[segs[0]] = segs[1]

    return configs


def main(args):
    """
    Takes the user input and invokes the appropriate method.
    """
    print("Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")

    data_path = './data'
    data_path = '/media/weida/Seagate8T/VehSenseTraffic/stampede'
    if args.data_path:
        data_path = args.data_path
    configs = load_config(data_path)
    configs["data_path"] = data_path

    if debug:
        print(configs)

    while True:
        input_string = input(">>").rstrip()
        if not input_string:
            continue
        input_string = input_string.replace("=", " ")
        input_segments = input_string.split()
        received_cmd = input_segments[0]
        if received_cmd == "help" and len(input_segments) == 1:
            helper()
        elif received_cmd == "help" and len(input_segments) == 2:
            cmd_help(input_segments[1])
        elif received_cmd == "exit":
            print("Exiting VehSense backend.")
            resume = False
            while True:
                try:
                    choice = input("Save config? (y/n): ").rstrip().lower()
                    if choice[0] == 'y':
                        # TODO: save config. But where to put it?
                        print(configs)
                        break
                    elif choice[0] == 'n':
                        print("quit without saving config")
                        break
                    elif choice == 'resume':
                        print('program resume')
                        resume = True
                        break
                except:
                    continue

            if not resume:
                sys.exit()

        elif received_cmd == 'cd':
            # TODO: do we need to reload config? DO NOT use this command for now
            if len(input_segments) == 2:
                if os.path.isdir(input_segments[1]):
                    configs = load_config(data_path)
                    configs['data_path'] = input_segments[1]
                else:
                    print("given folder does not exist.")
            else:
                print("missing args")
        elif received_cmd == 'dir' or received_cmd == 'pwd':
            print("current data path: %s" % configs['data_path'])
        elif received_cmd == 'rm':
            # to deal with empty string
            input_segments = [s.replace('"', '').replace("'", '') for s in input_segments]

            if len(input_segments) == 4:
                if os.path.isdir(input_segments[1]):
                    target_path = input_segments[1]
                    prefix = input_segments[2]
                    suffix = input_segments[3]
                else:
                    print("The provided path %s is invalid." % target_path)
                    continue
            elif len(input_segments) == 3:
                target_path = configs['data_path']
                prefix = input_segments[1]
                suffix = input_segments[2]
            else:
                print("'rm' command takes two paramters, i.e. 'rm prefix suffix', or\n\t three parameters, i.e. 'rm target_path prefix suffix'")
                continue
            print(target_path, prefix, suffix)
            remove_files_matching(target_path, prefix, suffix)
        elif received_cmd in cmd_list:
            if len(input_segments) == 1:
                cmd_help(input_segments[0])
            else:
                cmd_list[received_cmd](input_segments[1:], configs)
        else:
            print("Unrecognized command. Use \"help\" to list all available commands, and then enter \"help [cmd]\" for function syntax")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', help="used for CircleCI")
    parser.add_argument('-d', '--data_path', help='the default working directory while this script running')
    args = parser.parse_args()
    if args.test:
        print("test passed")
        sys.exit()
    main(args)
