import multiprocessing
import os
import sys

from method import CalSus
from tool import ToolIO, DynamicFeatureExtract, StaticFeatureExtract, CChandle, ToolMetric, ToolCluster
import seaborn as sns
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from pyclustering.cluster import cluster_visualizer

def dealSingleVersion(root_path, project_path, project_file, S_path, O_path, singe_version):
    print(project_file,singe_version)
    # 读取覆盖信息
    S_version_path = S_path + "/" + singe_version
    O_version_path = O_path + "/" + singe_version

    # if os.path.isdir(O_version_path+"/output"):
    #     print(O_version_path,"已完成")
    #     return
    # print(O_version_path,"未完成")

    O_version_middle_path_temp = O_path + "/" + singe_version + "/" + "middle"
    O_version_output_path_temp = O_path + "/" + singe_version + "/" + "output"
    ToolIO.checkurl(O_version_middle_path_temp)
    ToolIO.checkurl(O_version_output_path_temp)

    covMatrix, fault, in_vector, real_vector, cc_list, failN, passN = ToolIO.readFile(S_version_path, O_version_path)

    for fault_id in fault:
        StatementNum = len(covMatrix[0])
        O_version_middle_path = O_version_middle_path_temp + "/" + str(fault_id)
        O_version_output_path = O_version_output_path_temp + "/" + str(fault_id)
        ToolIO.checkurl(O_version_middle_path)
        ToolIO.checkurl(O_version_output_path)

        fileNum=os.listdir(O_version_output_path)
        if len(fileNum)==234:
            continue

        related_a = []
        unrelated_a = []
        related_a_and_b = []
        for i in cc_list:
            flag = 0
            if (covMatrix[i][fault_id] == 1):
                for j in fault:
                    if(j ==fault_id):
                        continue
                    if(covMatrix[i][j] == 1):
                        flag = 1
                        break
                if(flag==0):
                    related_a.append(i)
                else:
                    related_a_and_b.append(i)
            else:
                unrelated_a.append(i)

        #cc_pro_coverage的含义是测试用例为cc的概率，当前已知所有情况，所以fail设定为-1,pass设定为0，cc设定为1
        cc_pro_coverage_normal = []
        cc_pro_coverage_a = []
        cc_pro_coverage_una =[]
        cc_pro_coverage_a_b =[]
        cc_pro_coverage_all = []
        #原始cc_pro_coverage
        cc_pro_coverage_normal = list(in_vector)
        for i in range(len(cc_pro_coverage_normal)):
            if(cc_pro_coverage_normal[i] == 1):
                cc_pro_coverage_normal[i] = -1

        cc_pro_coverage_a = list(cc_pro_coverage_normal)
        cc_pro_coverage_una = list(cc_pro_coverage_normal)
        cc_pro_coverage_a_b = list(cc_pro_coverage_normal)
        cc_pro_coverage_all =list(cc_pro_coverage_normal)
        #处理仅和a相关的cc得到cc_pro_coverage_a
        for i in related_a:
            cc_pro_coverage_a[i] = 1

        # 处理仅和a不相关的cc得到cc_pro_coverage_una
        for i in unrelated_a:
            cc_pro_coverage_una[i] = 1

        #处理和a且和b相关的cc得到cc_pro_coverage_a_b
        for i in related_a_and_b:
            cc_pro_coverage_a_b[i] = 1

        #处理所有的cc
        for i in cc_list:
            cc_pro_coverage_all[i] = 1

        # 原始cc_pro_coverage 处理了所有的CC
        sus_oc, sus_tu, sus_op, sus_ds, sus_cr, sus_ja, sus_oc_cc, sus_tu_cc, sus_op_cc, sus_ds_cc, sus_cr_cc, sus_ja_cc = CalSus.deal(
            cc_pro_coverage_all, covMatrix, in_vector,StatementNum)
        Suspicion_coverage_normal = [sus_oc, sus_tu, sus_op, sus_ds, sus_cr, sus_ja]
        Suspicion_coverage_cc = [sus_oc_cc, sus_tu_cc, sus_op_cc, sus_ds_cc, sus_cr_cc, sus_ja_cc]

        # 仅和a相关
        sus_oc_a, sus_tu_a, sus_op_a, sus_ds_a, sus_cr_a, sus_ja_a, sus_oc_cc_a, sus_tu_cc_a, sus_op_cc_a, sus_ds_cc_a, sus_cr_cc_a, sus_ja_cc_a = CalSus.deal(
            cc_pro_coverage_a, covMatrix, in_vector,StatementNum)
        Suspicion_coverage_cc_a = [sus_oc_cc_a, sus_tu_cc_a, sus_op_cc_a, sus_ds_cc_a, sus_cr_cc_a, sus_ja_cc_a]

        #仅和a不相关的
        sus_oc_una, sus_tu_una, sus_op_una, sus_ds_una, sus_cr_una, sus_ja_una, sus_oc_cc_una, sus_tu_cc_una, sus_op_cc_una, sus_ds_cc_una, sus_cr_cc_una, sus_ja_cc_una = CalSus.deal(
            cc_pro_coverage_una, covMatrix, in_vector,StatementNum)
        Suspicion_coverage_cc_una = [sus_oc_cc_una, sus_tu_cc_una, sus_op_cc_una, sus_ds_cc_una, sus_cr_cc_una, sus_ja_cc_una]

        #和a和b均相关
        sus_oc_a_b, sus_tu_a_b, sus_op_a_b, sus_ds_a_b, sus_cr_a_b, sus_ja_a_b, sus_oc_cc_a_b, sus_tu_cc_a_b, sus_op_cc_a_b, sus_ds_cc_a_b, sus_cr_cc_a_b, sus_ja_cc_a_b = CalSus.deal(
            cc_pro_coverage_a_b, covMatrix, in_vector,StatementNum)
        Suspicion_coverage_cc_a_b = [sus_oc_cc_a_b, sus_tu_cc_a_b, sus_op_cc_a_b, sus_ds_cc_a_b, sus_cr_cc_a_b,
                                     sus_ja_cc_a_b]

        # 评估
        FormulaList = ["ochiai", "turantula", "op2", "dstar", "crosstab", "jaccard"]
        TopList = [1, 2, 3, 4, 5, 10]
        #情况1
        for index in range(len(Suspicion_coverage_normal)):
            cost, exam, fault_of_cost = ToolMetric.getEXAM(Suspicion_coverage_normal[index], fault)
            ToolIO.saveResult(O_version_output_path, "coverage_normal_v1", FormulaList[index], cost, exam, fault_of_cost,
                              )
        for index in range(len(Suspicion_coverage_cc)):
            ToolMetric.dealCCMetric(Suspicion_coverage_cc[index], "coverage_cc_v1", fault, FormulaList[index],
                                    O_version_output_path)

         #情况2
        for index in range(len(Suspicion_coverage_cc_a)):
            ToolMetric.dealCCMetric(Suspicion_coverage_cc_a[index], "coverage_cc_v1_a", fault, FormulaList[index],
                                    O_version_output_path)

        #情况3
        for index in range(len(Suspicion_coverage_cc_una)):
            ToolMetric.dealCCMetric(Suspicion_coverage_cc_una[index], "coverage_cc_v1_una", fault, FormulaList[index],
                                    O_version_output_path)

        #情况4
        for index in range(len(Suspicion_coverage_cc_a_b)):
            ToolMetric.dealCCMetric(Suspicion_coverage_cc_a_b[index], "coverage_cc_v1_a_b", fault, FormulaList[index],
                                    O_version_output_path)

def deal(root_path, fileType):
    pool = multiprocessing.Pool(processes=16)
    if fileType == 1:
        project_files = ["Time", "Mockito", "Math", "Lang", "JxPath", "Jsoup", "JacksonXml",
                         "JacksonDatabind","JacksonCore","Gson","Csv","Compress","Codec","Cli","Chart"]
        for project_file_index in range(len(project_files)):
            project_file = project_files[project_file_index]

            project_name = project_file
            project_path = root_path + "/" + project_name
            MFS_path = project_path + "/" + "MFsource"
            MFO_path = project_path + "/" + "MFoutput"

            SFS_path = project_path + "/" + "SFsource"
            SFO_path = project_path + "/" + "SFoutput"
            print("MFS_path",MFS_path,"MFO_path",MFO_path,"SFS_path",SFS_path,"SFO_path",SFO_path)
            version_files = os.listdir(MFO_path)
            for singe_version in version_files:
                dealSingleVersion(root_path, project_path, project_file, MFS_path, MFO_path, singe_version)
                # pool.apply_async(dealSingleVersion,(root_path, project_path, project_file, MFS_path, MFO_path, singe_version,))
            # version_files = os.listdir(SFO_path)
            # for singe_version in version_files:
            #     dealSingleVersion(root_path, project_path, project_file, SFS_path, SFO_path, singe_version)
                # pool.apply_async(dealSingleVersion,(root_path, project_path, project_file, SFS_path, SFO_path, singe_version,))
    pool.close()
    pool.join()


if __name__ == "__main__":
    root_path = sys.path[0] + "/"
    root_path = r"/home/wwb/D4J/djtoSir_statement"
    deal(root_path,1)
    # root_path = r"D:\defect"
    # deal(root_path, 2)
