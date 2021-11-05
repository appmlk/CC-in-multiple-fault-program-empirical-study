import os
import pickle


def checkAndSave(root, param, content):
    dump_path = root + "/" + param
    if not os.path.exists(dump_path):
        f = open(dump_path, 'wb')
        pickle.dump(content, f)
        f.close()


def readFile(Spath, Opath):
    covMatrix_path = Opath + "/covMatrix.in"
    fault_position_path = Opath + "/fault_location.txt"
    in_vector_path = Opath + "/in_vector.txt"

    if os.path.exists(Opath + "/covMatrix_project") and \
            os.path.exists(Opath + "/fault_project") and \
            os.path.exists(Opath + "/in_vector_project") and \
            os.path.exists(Opath + "/real_vector_project") and \
            os.path.exists(Opath + "/cc_project"):
        f = open(Opath + "/covMatrix_project", 'rb')
        covMatrix = pickle.load(f)
        f.close()
        f = open(Opath + "/fault_project", 'rb')
        fault = pickle.load(f)
        f.close()
        f = open(Opath + "/in_vector_project", 'rb')
        in_vector = pickle.load(f)
        f.close()
        f = open(Opath + "/real_vector_project", 'rb')
        real_vector = pickle.load(f)
        f.close()
        f = open(Opath + "/cc_project", 'rb')
        cc_list = pickle.load(f)
        f.close()

        failN = 0
        passN = 0
        for i in range(len(in_vector)):
            temp = int(in_vector[i])
            if temp == 1:
                failN += 1
            else:
                passN += 1
        return covMatrix, fault, in_vector, real_vector, cc_list, failN, passN

    if os.path.exists(Opath + "/covMatrix_project") and \
            os.path.exists(Opath + "/fault_project") and \
            os.path.exists(Opath + "/in_vector_project") and \
            os.path.exists(Opath + "/real_vector_project"):
        f = open(Opath + "/covMatrix_project", 'rb')
        covMatrix = pickle.load(f)
        f.close()
        f = open(Opath + "/fault_project", 'rb')
        fault = pickle.load(f)
        f.close()
        f = open(Opath + "/in_vector_project", 'rb')
        in_vector = pickle.load(f)
        f.close()
        f = open(Opath + "/real_vector_project", 'rb')
        real_vector = pickle.load(f)
        f.close()

        failN = 0
        passN = 0
        for i in range(len(in_vector)):
            temp = int(in_vector[i])
            if temp == 1:
                failN += 1
            else:
                passN += 1

        cc_list = []
        for index in range(len(in_vector)):
            if in_vector[index] == 0 and real_vector[index] == 1:
                cc_list.append(index)

        f = open(Opath + "/cc_project", 'wb')
        pickle.dump(cc_list, f)
        f.close()
        return covMatrix, fault, in_vector, real_vector, cc_list, failN, passN

    if not os.path.exists(covMatrix_path) or not os.path.exists(fault_position_path) or not os.path.exists(
            in_vector_path):
        return None, None, None, None, None, None, None

    f = open(covMatrix_path, 'r')
    tempCovMatrix = f.readlines()
    f.close()
    covMatrix = []
    for i in range(len(tempCovMatrix)):
        tempStatementlist = tempCovMatrix[i].split(' ')
        tempcovMatrix = []
        for j in range(len(tempStatementlist)):
            tempStatement = tempStatementlist[j]
            if tempStatement != "":
                tempcovMatrix.append(int(tempStatement))
        covMatrix.append(tempcovMatrix)

    f = open(fault_position_path, 'r')
    fault_position = f.readlines()
    fault = []
    for i in range(len(fault_position)):
        temp = int(fault_position[i].split(" :")[0].split("line ")[1]) - 1
        fault.append(temp)

    f = open(in_vector_path, 'r')
    in_vector_str = f.read()
    f.close()
    in_vector = []

    failN = 0
    passN = 0
    for i in range(len(in_vector_str)):
        temp = int(in_vector_str[i])
        in_vector.append(temp)
        if temp == 1:
            failN += 1
        else:
            passN += 1
    real_vector = []
    for t in range(len(in_vector)):
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
    for index in range(len(in_vector)):
        if in_vector[index] == 0 and real_vector[index] == 1:
            cc_list.append(index)

    f = open(Opath + "/covMatrix_project", 'wb')
    pickle.dump(covMatrix, f)
    f.close()
    f = open(Opath + "/fault_project", 'wb')
    pickle.dump(fault, f)
    f.close()
    f = open(Opath + "/in_vector_project", 'wb')
    pickle.dump(in_vector, f)
    f.close()
    f = open(Opath + "/real_vector_project", 'wb')
    pickle.dump(real_vector, f)
    f.close()
    f = open(Opath + "/cc_project", 'wb')
    pickle.dump(cc_list, f)
    f.close()
    return covMatrix, fault, in_vector, real_vector, cc_list, failN, passN


def merge(StaticFeature, DynamicFeature):
    FinalFeature = []
    for index in range(len(StaticFeature)):
        item1 = StaticFeature[index]
        item2 = DynamicFeature[index]
        FinalFeature.append(item1 + item2)
    return FinalFeature


# project_files = ["sed", "grep", "totinfo", "tcas", "schedule", "schedule2", "printtokens2", "printtokens","replace"]
def splitParameter(content_list, project_file):
    finalList = []
    for item in content_list:
        if "timeout" in item:
            strs = item.split(" ")
            strs = strs[3:]
            finalList.append(" ".join(strs))
        elif "$source/sed" in item:
            strs = item.split(" ")
            strs = strs[1:]
            finalList.append(" ".join(strs))
    return finalList


def checkurl(param):
    if not os.path.exists(param):
        os.mkdir(param)


def saveResult(O_version_output_path, file_name, formula_name, cost, exam, fault_of_cost):
    checkAndSave(O_version_output_path, "cost_" + file_name + "_" + formula_name, cost)
    checkAndSave(O_version_output_path, "exam_" + file_name + "_" + formula_name, exam)
    checkAndSave(O_version_output_path, "fault_" + file_name + "_" + formula_name, fault_of_cost)

def readFileD4J(singleOutputPath, singleFeaturePath):
    faultFile = pickle.load(open(singleOutputPath + "/faultFile.txt", 'rb'))
    faultLineIndex = pickle.load(open(singleOutputPath + "/faultLineIndex.txt", 'rb'))

    coveMethodIndex = pickle.load(open(singleFeaturePath + "/coveMethodIndex.txt", 'rb'))
    coveStatementIndex = pickle.load(open(singleFeaturePath + "/coveStatementIndex.txt", 'rb'))
    covMatrix_method = pickle.load(open(singleFeaturePath + "/covMatrix_method.txt", 'rb'))
    covMatrix_statement = pickle.load(open(singleFeaturePath + "/covMatrix_statement.txt", 'rb'))

    inVector = pickle.load(open(singleFeaturePath + "/inVector.txt", 'rb'))

    fault_statement=[]
    fault_method=[]
    #找到错误的语句
    for key in faultLineIndex:
        fault_lines=faultLineIndex[key]
        for fault_line in fault_lines:
            temp=key.split("/")
            fault_file_name=temp[len(temp)-1]
            fault_file_name=temp[len(temp)-2]+"::"+fault_file_name.split(".java")[0]
            for statement_index in range(len(coveStatementIndex)):
                statement_line=coveStatementIndex[statement_index]
                file_name=statement_line.split("::")[1]
                temp = file_name.split(".")
                file_name=temp[len(temp)-2]+"::"+temp[len(temp)-1]
                if file_name==fault_file_name:
                    file_line=int(statement_line.split("::")[4])
                    if file_line==fault_line:
                        fault_statement.append(statement_index)

    for statement_fault in fault_statement:
        fault_statement_line = coveStatementIndex[statement_fault]
        for method_index in range(len(coveMethodIndex)):
            method_line=coveMethodIndex[method_index]
            if fault_statement_line.startswith(method_line):
                if method_index not in fault_method:
                    fault_method.append(method_index)

    return inVector,covMatrix_statement,fault_statement,covMatrix_method,fault_method