package com.kingdee.plugin.pur;

import kd.bos.bill.AbstractBillPlugIn;
import kd.bos.dataentity.entity.DynamicObject;
import kd.bos.dataentity.entity.DynamicObjectCollection;
import kd.bos.dataentity.utils.StringUtils;
import kd.bos.entity.validate.ValidateContext;
import kd.bos.entity.validate.ValidationErrorInfo;
import kd.bos.form.events.BeforeDoOperationEventArgs;
import kd.bos.orm.util.Decimal;

import java.math.BigDecimal;

/**
 * 采购订单校验插件（苍穹风格）
 *
 * 校验规则：
 * 1. 单据体采购金额（amount）合计不能超过 10000 元
 * 2. 单据体采购数量（qty）合计不能超过 100
 *
 * 说明：
 * - 建议在“保存”“提交”操作上绑定该插件。
 * - 字段标识默认使用 amount、qty、billentry，若与实际模型不一致请调整常量。
 */
public class PurchaseOrderValidatePlugin extends AbstractBillPlugIn {

    /** 单据体标识 */
    private static final String ENTRY_KEY = "billentry";
    /** 采购金额字段标识 */
    private static final String AMOUNT_KEY = "amount";
    /** 采购数量字段标识 */
    private static final String QTY_KEY = "qty";

    /** 金额上限：10000 */
    private static final BigDecimal MAX_AMOUNT = new BigDecimal("10000");
    /** 数量上限：100 */
    private static final BigDecimal MAX_QTY = new BigDecimal("100");

    @Override
    public void beforeDoOperation(BeforeDoOperationEventArgs e) {
        super.beforeDoOperation(e);

        String operation = e.getOperateKey();
        if (!StringUtils.equalsIgnoreCase(operation, "save")
                && !StringUtils.equalsIgnoreCase(operation, "submit")) {
            return;
        }

        DynamicObject bill = this.getModel().getDataEntity(true);
        DynamicObjectCollection entries = bill.getDynamicObjectCollection(ENTRY_KEY);

        BigDecimal totalAmount = BigDecimal.ZERO;
        BigDecimal totalQty = BigDecimal.ZERO;

        if (entries != null) {
            for (DynamicObject row : entries) {
                BigDecimal amount = toBigDecimal(row.get(AMOUNT_KEY));
                BigDecimal qty = toBigDecimal(row.get(QTY_KEY));

                totalAmount = totalAmount.add(amount);
                totalQty = totalQty.add(qty);
            }
        }

        ValidateContext validateContext = new ValidateContext();

        if (totalAmount.compareTo(MAX_AMOUNT) > 0) {
            String msg = String.format("采购金额校验失败：当前合计金额为 %s，不能超过 %s 元。", totalAmount, MAX_AMOUNT);
            addError(validateContext, msg, AMOUNT_KEY);
        }

        if (totalQty.compareTo(MAX_QTY) > 0) {
            String msg = String.format("采购数量校验失败：当前合计数量为 %s，不能超过 %s。", totalQty, MAX_QTY);
            addError(validateContext, msg, QTY_KEY);
        }

        if (validateContext.getErrorInfos().size() > 0) {
            this.getView().showErrorNotification(validateContext.getErrorInfos().get(0).getMessage());
            e.setCancel(true);
        }
    }

    private static void addError(ValidateContext context, String msg, String fieldKey) {
        ValidationErrorInfo errorInfo = new ValidationErrorInfo(
                "PUR_ORDER_VALIDATE",
                "",
                0,
                fieldKey,
                msg,
                msg
        );
        context.addError(errorInfo);
    }

    private static BigDecimal toBigDecimal(Object value) {
        if (value == null) {
            return BigDecimal.ZERO;
        }

        if (value instanceof BigDecimal) {
            return (BigDecimal) value;
        }

        if (value instanceof Decimal) {
            return ((Decimal) value).toBigDecimal();
        }

        try {
            return new BigDecimal(String.valueOf(value));
        } catch (Exception ex) {
            return BigDecimal.ZERO;
        }
    }
}
