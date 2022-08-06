# brute_zip_rar
requirements:

    numpy==1.22.4
    pyzipper==0.3.6
    rarfile==4.0
    tqdm==4.64.0

flags:

    -f = path to archive
    -c = number of threads
    -p = password list

example:
  
    python brute_rar.py -f secret.zip -c 12 -p passwords.txt 

after work she will show result success and time work
if success true then he is extracted the files and password to a new folder "result/*name archive*"
