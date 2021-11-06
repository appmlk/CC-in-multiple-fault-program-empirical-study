import os
import pickle

from tqdm import trange

formulaList={"crosstab", "dstar", "jaccard", "ochiai", "op2", "turantula"}
strategyList={"clean", "exchange", "relabel"}
innerPath="output"

def getFileSmallExam(filePath):
    TopList = [1, 3, 5, 10]
    TopList.sort(reverse=True)
    temp={}
    for item in TopList:
        temp[item] = 0
    if os.path.exists(filePath):
        f = open(filePath, 'rb')
        content = pickle.load(f)
        f.close()
    minvalue=-1
    for key in content:
        for item in reversed(TopList):
            if content[key][3] <= item:
                temp[item] += 1
                break
    return temp

def whichFaultIsMin(faultIDList, outputPath):
    minFault={}
    for formula in formulaList:
        faultIDPath = os.path.join(outputPath, faultIDList[0])
        filename = "exam_coverage_normal_v1_" + formula
        filename_fault = "fault_coverage_normal_v1_" + formula
        filePath=os.path.join(faultIDPath,filename)
        faultPath=os.path.join(faultIDPath,filename_fault)
        if os.path.exists(filePath):
            f = open(filePath, 'rb')
            content = pickle.load(f)
            f.close()
        if os.path.exists(faultPath):
            f = open(faultPath, 'rb')
            faultcontent = pickle.load(f)
            f.close()
        minFlag=-1
        minValue=-1
        for key in content:
            if content[key][3] < minValue or minValue == -1:
                minValue = content[key][3]
                minFlag=key
        minFault[formula]=faultcontent[minFlag]
    return minFault


def getSmallExam(MFverionPath):
    result={}
    outputPath=os.path.join(MFverionPath,innerPath)
    faultIDList=os.listdir(outputPath)

    minFault=whichFaultIsMin(faultIDList,outputPath)

    for formula in formulaList:
        faultID=minFault[formula]
        faultIDPath = os.path.join(outputPath, str(faultID))

        result[formula] ={}
        result[formula]["normal"] = {}
        filename="cost_coverage_normal_v1_"+formula
        SmallValue = getFileSmallExam(os.path.join(faultIDPath, filename))
        result[formula]["normal"] = SmallValue
        for type in ["a","a_b","una"]:
            result[formula][type]={}
            for strategy in strategyList:
                result[formula][type][strategy] = {}
                filename_CC = "cost_coverage_cc_v1_"+type+"_"+strategy+"_" + formula
                SmallValue_CC = getFileSmallExam(os.path.join(faultIDPath, filename_CC))
                result[formula][type][strategy] = SmallValue_CC
    return result

if __name__ == "__main__":
    # rootPath="/home/wwb/sirCCex"
    # rootPath="/home/wwb/D4J/djtoSir_statement"
    # rootPath="/home/wwb/D4J/djtoSir_method"
    # rootPath=r"D:\SIRData"
    Paths=["/home/wwb/D4J/djtoSir_method"]
    for rootPath in Paths:
        projects=os.listdir(rootPath)

        ExamSmallResult={}
        TopResult={}
        ExamSmallResultPath=os.path.join(rootPath,"BigThreeResult_Top.txt")

        for project in projects:
            projectPath=os.path.join(rootPath,project)
            MFPath=os.path.join(projectPath,"MFoutput")
            SFPath=os.path.join(projectPath,"SFoutput")
            if not os.path.exists(MFPath):
                continue

            ExamSmallResult[project]={}
            TopResult[project]={}

            versionList=os.listdir(MFPath)
            print("current project",project)
            for versionIndex in trange(len(versionList)):
                version=versionList[versionIndex]
                MFverionPath=os.path.join(MFPath,version)
                SFverionPath=os.path.join(SFPath,version)

                outputPath = os.path.join(MFverionPath, innerPath)
                innerPathList=os.listdir(outputPath)
                if len(innerPathList)==0:
                    continue

                ExamResult=getSmallExam(MFverionPath)
                ExamSmallResult[project][version] = ExamResult

        f = open(ExamSmallResultPath, 'wb')
        pickle.dump(ExamSmallResult,f)
        f.close()