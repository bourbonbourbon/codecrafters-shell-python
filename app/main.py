import os
import sys
import subprocess

def args_preprocessor(args):
    args_stack = []
    q_stack = []
    char_stack = []
    q_stack_len = 0
    for c in args:
        if c == "'":
            if q_stack_len != 0:
                item = q_stack.pop()
                if item and c == "'":
                    q_stack_len -= 1
                    args_stack.append("".join(char_stack).strip())
                    char_stack = []
                else:
                    q_stack.append(item)
            else:
                q_stack.append(c)
                q_stack_len += 1
        else:
            char_stack.append(c)

    return args_stack



def main():
    _shell_builtins: list[str] = ["echo", "exit", "type", "pwd", "cd"]
    _path = os.getenv("PATH")

    while True:
        sys.stdout.write("$ ")
        user_input = input()

        command = user_input.split()[0]
        args = user_input.removeprefix(command + " ")

        args = args_preprocessor(args)

        if command == "exit":
            sys.exit(0)

        elif command == "echo":
            print(" ".join(args))
            continue

        elif command == "pwd":
            print(os.getcwd())
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

            if args[0] in _shell_builtins:
                print(f"{args[0]} is a shell builtin")
                continue

            elif args[0] not in _shell_builtins:
                for path_dir in _path.split(":"):
                    exe_path = os.path.join(path_dir, args[0])
                    if os.path.exists(exe_path):
                        if os.access(exe_path, os.R_OK | os.X_OK):
                            print(f"{args[0]} is {exe_path}")
                            command_found_in_path = True
                            break

            if not command_found_in_path:
                print(f"{args[0]}: not found")

            continue

        command_found_in_path = False
        for path_dir in _path.split(":"):
            exe_path = os.path.join(path_dir, command)
            if os.path.exists(exe_path):
                if os.access(exe_path, os.R_OK | os.X_OK):
                    command_found_in_path = True
                    break

        if command_found_in_path:
            try:
                subprocess.run([command, *args], check=True)
            except subprocess.CalledProcessError:
                pass
            continue

        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
