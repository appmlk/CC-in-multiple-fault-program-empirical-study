from tool import ToolIO


def average(alist1):
    sum = 0
    for item in alist1:
        sum += item
    if len(alist1) > 0:
        return sum / len(alist1)
    else:
        return 0


def getEXAM(sus_value, fault_location):
    fault_of_cost = []
    cost = {}
    exam = {}
    sus_find = []

    cost_temp = {}
    dict = sorted(sus_value.items(), key=lambda d: d[1], reverse=True)

    for index in range(len(dict)):
        line_no = dict[index][0]
        if line_no in fault_location:
            sus_find.append(dict[index][1])
            cost_temp[4] = index + 1
            fault_of_cost.append(line_no)

    for sus_index in range(len(sus_find)):
        cost[sus_index] = {}
        exam[sus_index] = {}
        first_index = -1
        end_index = -1
        sus_record = sus_find[sus_index]
        for sus_item in range(len(dict)):
            if dict[sus_item][1] == sus_record and first_index == -1:
                first_index = sus_item + 1
            if first_index != -1 and dict[sus_item][1] != sus_record:
                end_index = sus_item
                break
        if end_index == -1:
            end_index = len(dict)
        average_index = (first_index + end_index) / 2
        cost[sus_index][1] = first_index
        cost[sus_index][2] = end_index
        cost[sus_index][3] = average_index
        exam[sus_index][1] = first_index / len(sus_value)
        exam[sus_index][2] = end_index / len(sus_value)
        exam[sus_index][3] = average_index / len(sus_value)

    return cost, exam, fault_of_cost


def getTop(sus_value, fault_location, TopList):
    TopList.sort(reverse=True)
    top_num = {}
    for item in TopList:
        top_num[item] = 0
    sus_find = []

    dict = sorted(sus_value.items(), key=lambda d: d[1], reverse=True)

    for index in range(len(dict)):
        line_no = dict[index][0]
        if line_no in fault_location:
            sus_find.append(dict[index][1])

    for sus_index in range(len(sus_find)):
        first_index = -1
        sus_record = sus_find[sus_index]
        for sus_item in range(len(dict)):
            if dict[sus_item][1] == sus_record and first_index == -1:
                first_index = sus_item + 1
                break
        for item in reversed(TopList):
            if first_index <= item:
                top_num[item] += 1
                break

    return top_num


def dealCCMetric(suspicion_list,file_name, fault,FormulaName,O_version_output_path):
    suspicion_list1={}
    suspicion_list2={}
    suspicion_list3={}
    for index in suspicion_list:
        item = suspicion_list[index]
        if not isinstance(item,int):
            suspicion_list1[index]=(item[0])
            suspicion_list2[index]=(item[1])
            suspicion_list3[index]=(item[2])
        else:
            suspicion_list1[index]=(item)
            suspicion_list2[index]=(item)
            suspicion_list3[index]=(item)

    cost, exam, fault_of_cost = getEXAM(suspicion_list1, fault)
    # top_num = getTop(suspicion_list1, fault, TopList)
    ToolIO.saveResult(O_version_output_path, file_name+"_clean", FormulaName, cost, exam, fault_of_cost)

    cost, exam, fault_of_cost = getEXAM(suspicion_list2, fault)
    # top_num = getTop(suspicion_list2, fault, TopList)
    ToolIO.saveResult(O_version_output_path, file_name+"_relabel", FormulaName, cost, exam, fault_of_cost)

    cost, exam, fault_of_cost = getEXAM(suspicion_list3, fault)
    # top_num = getTop(suspicion_list3, fault, TopList)
    ToolIO.saveResult(O_version_output_path, file_name+"_exchange", FormulaName, cost, exam, fault_of_cost)


def findCC(inVector, covMatrix, fault):
    failN = 0
    passN = 0
    for i in range(len(inVector)):
        temp = inVector[i]
        if temp == 1:
            failN += 1
        else:
            passN += 1
    real_vector = []
    for t in range(len(inVector)):
        isPass = True
        for fs in fault:
            # print(t)
            # print(fs)
            # print(len(covMatrix))
            # print(len(covMatrix[t]))
            # print(tempCovMatrix[t])
            if covMatrix[t][fs] == 1:
                isPass = False
                break
        if isPass:
            real_vector.append(0)
        else:
            real_vector.append(1)

    cc_list = []
    for index in range(len(inVector)):
        if inVector[index] == 0 and real_vector[index] == 1:
            cc_list.append(index)
    
    return real_vector, cc_list, failN, passN