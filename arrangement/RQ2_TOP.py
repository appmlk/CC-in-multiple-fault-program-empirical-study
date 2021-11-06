import os
import pickle

from tqdm import trange

formulaList={"crosstab", "dstar", "jaccard", "ochiai", "op2", "turantula"}
strategyList={"clean", "exchange", "relabel"}


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


def getSmallExam(MFverionPath):
    result={}
    outputPath=os.path.join(MFverionPath,"output")
    faultID=os.listdir(outputPath)[0]
    faultIDPath=os.path.join(outputPath,faultID)

    for formula in formulaList:
        result[formula] ={}
        filename="cost_coverage_normal_v1_"+formula
        SmallValue=getFileSmallExam(os.path.join(faultIDPath,filename))
        result[formula]["normal"] = SmallValue
        # print("normal",formula,SmallValue)
        for strategy in strategyList:
            filename_CC = "cost_coverage_cc_v1_"+strategy+"_" + formula
            SmallValue_CC = getFileSmallExam(os.path.join(faultIDPath, filename_CC))
            # print("CC", formula,strategy, SmallValue_CC)
            result[formula][strategy] = SmallValue_CC
    return result


if __name__ == "__main__":
    # rootPath="/home/wwb/sirCCex"
    # rootPath="/home/wwb/D4J/djtoSir_statement"
    # rootPath=r"D:\SIRData"
    Paths=["/home/wwb/sirCCex","/home/wwb/D4J/djtoSir_statement"]
    for rootPath in Paths:
        projects=os.listdir(rootPath)

        ExamSmallResult={}
        TopResult={}
        TopResultPath=os.path.join(rootPath,"TopResult.txt")

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

                outputPath = os.path.join(MFverionPath, "output")
                innerPathList=os.listdir(outputPath)
                if len(innerPathList)==0:
                    continue

                ExamResult=getSmallExam(MFverionPath)
                ExamSmallResult[project][version] = ExamResult

        f = open(TopResultPath, 'wb')
        pickle.dump(ExamSmallResult,f)
        f.close()