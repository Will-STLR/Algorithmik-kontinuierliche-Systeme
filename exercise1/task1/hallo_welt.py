#!/usr/bin/env python3

def hallo_welt():
    """Prints ``Hallo, Welt!`` on the command line."""
    print("Hallo, Welt!")



def hallo_name(name):
    """Prints ``Hallo, <name>!`` on the command line,
    where <name> is the contents of the variable `name`.

    Args:
        name (str):
            The string that is to be printed.
    """
    print(f"Hallo, {name}!")


def main():
    """The Main-Function of the programme. Should
    call ``hallo_welt`` and ``hallo_name``, the latter
    herein with an arbitrary parameter."""
    hallo_welt()
    hallo_name("Lisa")


# TODO: Execute the Main-Function whenever the module is
#       called directly from the command line.
if __name__ == "__main__":
    main()
