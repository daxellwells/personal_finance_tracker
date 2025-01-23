def main_menu():
    selection = 1
    while selection != -1:
        print("please make a selection:")
        print("1. add transaction")
        print("2. print transactions")
        print("\n-1 quit program\n")
        selection = input()
        print(selection[1:])
        if not selection.isdigit() and not (selection.startswith("-") and selection[1:].isdigit()):
            print("ERROR: please input a valid selection (number)")
            continue
        selection = int(selection)
        if selection > 2 or selection < -1:
            print("ERROR: please make a valid selection")
            continue
        if selection == -1:
            return 0
    pass


if __name__ == "__main__":
    main_menu()