import random
import statistics
import time
import matplotlib.pyplot as plt
import mysql.connector
import json
import numpy as np

print(f"🧬 GENERATION ")
print("\n🔬 FINAL RESULT")
# connecting to the database
dataBase = mysql.connector.connect(
    host="localhost",
    user="shir",
    passwd="bendshir",
    database="macrodatabase")

# preparing a cursor object
cursorObject = dataBase.cursor()

ele3 = 293.5938837528229
ele1 = 15.221281051635742
ele2 = 6.301144123077393
mdc2 = 4.851024389266968
MDC3 = 1.1658821105957031
MDC1 = 1.3174762725830078
ktr1 = 0.3031883239746094
ktr2 = 0.2563142776489258
ktr3 = 0.2822458744049072

x = [293.5938837528229,15.221281051635742,6.301144123077393, 4.851024389266968,1.1658821105957031,1.3174762725830078
     ,0.3031883239746094,0.2563142776489258,0.2822458744049072 ]
print(statistics.mean(x))
print(statistics.stdev(x))

mdc3_fit_max = [0.92, 0.9087323943661972, 0.8823943661971831, 0.9147058823529411]
mdc3_fit_avg = [0.7946558141021504, 0.8108525609071132, 0.8160802090365831, 0.8255174406014507]
mdc1_fit_max = [0.8947368421052632, 0.9263157894736842, 0.9263157894736842, 0.9333333333333333, 0.9411764705882354]
mdc1_fit_avg = [0.7271176675399251, 0.7400369312597724, 0.7555084381872881, 0.7790081866032769, 0.8005658516188794]
mdc2_fit_max = [0.9272727272727274, 0.9272727272727274, 0.9181818181818182, 0.9181818181818182]
mdc2_fit_avg = [0.8189091457296618, 0.8429395364379195, 0.8505504680977575, 0.8175061515454658]



ktr1_fit_max =[0.8666666666666667, 0.8666666666666667, 0.8666666666666667, 0.8666666666666667]
ktr1_fit_avg =  [0.7225323827760225, 0.7225323827760225, 0.7225323827760225, 0.7225323827760225]
ktr2_fit_avg =  [0.8124643845048257, 0.8124643845048257, 0.8018794398400273, 0.8126366919504174]
ktr2_fit_max =  [0.9333333333333333, 0.9333333333333333, 0.9333333333333333, 0.9333333333333333]
ktr3_fit_max = [0.9, 0.9, 0.9, 0.9]
ktr3_fit_avg = [0.8137091275463387, 0.8218585950684705, 0.817266963818991, 0.817266963818991]


ele1_fit_max = [0.9714285714285715, 0.9714285714285715, 0.9771428571428572, 0.9771428571428572]
ele1_fit_avg =[0.9304177055931087, 0.9084523616484541, 0.9188949834976599, 0.9268175148669997]
ele2_fit_max =[0.991304347826087, 0.991304347826087, 0.991304347826087, 0.991304347826087]
ele2_fit_avg = [0.9601065116737109, 0.948756995094678, 0.9483768167691394, 0.9526293634056746]
ele3_fit_max = [0.9906250000000001, 0.9876923076923078, 0.9876923076923078, 0.9846153846153847]
ele3_fit_avg = [0.9676017797079816, 0.9682098747958997, 0.9682098747958997, 0.9614609356725131]



def graph1():
    """
    the output graph
    """
    # MDC 1
    x1 = list(range(1, len(mdc1_fit_max)+1))
    y1 = mdc1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='blue', label="Medical infusion kit-1")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    #plt.title('Max fitness value per generation:')
    # MDC 3
    x1 = list(range(1, len(mdc3_fit_max) + 1))
    y1 = mdc3_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='dodgerblue', label="Medical infusion kit-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # MDC 2
    x1 = list(range(1, len(mdc2_fit_max) + 1))
    y1 = mdc2_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='royalblue', label="Medical infusion kit-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')

    # KTR 1
    x1 = list(range(1, len(ktr1_fit_max) + 1))
    y1 = ktr1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='red', label="Plastic lid-1")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # KTR 2
    x1 = list(range(1, len(ktr2_fit_max) + 1))
    y1 = ktr2_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='coral', label="Plastic lid-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # KTR 3
    x1 = list(range(1, len(ktr3_fit_max) + 1))
    y1 = ktr3_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='lightcoral', label="Plastic lid-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # ELE 1
    x1 = list(range(1, len(ele1_fit_max) + 1))
    y1 = ele1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='orange', label="Smart light compartment-1")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # ELE 2
    x1 = list(range(1, len(ele2_fit_max) + 1))
    y1 = ele2_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='sandybrown', label="Smart light compartment-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # ELE 3
    x1 = list(range(1, len(ele3_fit_max) + 1))
    y1 = ele3_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='gold', label="Smart light compartment-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # show a legend on the plot
    plt.legend(loc=4, prop={'size': 16})
    plt.xticks(range(1, 6))
    plt.ylim(0.8,1)
    # function to show the plot
    plt.show()

def graph2():
    """
    the output graph
    """
    # MDC 1
    x1 = list(range(1, len(mdc1_fit_avg)+1))
    y1 = mdc1_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='blue', label="MDC-1")
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    #plt.title('Average fitness value per generation:')
    # MDC 2
    x1 = list(range(1, len(mdc2_fit_avg) + 1))
    y1 = mdc2_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='royalblue', label="MDC-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # MDC 3
    x1 = list(range(1, len(mdc3_fit_avg) + 1))
    y1 = mdc3_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='dodgerblue', label="MDC-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # KTR 1
    x1 = list(range(1, len(ktr1_fit_avg) + 1))
    y1 = ktr1_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='red', label="KTR-1")
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # KTR 2
    x1 = list(range(1, len(ktr2_fit_avg) + 1))
    y1 = ktr2_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='coral', label="KTR-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # KTR 3
    x1 = list(range(1, len(ktr3_fit_avg) + 1))
    y1 = ktr3_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='lightcoral', label="KTR-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # ELE 1
    x1 = list(range(1, len(ele1_fit_avg) + 1))
    y1 = ele1_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='orange', label="ELE-1")
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # ELE 2
    x1 = list(range(1, len(ele2_fit_avg) + 1))
    y1 = ele2_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='sandybrown', label="ELE-2", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Average value')
    # ELE 3
    x1 = list(range(1, len(ele3_fit_avg) + 1))
    y1 = ele3_fit_avg
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='gold', label="ELE-3", linestyle='dashed')
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # show a legend on the plot
    plt.legend()
    plt.xticks(range(1, 6))
    plt.ylim(0.7,1)
    # function to show the plot
    plt.show()


def graph3():
    """
    for the paper
    """
    # MDC 1
    x1 = list(range(1, len(mdc1_fit_max) + 1))
    y1 = mdc1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='blue', label="Medical infusion kit ")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # plt.title('Max fitness value per generation:')
    # KTR 1
    x1 = list(range(1, len(ktr1_fit_max) + 1))
    y1 = ktr1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='red', label="Plastic lid ")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # ELE 1
    x1 = list(range(1, len(ele1_fit_max) + 1))
    y1 = ele1_fit_max
    # plotting the line 1 points
    plt.rcParams.update({'font.size': 22})
    plt.plot(x1, y1, color='orange', label="Smart light compartment")
    plt.xlabel('Generation')
    plt.ylabel('Fitness value')
    # show a legend on the plot
    plt.legend()
    plt.xticks(range(1, 6))
    plt.ylim(0.8, 1)
    # function to show the plot
    plt.show()

graph1()
plt.clf()
graph1()