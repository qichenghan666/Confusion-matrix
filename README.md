# Confusion-matrix
Confusion matrix correlation

Confusion matrix 类的调用：

    c = ConfusionMatrix(y_true, y_pred)
    c.plot_confusion_matrix() # 混淆矩阵热力图可视化
    c.level_1() # 打印混淆矩阵
    c.accuary() # 准确率
    c.precision(config=True) # 精确率, config 配置是否打印输出
    c.recall(config=True) # 召回率
    c.specificity(config=True)# 特异度
    c.level_2() # 同时输出准确率，精确率，召回率，特异度
    c.F1_score() # F1 score
    c.roc_auc() # 绘制roc曲线
