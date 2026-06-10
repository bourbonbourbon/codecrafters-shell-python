import os
import sys
import subprocess


def main():
    _shell_builtins = ["echo", "exit", "type"]
    _path = os.getenv("PATH")

    while True:
        sys.stdout.write("$ ")
        user_input = input()

        command = user_input.split()[0]
        args = user_input.split()[1:]

        if command == "exit":
            sys.exit(0)

        elif command == "echo":
            print(" ".join(args))
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
                        if os.access(exe_path, os.R_OK & os.X_OK):
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
                if os.access(exe_path, os.R_OK & os.X_OK):
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
