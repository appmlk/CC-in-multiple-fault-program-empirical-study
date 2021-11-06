import os
import pickle

from tqdm import trange

formulaList={"crosstab", "dstar", "jaccard", "ochiai", "op2", "turantula"}
strategyList={"clean", "exchange", "relabel"}


def getFileSmallExam(filePath):
    if os.path.exists(filePath):
        f = open(filePath, 'rb')
        content = pickle.load(f)
        f.close()
    minvalue=-1
    for key in content:
        if content[key][3]<minvalue or minvalue==-1:
            minvalue=content[key][3]
    return minvalue


def getSmallExam(MFverionPath):
    result={}
    outputPath=os.path.join(MFverionPath,"output")
    faultID=os.listdir(outputPath)[0]
    faultIDPath=os.path.join(outputPath,faultID)

    for formula in formulaList:
        result[formula] ={}
        result[formula]["normal"]={}
        filename="exam_coverage_normal_v1_"+formula
        # SmallValue=getFileSmallExam(os.path.join(faultIDPath,filename))
        filePath = os.path.join(faultIDPath, filename)
        if os.path.exists(filePath):
            f = open(filePath, 'rb')
            content = pickle.load(f)
            f.close()
        for key in content:
            # SmallValue_CC = getFileSmallExam(os.path.join(faultIDPath, filename_CC))
            # print("CC", formula,strategy, SmallValue_CC)
            # result[formula][strategy][key] = content[key][3]
            result[formula]["normal"][key] = content[key][3]
        # print("normal",formula,SmallValue)
        for strategy in strategyList:
            result[formula][strategy]={}
            filename_CC = "exam_coverage_cc_v1_"+strategy+"_" + formula
            filePath=os.path.join(faultIDPath, filename_CC)
            if os.path.exists(filePath):
                f = open(filePath, 'rb')
                content = pickle.load(f)
                f.close()
            for key in content:
                # SmallValue_CC = getFileSmallExam(os.path.join(faultIDPath, filename_CC))
                # print("CC", formula,strategy, SmallValue_CC)
                result[formula][strategy][key] = content[key][3]
    return result

if __name__ == "__main__":
    rootPath="/home/wwb/sirCCex"
    rootPath="/home/wwb/D4J/djtoSir_statement"
    # rootPath=r"D:\SIRData"
    projects=os.listdir(rootPath)

    ExamSmallResult={}
    TopResult={}
    ExamSmallResultPath=os.path.join(rootPath,"ScoreBigResult.txt")

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

    f = open(ExamSmallResultPath, 'wb')
    pickle.dump(ExamSmallResult,f)
    f.close()