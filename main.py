import os
import sys
import string
import random
import re
import json
import csv
import threading


def random_generator(count: int, chars=string.ascii_uppercase, digits=string.digits):
    string: str = ""
    tkn = "<Tkn"
    tkn1 = "Tkn>"
    for _ in range(count):
        string += tkn + ''.join(random.choice(digits) for _ in range(3)) + ''.join(random.choice(chars)
                                                                                      for _ in range(5)) + tkn1
        string += ''.join(random.choice(digits) for _ in range(10)) + ''.join(random.choice(chars) for _ in range(10))
    return string


def create_input_folder(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


def create_output_folder(output_path: str):
    if not os.path.exists(output_path):
        os.mkdir(output_path)


def create_random_files(count: int, path: str):
    for i in range(count):
        with open(f"{path}/file{i+1}.txt", "w") as file:
            file.write(random_generator(count))


def read_folder(path: str):
    path_files = os.listdir(path)
    dictionary: dict = {}
    for i in range(len(path_files)):
        with open(f"{path}/{path_files[i]}", "r") as file:
            match_all = re.findall(r"<Tkn\d{3}\w{5}Tkn>", file.read())
            create_dict(match_all, f"{path}/{path_files[i]}", dictionary)
    return dictionary


def write_to_csv_file(dictionary: dict, output_path: str):
    with open(f"{output_path}/output_file.csv", 'w', newline='') as csv_file:
        spamwriter = csv.writer(csv_file, delimiter=':')
        for item in dictionary.items():
            spamwriter.writerow(item)

    csv_file.close()


def write_to_json_file(dictionary: dict, output_path: str):
    json_object = json.dumps(dictionary, indent=4)
    with open(f"{output_path}/output_file.json", "w") as json_file:
        json_file.write(json_object)
    json_file.close()


def create_dict(match_all: list, path_files: str, dictionary: dict):
    for i in match_all:
        count = 1
        if f"{path_files} {i}" in dictionary:
            count += 1
            dictionary[f"{path_files} {i}"] = count
        dictionary[f"{path_files} {i}"] = count


def analyze_firmware(count_files: int, directory_path: str, output_path: str):
    print("Create input folder")
    create_input_folder(path)
    print("Create output folder")
    create_output_folder(output_path)
    print("Create random .txt files with tokens")
    create_random_files(count_files, directory_path)
    print("Read folder")
    dictionary = read_folder(directory_path)

    print("Write to output .csv file")
    csv_tread = threading.Thread(target=write_to_csv_file, args=(dictionary, output_path))
    csv_tread.start()

    print("Write to output .json file")
    json_thread = threading.Thread(target=write_to_json_file, args=(dictionary, output_path))
    json_thread.start()

    csv_tread.join()
    json_thread.join()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("You should to input full directory path, full output path and the number of files to be created.")
        exit(-1)
    path = sys.argv[1]
    output_path = sys.argv[2]
    count_files = int(sys.argv[3])
    analyze_firmware(count_files, path, output_path)
