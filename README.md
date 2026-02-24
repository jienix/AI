# 双色球历史数据抓取与示例预测

## 功能
- 抓取中国福利彩票官网双色球历史开奖数据。
- 导出历史记录到 CSV。
- 基于历史频率进行一个**示例性**下一期号码预测。

> 注意：彩票号码本质是随机事件，历史统计不能可靠预测未来结果，本项目仅用于技术学习。

## 运行
```bash
python3 lottery_ssq_predict.py --output data/ssq_history.csv --seed 42
```

## 输出示例
- 历史数据：`data/ssq_history.csv`
- 终端会打印一组示例预测号码。
