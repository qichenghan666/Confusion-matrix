from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.utils.multiclass import unique_labels
from sklearn.preprocessing import label_binarize
from scipy import interp
from itertools import cycle
import pandas as pd


def load_csv_file(path):
    """
    :param path: csv file path
    the file must be fomated by
    first row  : predict  data
    second row : label    data
    """
    result = pd.read_csv(path, header=None, sep=',')
    result = result.values[:,:-1]
    pred_idx = result[0]
    truth_idx = result[1]
    return pred_idx, truth_idx

class ConfusionMatrix(object):

    def __init__(self, y_true, y_pred, decimal=4):
        '''
        :param y_true:
        :param y_pred:
        :param decimal: nums of decimal 
        for example:
        y_true = ['2', '0', '0', '1', '2', '0']
        y_pred = ['2', '0', '0', '1', '2', '1']  
        
        y_true = ['cat', 'dog', 'cat']
        y_pred = ['cat', 'dog', 'dog']
        '''
        self.decimal = decimal # 结果保留小数点后几位
        self.y_true = y_true
        self.y_pred = y_pred
        self.labels = unique_labels(self.y_true, self.y_pred) # 得到labels
        self.n = len(self.labels) # labels数量        
        self.c = np.array(confusion_matrix(y_true, y_pred, labels=self.labels), np.float32) # 计算混淆矩阵
    
    #==========================================================================================#
    #                               一级指标：混淆矩阵                                          #
    #==========================================================================================#
        
    def plot_confusion_matrix(self):
        """
        plot confusion matrix
        :return:
        """
        f, ax = plt.subplots(figsize = (6,4),nrows=1) 
        sns.heatmap(self.c, annot=True, cmap="Blues", linewidths = 0.01)#.invert_yaxis()# 反轴显示
        ax.set_title('Confusion Matrix')
        ax.set_xlabel('y_pred')
        ax.set_ylabel('y_true')
        
    def level_1(self):
        """
        print confusion matrix
        """
        print(self.c)
    #==========================================================================================#
    #   二级指标：准确率（Accuracy）, 精确率（Precision），召回率（Recall）, 特异度（Specificity）#
    #==========================================================================================#
    def accuracy(self):
        """
        accuracy = (TP + TN) / (TP + TN + FP + FN)
        :return:
        """
        print('Accuracy: ', round(accuracy_score(self.y_true, self.y_pred), self.decimal))

    def _bi_matrix(self, i):
        bi_arr = np.zeros((2, 2), np.float32)
        bi_arr[0, 0] = self.c[i, i]
        bi_arr[0, 1] = np.sum(self.c[i, :]) - self.c[i, i]
        bi_arr[1, 0] = np.sum(self.c[:, i]) - self.c[i, i]
        bi_arr[1, 1] = np.sum(self.c[:, :]) - bi_arr[0, 0] - bi_arr[0, 1] -bi_arr[1, 0] 
        return bi_arr
            
    def recall(self, config=True):
        """
        recall = TP / (TP + FN)
        :param config: print infomation or not
        :return:
        """
        Recall = {}
        for i in range(self.n):
            bi_arr = self._bi_matrix(i)
            tp = bi_arr[0, 0]
            fn = bi_arr[0, 1]
            if tp == 0:
                Recall[self.labels[i]] = 0
                if config == True:
                    print("class:", self.labels[i], "    Recall:", 0)
            else:
                Recall[self.labels[i]] = round(tp / (tp + fn), self.decimal)
                if config == True:
                    print("class:", self.labels[i], "    Recall:", round(tp / (tp + fn), self.decimal))
        return Recall

    def precision(self, config=True):
        """
        precision = TP / (TP + FP)
        :param config:
        :return:
        """

        Precision = {}
        for i in range(self.n):        
            bi_arr = self._bi_matrix(i)
            tp = bi_arr[0, 0]
            fp = bi_arr[1, 0]
            if tp == 0:
                Precision[self.labels[i]] = 0
                if config == True:
                    print("class:", self.labels[i], "    Precision:", 0)
            else:
                Precision[self.labels[i]] = round(tp / (tp + fp), self.decimal)
                if config == True:
                    print("class:", self.labels[i], "    Precision:", round(tp / (tp + fp), self.decimal))
        return Precision
    
    def specificity(self, config=True):
        """
        specificity = TN / (TN + FP)
        :param config:
        :return:
        """
        Specificity = {}
        for i in range(self.n):        
            bi_arr = self._bi_matrix(i)
            tn = bi_arr[1, 1]
            fp = bi_arr[1, 0]
            Specificity[self.labels[i]] = round(tn / (tn + fp), self.decimal)
            if config == True:
                print("class:", self.labels[i], "    Specificity:", round(tn / (tn + fp), self.decimal))   
        return Specificity    
    
    def level_2(self):
        '''
        accuracy、Precision、Recall、Specificity
        '''
        self.accuracy()
        for i in range(self.n):
            bi_arr = self._bi_matrix(i)
            tn = bi_arr[1, 1]
            fp = bi_arr[1, 0]
            tp = bi_arr[0, 0]
            fn = bi_arr[0, 1] 
            if tp != 0:
                print("class:", self.labels[i],
                      "      Recall:",  round(tp / (tp + fp), self.decimal),
                      "      Precision:",  round(tp / (tp + fn), self.decimal),
                      "      Specificity:", round(tn / (tn + fp), self.decimal))
            else:
                print("class:", self.labels[i],
                  "      Recall:",  0,
                  "      Precision:",  0,
                  "      Specificity:", round(tn / (tn + fp), self.decimal))               

    #==========================================================================================#
    #                               三级指标：F1 Score                                          #
    #==========================================================================================#
    def F1_score(self):
        """
        F1 score = 2PR / (P + R)
        :return:
        """

        for i in range(self.n): 
            p = self.precision(config=False)[self.labels[i]]
            r = self.recall(config=False)[self.labels[i]]
            if p == 0 or r == 0:
                F1_score = 0
            else:
                F1_score = 2. * p * r / (p + r)
            print("class:", self.labels[i], "    F1_score:", round(F1_score, self.decimal))  
    

    #==========================================================================================#
    #                               ROC & AUC                                                  #
    #==========================================================================================#
    def _binarize(self, y):
        return label_binarize(y, classes=self.labels)

    
    def roc_auc(self):
        y_true = self._binarize(self.y_true)
        y_pred = self._binarize(self.y_pred)
        
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(self.n):
            fpr[i], tpr[i], _ = roc_curve(y_true[:, i], y_pred[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # First aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(self.n)]))
        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(self.n):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])
        # Finally average it and compute AUC
        mean_tpr /= self.n
        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
        
        # Plot all ROC curves
        lw=2 # 线宽
        plt.figure()
        
        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)
        
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(range(self.n), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                     ''.format(i, roc_auc[i]))
        
        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        plt.show()


if __name__ == "__main__":

    
    y_true = ['2', '0', '0', '1', '2', '0']
    y_pred = ['2', '0', '0', '1', '2', '1'] 
#    y_pred, y_true = load_csv_file('./results-all.csv')
    c = ConfusionMatrix(y_true, y_pred)
    c.level_2()


