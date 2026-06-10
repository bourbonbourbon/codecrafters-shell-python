import sys


def main():
    _shell_builtins = ["echo", "exit", "type"]
    while True:
        sys.stdout.write("$ ")
        user_input = input()

        command = user_input.split()[0]
        args = user_input.split()[1:]


        if command == "exit":
            sys.exit(0)

        elif command == "echo":
            print(" ".join(args))

        elif command == "type":
            if args[0] in _shell_builtins:
                print(f"{args[0]} is a shell builtin")
            else:
                print(f"{args[0]}: not found")

        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
