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

    O_version_middle_path_temp = O_path + "/" + singe_version + "/" + "middle_ideaIsolation"
    O_version_output_path_temp = O_path + "/" + singe_version + "/" + "output_ideaIsolation"
    ToolIO.checkurl(O_version_middle_path_temp)
    ToolIO.checkurl(O_version_output_path_temp)
    covMatrix_temp, fault_temp, in_vector_temp, real_vector_temp, cc_list_temp, failN_temp, passN_temp = ToolIO.readFile(S_version_path, O_version_path)
    for fault_id in fault_temp:

        StatementNum = len(covMatrix_temp[0])
        # 得到仅和a相关的错误
        Related_a = []
        for test_id in range(len(covMatrix_temp)):
            if(covMatrix_temp[test_id][fault_id] == 1 and in_vector_temp[test_id] == 1):
                Related_a.append(test_id)
        #计算下通过测试用例的个数，方便验证代码是否正确
        pass_num = 0
        for pass_id in in_vector_temp:
            if(pass_id == 0):
                pass_num = pass_num + 1
        #算covMatrix和in_vector
        covMatrix = []
        in_vector = []
        for i in range(len(in_vector_temp)):
            if((i in Related_a) or in_vector_temp[i] == 0):
                covMatrix.append(covMatrix_temp[i])
                in_vector.append(in_vector_temp[i])
        #算real_vector
        real_vector = []
        for t in range(len(in_vector)):
            isPass = True
            for fs in fault_temp:
                if covMatrix[t][fs] == 1:
                    isPass = False
                    break
            if isPass:
                real_vector.append(0)
            else:
                real_vector.append(1)

        #算failN
        failN = len(Related_a)

        #算passN_temp
        passN = passN_temp


        O_version_middle_path = O_version_middle_path_temp + "/" + str(fault_id)
        O_version_output_path = O_version_output_path_temp + "/" + str(fault_id)
        ToolIO.checkurl(O_version_middle_path)
        ToolIO.checkurl(O_version_output_path)

        fileNum = os.listdir(O_version_output_path)

        if len(fileNum)==72:
            continue
        cc_pro_coverage = CChandle.getCCP(covMatrix, in_vector, O_version_middle_path, "distance_for_normal_cc_v1")
        ToolIO.checkAndSave(O_version_middle_path, "cc_pro_knn_coverage_v1", cc_pro_coverage)
        #处理CC
        sus_oc, sus_tu, sus_op, sus_ds, sus_cr, sus_ja, sus_oc_cc, sus_tu_cc, sus_op_cc, sus_ds_cc, sus_cr_cc, sus_ja_cc = CalSus.deal(
            cc_pro_coverage, covMatrix, in_vector,StatementNum)
        Suspicion_coverage_normal = [sus_oc, sus_tu, sus_op, sus_ds, sus_cr, sus_ja]
        Suspicion_coverage_cc = [sus_oc_cc, sus_tu_cc, sus_op_cc, sus_ds_cc, sus_cr_cc, sus_ja_cc]
        # 评估
        FormulaList = ["ochiai", "turantula", "op2", "dstar", "crosstab", "jaccard"]
        TopList = [1, 2, 3, 4, 5, 10]

        for index in range(len(Suspicion_coverage_normal)):
            cost, exam, fault_of_cost = ToolMetric.getEXAM(Suspicion_coverage_normal[index], fault_temp)
            ToolIO.saveResult(O_version_output_path, "coverage_normal_v1", FormulaList[index], cost, exam, fault_of_cost,)
        for index in range(len(Suspicion_coverage_cc)):
            ToolMetric.dealCCMetric(Suspicion_coverage_cc[index], "coverage_cc_v1", fault_temp, FormulaList[index],
                                    O_version_output_path)


def deal(root_path, fileType):
    #pool = multiprocessing.Pool(processes=16)
    if fileType == 1:
        project_files = ["sed", "grep", "totinfo", "tcas", "schedule", "schedule2", "printtokens2", "printtokens","replace"]
        # project_files = ["sed"]
        for project_file_index in range(len(project_files)):
            project_file = project_files[project_file_index]

            project_name = project_file
            project_path = root_path + "/" + project_name
            MFS_path = project_path + "/" + "MFsource"
            MFO_path = project_path + "/" + "MFoutput"

            # SFS_path = project_path + "/" + "SFsource"
            # SFO_path = project_path + "/" + "SFoutput"
            # print("MFS_path",MFS_path,"MFO_path",MFO_path,"SFS_path",SFS_path,"SFO_path",SFO_path)
            version_files = os.listdir(MFO_path)
            for singe_version in version_files:
                dealSingleVersion(root_path, project_path, project_file, MFS_path, MFO_path, singe_version)
                #pool.apply_async(dealSingleVersion,(root_path, project_path, project_file, MFS_path, MFO_path, singe_version,))
            # version_files = os.listdir(SFS_path)
            # for singe_version in version_files:
            #     dealSingleVersion(root_path, project_path, project_file, SFS_path, SFO_path, singe_version)
                # pool.apply_async(dealSingleVersion,(root_path, project_path, project_file, SFS_path, SFO_path, singe_version,))
    #pool.close()
    #pool.join()


if __name__ == "__main__":
    root_path = sys.path[0] + "/"
    root_path = r"/home/wwb/sirCCex"
    deal(root_path,1)
    # root_path = r"D:\defect"
    # deal(root_path, 2)
