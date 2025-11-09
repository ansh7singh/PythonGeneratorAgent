from functions1.get_file_info import get_file_info
from functions1.get_file_content import get_file_content
from functions1.get_write_file_content import write_file
from functions1.run_python_file import run_python_file
def main():
    working_directory = "calculator"
    print(run_python_file(working_directory,"main.py" , ["3+5"]))

    

main()