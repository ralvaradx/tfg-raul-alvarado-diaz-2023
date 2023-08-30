class color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    MAGENTA = '\033[35m'

def progressBar(progress : int, total : int) -> str:
    progressPercentage = int(progress*100/total)
    progressBar = "[" + color.MAGENTA
    for i in range(progressPercentage):
        progressBar += "="
    progressBar += ">"
    for i in range(100 - progressPercentage - 1):
        progressBar += "-"
    progressBar += color.END + "] " + str(progressPercentage) + "%"
    print(progressBar, end='\r')

def finishProgressBar():
    progressBar(1,1)
    print()