import os


def main():
    commandToRun = os.environ.get('COMMAND')
    data = os.environ.get('DATA')

    print "INSIDE TESTSCRIPTPARAMS"
    print "commandToRun: " + commandToRun
    print "data: " + data

if __name__ == "__main__":
    main()