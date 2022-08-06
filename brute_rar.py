from multiprocessing import Process, Queue
from timeit import default_timer as timer
from argparse import ArgumentParser
from os.path import exists
from tqdm import tqdm
import numpy as np
import pyzipper
import rarfile
import os

def save_passw(passw, path):
    with open(path, 'w') as f:
        f.write(passw)

def try_zip(file_name:str, password_list:list, path_save:str, result:Queue, primary:bool) -> None:
    if primary:
        password_list = tqdm(password_list)
    with pyzipper.AESZipFile(file_name, 'r',
                                    compression=pyzipper.ZIP_DEFLATED,
                                    encryption=pyzipper.WZ_AES) as extracted_zip:
        for passw in password_list:
            try:
                extracted_zip.extractall(path=path_save,pwd=str.encode(passw))
                save_passw(passw, path_save+'/password.txt')
                result.put(True)
                return
            except:
                pass
    result.put(False)


def try_rar(file_name:str, password_list:list, path_save:str, result:Queue, primary:bool) -> None:
    if primary:
        password_list = tqdm(password_list)
    with rarfile.RarFile(file=file_name, mode='r') as extracted_rar:
        for passw in password_list:
            try:
                extracted_rar.extractall(path=path_save,pwd=str.encode(passw))
                save_passw(passw, path_save+'/password.txt')
                result.put(True)
                return
            except:
                pass
    result.put(False)

def setup_args() -> ArgumentParser.parse_args:
    parser = ArgumentParser()
    parser.add_argument('-f', help='file archive', dest='file')
    parser.add_argument('-c', help='number of threads', dest='threads', type=int)
    parser.add_argument('-p', help='password list', dest='passwords_list')
    args = parser.parse_args()
    return args

def get_path_save(file_name:str) -> str:
    clearname = file_name.split('.')[0]
    path_save = f'./result/{clearname}'
    if not exists(path_save):
        os.makedirs(path_save)
    return path_save

def get_type_archive(file_name):
    if file_name.endswith('zip'):
        target_funk = try_zip
    elif file_name.endswith('rar'):
        target_funk = try_rar
    else:
        print('error with archive extension')
        exit(1)
    return target_funk


def main() -> None:
    if not exists('./result'):
        os.makedirs("result")
    result = Queue()
    success = False

    get_args = setup_args()

    COUNT_PROCESS:int = get_args.threads
    file_name:str = get_args.file
    passwords_list:str = get_args.passwords_list
    if any((COUNT_PROCESS is None, file_name is None, passwords_list is None)):
        exit('empty arguments')

    target_funk = get_type_archive(file_name)
    try:
        with open(passwords_list, 'r', encoding= 'unicode_escape') as f:
            passwords = f.read().split('\n')
    except FileNotFoundError:
        exit('not found password list file')
    
    passwords_10 = np.array_split(passwords, COUNT_PROCESS)
    jobs = []
    start = timer()
    for index, password_list in enumerate(passwords_10):
        if index == len(passwords_10)-2:
            primary = True
        else:
            primary = False
        th = Process(target=target_funk, args=(file_name, password_list, get_path_save(file_name), result, primary, ))
        th.start()
        jobs.append(th)
    try:
        for job in jobs:
            job.join()
            raw_success = result.get()
            success = True if raw_success == True else success
    except KeyboardInterrupt:
        for job in jobs:
            job.terminate()

    print(f'result = {success} time =', timer()-start)

if __name__ == "__main__":
    main()