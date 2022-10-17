This project is done by Ahmad Abbas and Aseel Sabri 

The project keep track of attendance sheets and participation of students during online sessions on ZOOM platform.

• To run the project, run the Driver.py file in the terminal, 
  the path of the students' list sheet must be entered as an argument

• other optional arguments are:

  -a DIRECTORY, --att=DIRECTORY
                        attendance reports' folder path
  -r DIRECTORY, --part=DIRECTORY
                        participation reports' folder path
  -s DIRECTORY, --store=DIRECTORY
                        output files path
  -P P                  minimum minutes to consider attendance
  -b TB, --Tb=TB        discard participation in the first Tb minutes
  -e TE, --Te=TE        discard participation in the last Te minutes

• if input path was not provided, it will be considered to be the current directory
• if the ouptut path was not provided, a dirictory named "output_file" will be created in the current dirictory to store the output files in


