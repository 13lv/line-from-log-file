#!/usr/bin/python
#
# Filename: "print_regex.py"
#
#time zcat <filename>.log-2023* |grep -iP 'T=\+?(<999>|<999>|<999>|<999>)[0-9]{3,27}' | grep -i ' ACC: transaction answered: ' | \
#awk '{split($0, a, ";") split(a[1], b, " "); printf "%s %s, %s, %s\n", b[1],b[2],a[8],a[11]}' | \
#sed s/\(NOTICE\)//g > print_grep_result.txt
#
import os
import re
import gzip


WRITE = 1

fname = os.path.basename(__file__).split('.')[0]


ptrn_tr_ans = re.compile(r' ACC: transaction answered: ', re.I)
ptrn_dt = re.compile(r'^2023-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3])(:(0[0-9]|[1-5][0-9])){2}', re.I)
ptrn_from = re.compile(r'F=\+?[0-9]{3,28}', re.I)
ptrn_to = re.compile(r'T=\+?(<999>|<999>|<999>|<999>)[0-9]{3,28}', re.I)


ptrn_in_f = re.compile(r'^S8800_(0[1-9]|[12][0-9]|3[01])-May\(05\)-2023_', re.I)
ptrn_d_dflt = re.compile(r'(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])[0-9]{2}') # Default
ptrn_t_dflt = re.compile(r'(0[1-9]|1[0-9]|2[0-3])(0[0-9]|[1-5][0-9]){2}') # Default
ptrn_date = re.compile(r'0[1-9]0523')
ptrn_stime = ptrn_t_dflt
ptrn_etime = re.compile(r'')
ptrn_tac = re.compile(r'839')


def find_pattern_1(f_in, f_out):
    for line in f_in:
        res_to = ptrn_to.search(line)
        res_tr_ans = ptrn_tr_ans.search(line)
        if not res_tr_ans is None and not res_to is None:
            res_dt = ptrn_dt.search(line)
            if res_dt is None:
                print("res_dt", line)
            res_from = ptrn_from.search(line)
            if res_from is None:
                print("res_from", line)
            res_str = "%s, %s, %s\n"%(res_dt.group(0), res_from.group(0), res_to.group(0))

            if WRITE:
                f_out.write(res_str)
            else:
                print(res_str)


def find_pattern_2(f_in, f_out):
    """
    """
    L_res = []
    for line in f_in:
        uid = line[:20]
        date = line[21:27]
        stime = line[28:34]
        etime = line[35:41]
        tac = line[42:45]
        cnum = line[46:61]
        vdn = line[62:66]
        dnum = line[67:85]
        ucode = line[86:89]
        duration = line[90:95]
        frl = line[96:97]
        acode=  line[98:103]

#        print(id, date, stime, etime, tac, cnum, vdn, dnum, ucode, duration, frl, acode)

        res_date = ptrn_date.search(date)
        if res_date is None:
            break
        res_stime = ptrn_stime.search(stime)
        if res_stime is None:
            break
        res_tac = ptrn_tac.search(tac)
        if res_tac is None:
            break

        L_res.append(uid)

#        res_to = ptrn_to.search(line)
#        res_tr_ans = ptrn_tr_ans.search(line)
#        if not res_tr_ans is None and not res_to is None:
#            res_dt = ptrn_dt.search(line)
#            if res_dt is None:
#                print("res_dt", line)
#            res_from = ptrn_from.search(line)
#            if res_from is None:
#                print("res_from", line)
#            res_str = "%s, %s, %s\n"%(res_dt.group(0), res_from.group(0), res_to.group(0))

    for line in f_in:
        uid = line[:20]
        if uid in L_res:

            res_str = line

            if WRITE:
                f_out.write(res_str)
            else:
                print(res_str)


count = 0
with open('./%s_result.txt'%fname, 'w') as f_out:
    for root, dirs, files in os.walk("./"):
        files = sorted(files, key=os.path.getctime, reverse=True)

#        print(root)
#        print(dirs)
#        print(files)

        for file in files:
            if file.startswith(("<filename>.log-2023")) and file.endswith((".gz")):
                count += 1
                print("Log_1: \"%s\""%file)
                f_in_gz = gzip.open(file, 'r')
                find_pattern(f_in_gz, f_out)
                f_in_gz.close()

            if file.startswith(("<filename>")) and file.endswith((".log")):
                count += 1
                print("Log_2: \"%s\""%file)
                with open(file, 'r') as f_in_log:
                    find_pattern(f_in_log, f_out)

            if not ptrn_in_f.search(file) is None and file.endswith((".log")):
                count += 1
                print("Log_3: \"%s\""%file)
                with open(file, 'r') as f_in_log:
                    find_pattern_2(f_in_log, f_out)

#            if count == 3:
#                break
        break

print("\n%s\n -> Total numbers of processed files: \"%s\""%('-'*79, count))

