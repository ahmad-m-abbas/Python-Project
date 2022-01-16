import csv
import glob
import re
import Levenshtein as lev  # library to check the similarity ratio between two strings
import copy
import datetime

from Abstract import Abstract


class Course(Abstract):
    def __init__(self):
        super().__init__()

    def _readStudentList(self):
        try:
            studentListFile = Abstract.args[0]  # extract the student list sheet path from the passed arguments
            with open(studentListFile, mode='r', encoding='latin1') as file:
                reader = csv.reader(file)
                next(reader)  # skip the header
                for read in reader:
                    self._studentData.append(read)  # store the students' data (names)
                    self._stdDict[read[0]] = read  # store in the dictionary with ID as a key
        except IOError as e:
            print(e)
            exit(1)

    def _readAttendance(self):
        try:
            stdAttPath = Abstract.options.att  # get the attendance files path
            P = Abstract.options.P
            attDict = copy.deepcopy(self._stdDict)  # deep copy to create new dict to store attendance data
            # attDict[ID][0]=ID, attDict[ID][1]=name

            header = ['Student ID', 'Student Name']
            counter = 0
            # edit the path to find files that match the name convention for attendance files
            stdAttPath += "\\" + self._courseName + "-[01][0-9]-[0-3][0-9]-[0-9][0-9][0-9][0-9]-AR.csv"
            files = glob.glob(stdAttPath)  # store all files matching the convention
            if len(files) == 0:  # if no match was found, inform the user
                print("WARNING: No attendance file was found\n")
                return
            for file in files:
                # extract the date from the file name
                date = str(file).split('\\')
                date = date[len(date) - 1]
                date = date.split('-')
                date = date[1:4]
                date = "-".join(date)
                header.append(date)  # add the date to the header
                counter += 1  # indicate the number of the current file
                for key in self._stdDict:  # initiate the number of minutes to 0
                    attDict[key].append(0)

                # create a file for non-valid attendance
                nonValidAt = str(file)
                # extract the file name
                nonValidAt = nonValidAt.split('\\')
                nonValidAt = nonValidAt[len(nonValidAt) - 1]
                nonValidAt = Abstract.options.store + "\\" + re.sub(r'\.csv$', "-NV.csv", nonValidAt)
                nonValidAtFile = open(nonValidAt, mode="w", newline='', encoding='latin1')
                writer = csv.writer(nonValidAtFile)

                with open(file, mode='r', encoding='latin1') as f:
                    reader = csv.reader(f)
                    for read in reader:
                        if read == "":  # ignore blank lines
                            continue

                        # read[0]=name_(ID), read[1]=minutes

                        flag = False  # flag to indicate whether the name or ID was mapped to a student in the sheet
                        ID = re.search(r'[0-9]{7}', read[0])

                        if ID and ID.group() in self._stdDict.keys():
                            flag = True

                            attDict[ID.group()][1 + counter] += int(read[1])

                        else:
                            # names may be in the format : Name (Original Name)
                            # so we need to check if any of the two (name or original name) matches a student in the list
                            originalName = ""
                            atName = read[0].split('(')
                            if len(atName) > 1:
                                originalName = atName[1]
                                originalName = re.sub(r'[^A-Za-z\s]', "", originalName)  # remove non-alphabetical characters
                            atName = atName[0]
                            atName = re.sub(r'[^A-Za-z\s]', "", atName)  # remove non-alphabetical characters

                            for ID in attDict:
                                name = attDict[ID][1].strip().split(" ")
                                firs_surName = [name[0]]
                                firs_surName += name[3:]
                                firs_surName = " ".join(firs_surName)
                                # ratios for Name
                                ratio1 = lev.ratio(firs_surName.lower(), atName.lower())  # for first and surname
                                ratio2 = lev.ratio((name[0] + " " + name[1]).lower(),
                                                   atName.lower())  # for first and second name
                                # ratios for Original Name
                                ratio3 = lev.ratio(firs_surName.lower(), originalName.lower())  # for first and surname
                                ratio4 = lev.ratio((name[0] + " " + name[1]).lower(),
                                                   originalName.lower())  # for first and second name
                                if ratio1 > .80 or ratio2 > .80 or ratio3 > .80 or ratio4 > .80:
                                    # attDict[ID][0]=ID, attDict[ID][1]=name
                                    # attDict[ID][1 + counter] = num of minutes for the current meeting
                                    attDict[ID][1 + counter] += int(read[1])
                                    flag = True

                        if not flag:  # non-valid name or ID
                            writer.writerow(read)
                if P != 0:
                    # print the students who attended less than P minutes
                    writer.writerow("")
                    writer.writerow(["Students attended less than " + str(Abstract.options.P) + " minutes"])
                    for key in attDict:
                        minutes = attDict[key][1 + counter]
                        if P >= minutes > 0:
                            temp = attDict[key][0] + "-" + attDict[key][1]
                            writer.writerow([temp, attDict[key][1 + counter]])

                nonValidAtFile.close()

                attReport = copy.deepcopy(
                    self._stdDict)  # deep copy to create new dict to store attendance report for each student
                # attDict[ID][0]=ID, attDict[ID][1]=name, attDict[ID][2:]= attendance state

                for key in attDict:
                    for minutes in attDict[key][2:]:
                        if minutes > P:
                            attReport[key].append('a')
                        else:
                            attReport[key].append('x')

                # edit the path for the each output file
                outputFile = Abstract.options.store + "\\" + self._courseName + "-Attendance_Report.csv"
                # write data
                with open(outputFile, mode='w', encoding='latin1', newline="") as outf:
                    writer = csv.writer(outf)
                    writer.writerow(header)
                    for student in attReport.values():
                        writer.writerow(student)
        except IOError as e:
            print(e)
            exit(1)

    def _readParticipation(self):
        try:
            stdPrtPath = Abstract.options.part  # get participation files path
            Tb = Abstract.options.Tb
            Te = Abstract.options.Te
            prDict = copy.deepcopy(self._stdDict)  # deep copy to create a dictionary to store participation report
            # prDict[ID][0]=ID, prDict[ID][1]=name, prDict[ID][1+counter]: num of messages in the meeting
            header = ['Student ID', 'Student Name']
            counter = 0  # to indicate the number of file we are reading
            # edit the path to find files that match the name convention for participation files
            stdPrtPath += "\\" + self._courseName + "-[01][0-9]-[0-3][0-9]-[0-9][0-9][0-9][0-9]-PR.txt"
            files = glob.glob(stdPrtPath)  # store all files matching the convention
            if len(files) == 0:  # if no match was found, inform the user
                print("WARNING: No participation file was found\n")
                return
            for file in files:
                msgDict = {}  # to store the messages with the participant name as the key
                # extract the date from the file name
                date = str(file).split('\\')
                date = date[len(date) - 1]
                date = date.split('-')
                date = date[1:4]
                date = "-".join(date)
                header.append(date)
                counter += 1
                for key in prDict:  # initialize the number of messages to be zero
                    prDict[key].append(0)

                # create a file for non-valid participation
                nonValidPr = str(file)
                # extract the file name
                nonValidPr = nonValidPr.split('\\')
                nonValidPr = nonValidPr[len(nonValidPr) - 1]
                nonValidPr = Abstract.options.store + "\\" + re.sub(r'\.txt$', "-NV.txt", nonValidPr)
                nonValidPrFile = open(nonValidPr, mode="w", encoding='latin1')

                with open(file, mode="r", encoding='latin1') as f:  # to find the first and last messages
                    for line in f:
                        if line != "":
                            first_line = line  # store the first non blank line
                            break
                    else:  # if the file is empty, continue to the next file
                        nonValidPrFile.close()
                        continue

                    for line in f:
                        # sender name is always between "From" and "to"
                        # if a line does not contain these two words, it will be a wrapped message
                        bIndex = line.find('From')
                        eIndex = line.find('to')
                        if bIndex < 0 or eIndex < 0:
                            continue
                        last_line = line  # store the last line

                # extract the time of the first message
                b = first_line[0:8]
                b = b.split(':')
                # create datetime object to use in adding Tb to the time of first message sent
                firstMsg = datetime.datetime.combine(datetime.date(2001, 6, 17),
                                                     datetime.time(int(b[0]), int(b[1]), int(b[2]))) + datetime.timedelta(
                    minutes=Tb)

                # extract the time of the last message
                e = last_line[0:8]
                e = e.split(':')

                # create datetime object to use in subtracting Te from the time of last message sent
                lastMsg = datetime.datetime.combine(datetime.date(2001, 6, 17),
                                                    datetime.time(int(e[0]), int(e[1]), int(e[2]))) - datetime.timedelta(
                    minutes=Te)
                with open(file, mode="r", encoding='latin1') as f:
                    name = ""  # to indicate whether a sender was found

                    tbFlag = True  # will stay true until reaching the first message after Tb time
                    if Tb == 0:  # if Tb was not entered
                        tbFlag = False
                    else:
                        nonValidPrFile.write(f"Tb messages (Tb = {Abstract.options.Tb} minutes):\n")

                    teFlag = False  # will stay false until the reaching first message after Te time

                    for line in f:
                        # sender name is always between "From" and "to"
                        bIndex = line.find('From')
                        eIndex = line.find('to')
                        if bIndex < 0 or eIndex < 0:  # wrapped messages case
                            # if no name was stored, the message is before Tb
                            if name != "":
                                msgDict[name].append(line)
                            else:
                                nonValidPrFile.write(line)
                            continue
                        if tbFlag:
                            # compare the time
                            time = line[0:8]
                            time = time.split(':')
                            time = datetime.datetime.now().replace(year=2001, month=6, day=17, hour=int(time[0]),
                                                                   minute=int(time[1]),
                                                                   second=int(time[2]), microsecond=0)
                            if time < firstMsg:
                                nonValidPrFile.write(line)
                                continue
                            else:
                                tbFlag = False
                                nonValidPrFile.write("\n")  # write a blank line after writing all Tb messages

                        if Te != 0 and not teFlag:  # if the user entered Te, check if the message is after Te
                            # compare time
                            time = line[0:8]
                            time = time.split(':')
                            time = datetime.datetime.now().replace(year=2001, month=6, day=17, hour=int(time[0]),
                                                                   minute=int(time[1]),
                                                                   second=int(time[2]), microsecond=0)
                            if time > lastMsg:
                                nonValidPrFile.write(f"Te messages (Te = {Abstract.options.Te} minutes):\n")
                                teFlag = True

                        if teFlag:  # write messages after Te to non-valid file
                            nonValidPrFile.write(line)
                            continue

                        # extract sender name
                        name = line[bIndex + 5:eIndex - 1]
                        if name in msgDict:
                            msgDict[name][0] += 1  # increment the number of messages
                            msgDict[name].append(line)  # append the message
                        else:
                            msgDict[name] = [1, line]  # numOfMessages =1, and append the message to the list

                if teFlag:  # write a blank line after writing all Te messages
                    nonValidPrFile.write("\n")

                # the names are mapped after reading the whole file
                for student in msgDict.keys():  # mapping names or IDs to the students in the sheet
                    ID = re.search(r'[0-9]{7}', student)  # try mapping using ID
                    flag = False
                    if ID and ID.group() in self._stdDict.keys():
                        flag = True
                        prDict[ID.group()][1 + counter] += msgDict[student][0]
                    else:  # try mapping by name
                        prName = re.sub(r'[^A-Za-z\s]', "", student)  # remove non-alphabetical characters
                        for ID in prDict:
                            name = prDict[ID][1].strip().split(" ")
                            firs_surName = [name[0]]
                            firs_surName += name[3:]
                            firs_surName = " ".join(firs_surName)
                            ratio1 = lev.ratio(firs_surName.lower(), prName.lower())  # for first and surname
                            ratio2 = lev.ratio((name[0] + " " + name[1]).lower(),
                                               prName.lower())  # for first and second name
                            if ratio1 > .80 or ratio2 > .80:
                                prDict[ID][1 + counter] += msgDict[student][0]
                                flag = True

                    if not flag:  # if the name or ID does not match any student in the sheet
                        nonValidPrFile.write(f"\"{student}\" non-valid messages:\n")
                        for msg in msgDict[student][1:]:
                            nonValidPrFile.write(msg)
                        nonValidPrFile.write("\n")
                nonValidPrFile.close()

            # edit the output path for each meeting
            outputFile = Abstract.options.store + "\\" + self._courseName + "-Participation_Report.csv"
            with open(outputFile, mode='w', encoding='latin1', newline="") as outf:
                writer = csv.writer(outf)
                writer.writerow(header)
                for student in prDict.values():
                    writer.writerow(student)
        except IOError as e:
            print(e)
            exit(1)
