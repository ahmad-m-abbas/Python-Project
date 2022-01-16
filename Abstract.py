class Abstract:
    """Abstract class that contains functions' prototype and parser options"""
    import optparse
    import os

    # Python project file path, used as default for attendance and participation path
    module_path = os.path.dirname(os.path.realpath(__file__))

    # to create output directory in python project file path, used as default path to store output files
    output_path = os.path.join(module_path, 'output_file')

    parser = optparse.OptionParser("Usage: %prog  PATH_TO_STUDENT_LIST_SHEET")

    parser.add_option("-a", "--att", default=module_path, type=str,
                      help="attendance reports' folder path", metavar="DIRECTORY")
    parser.add_option("-r", "--part", default=module_path, type=str,
                      help="participation reports' folder path", metavar="DIRECTORY")
    parser.add_option("-s", "--store", default=output_path, type=str,
                      help="output files path", metavar="DIRECTORY")
    parser.add_option("-P", default=0, type=int,
                      help="minimum minutes to consider attendance")
    parser.add_option("-b", "--Tb", default=0, type=int,
                      help="discard participation in the first Tb minutes")
    parser.add_option("-e", "--Te", default=0, type=int,
                      help="discard participation in the last Te minutes")
    (options, args) = parser.parse_args()

    # if the user did not enter an argument
    if len(args) != 1:
        parser.error("INCORRECT NUMBER OF ARGUMENTS")

    # check whether student list sheet path is valid, if not exit the program
    if not os.path.isfile(args[0]):
        parser.error("Student list file or path does not exist!")

    # check whether the attendance reports path exists, if not exit the program
    if not os.path.exists(options.att):
        parser.error("Attendance reports' folder path does not exist!")

    # check whether the participation reports path exists, if not exit the program
    if not os.path.exists(options.part):
        parser.error("Participation reports' folder path does not exist!")

    # check whether the passed integers are negative
    if options.P < 0 or options.Tb < 0 or options.Te < 0:
        parser.error("Number of minutes cannot be negative!")

    # check whether the output path exists, if not create one
    if not os.path.exists(options.store):
        os.mkdir(options.store)

    def __init__(self):
        self._stdDict = {}  # to store student IDs as keys for the data
        self._studentData = []  # to store students' data
        # store the course name
        self._courseName = Abstract.args[0].split('\\')
        self._courseName = self._courseName[len(self._courseName) - 1].split('-')
        self._courseName = self._courseName[0]
        self._readStudentList()
        self._readAttendance()
        self._readParticipation()

    # functions' prototypes
    def _readStudentList(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def _readAttendance(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def _readParticipation(self):
        raise NotImplementedError("Subclass must implement abstract method")
