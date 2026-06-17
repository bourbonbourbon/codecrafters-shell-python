import os
import re
import sys
import typing
import subprocess

def get_command_and_args(user_input):
    command = ""
    args_list = []

    in_single = False
    in_double = False
    escape_next = False
    c_list = []

    for i, ch in enumerate(user_input):

        if escape_next:
            escape_next = False
            c_list.append(ch)
            continue

        if ch.isspace() and not in_single and not in_double:
            if c_list:
                if command == "":
                    command = "".join(c_list)
                    user_input = user_input[i + 1:]
                else:
                    args_list.append("".join(c_list))
                c_list = []
            continue

        if ch == "\\" and not in_single:
            escape_next = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            continue

        if ch == "\"" and not in_single:
            in_double = not in_double
            continue

        if ch != "'" or ch != "\"" and in_single or in_double:
            c_list.append(ch)
            continue

        if not in_single:
            c_list.append(ch)
            continue

        if not in_double:
            c_list.append(ch)
            continue

    # for the last or only arg
    if c_list:
        if command == "":
            command = "".join(c_list)
        else:
            args_list.append("".join(c_list))

    return command, args_list

def preprocess_redirection(user_input):
    command = re.split(" 1> | > ", user_input)

    if len(command) < 2:
        return command[0], ""

    if not os.path.exists(os.path.abspath(command[1])):
        try:
            fp = open(os.path.abspath(command[1]), "w", encoding="UTF-8")
        except PermissionError:
            pass
        else:
            with fp:
                pass

    return command[0], os.path.abspath(command[1])


def send_stdout_redirection(stdout_redirect_file, stdout):
    if stdout_redirect_file != "":
        try:
            fp = open(stdout_redirect_file, "w", encoding="UTF-8")
        except PermissionError:
            pass
        else:
            with fp:
                fp.write(stdout)


def main():
    _shell_builtins: list[str] = ["echo", "exit", "type", "pwd", "cd"]
    _path = os.getenv("PATH")

    while True:
        sys.stdout.write("$ ")
        user_input = input()

        if user_input == "":
            continue

        try:
            user_input, stdout_redirect_file = preprocess_redirection(user_input)
        except PermissionError:
            pass

        command, args = get_command_and_args(user_input)


        # command redirection for shell internals as well

        if command == "exit":
            sys.exit(0)

        elif command == "echo":
            if args:
                if stdout_redirect_file == "":
                    print(" ".join(args))
            send_stdout_redirection(stdout_redirect_file, " ".join(args))
            continue

        elif command == "pwd":
            if stdout_redirect_file == "":
                print(os.getcwd())
            send_stdout_redirection(stdout_redirect_file, os.getcwd())
            continue

        elif command == "cd":
            try:
                if args[0] == "~":
                    os.chdir(os.getenv("HOME"))
                else:
                    os.chdir(args[0])
            except (FileNotFoundError, PermissionError, NotADirectoryError):
                print(f"cd: {args[0]}: No such file or directory")

            continue

        elif command == "type":
            command_found_in_path = False

            if not args:
                continue

            if args[0] in _shell_builtins:
                if stdout_redirect_file == "":
                    print(f"{args[0]} is a shell builtin")
                send_stdout_redirection(stdout_redirect_file, f"{args[0]} is a shell builtin")
                continue

            elif args[0] not in _shell_builtins:
                for path_dir in _path.split(":"):
                    exe_path = os.path.join(path_dir, args[0])
                    if os.path.exists(exe_path):
                        if os.access(exe_path, os.R_OK | os.X_OK):
                            if stdout_redirect_file == "":
                                print(f"{args[0]} is {exe_path}")
                            send_stdout_redirection(stdout_redirect_file, f"{args[0]} is {exe_path}")
                            command_found_in_path = True
                            break

            if not command_found_in_path:
                print(f"{args[0]}: not found")
                send_stdout_redirection(stdout_redirect_file, f"{args[0]}: not found")

            continue

        command_found_in_path = False
        for path_dir in _path.split(":"):
            exe_path = os.path.join(path_dir, command)
            if os.path.exists(exe_path):
                if os.access(exe_path, os.R_OK | os.X_OK):
                    command_found_in_path = True
                    break

        if command_found_in_path:
            # print(command, args)
            # print(stdout_redirect_file)
            if args:
                p = subprocess.run([command, *args], check=False, capture_output=True)
            else:
                p = subprocess.run([command], check=False, capture_output=True)

            if p.stdout.decode().rstrip() != "":
                if stdout_redirect_file != "":
                    print(p.stdout.decode(), end="")
            if  p.stderr.decode().rstrip() != "":
                print(p.stderr.decode(), end="")
            send_stdout_redirection(stdout_redirect_file, p.stdout.decode())

            continue

        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
