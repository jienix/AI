# 金蝶云苍穹采购订单校验插件示例

本仓库新增了一个**采购订单校验插件**，用于在保存/提交采购订单时校验：

- 采购金额合计不能超过 **10000 元**；
- 采购数量合计不能超过 **100**。

## 插件文件

- `src/main/java/com/kingdee/plugin/pur/PurchaseOrderValidatePlugin.java`

## 规则说明

插件在 `beforeDoOperation` 中拦截 `save`、`submit` 操作：

1. 遍历单据体（默认 `billentry`）
2. 累加金额字段（默认 `amount`）
3. 累加数量字段（默认 `qty`）
4. 若金额 > 10000 或数量 > 100，则取消操作并提示错误

> 如你的业务对象字段标识不同，请修改类中的 `ENTRY_KEY`、`AMOUNT_KEY`、`QTY_KEY` 常量。
