/**
 * Stock quantity helpers: decimals only for Kg, Mtr, Lit (and Ltr variants).
 * Nos and all other units use whole numbers only.
 */
(function (global) {
    'use strict';

    var DECIMAL_UNITS = { kg: true, mtr: true, lit: true, ltr: true };

    function normalizeUnit(unit) {
        return String(unit || '').trim().toLowerCase().replace(/\./g, '');
    }

    function isDecimalQuantityUnit(unit) {
        return !!DECIMAL_UNITS[normalizeUnit(unit)];
    }

    function parseQtyValue(raw) {
        var s = String(raw == null ? '' : raw).trim();
        if (!s) {
            return NaN;
        }
        if (/^-?\d+(\.\d+)?$/.test(s)) {
            return parseFloat(s);
        }
        return parseFloat(s.replace(/[^\d.-]/g, ''));
    }

    function roundQty(value, unit) {
        var num = parseQtyValue(value);
        if (isNaN(num)) {
            return 0;
        }
        if (unit && !isDecimalQuantityUnit(unit)) {
            return Math.round(num);
        }
        return Math.round(num * 1000) / 1000;
    }

    function formatQtyDisplay(value, unit) {
        var qty = unit ? roundQty(value, unit) : roundQty(value);
        if (!Number.isFinite(qty) || Math.abs(qty) < 0.0000001) {
            return '0';
        }
        if (unit && !isDecimalQuantityUnit(unit)) {
            return String(Math.round(qty));
        }
        return String(parseFloat(qty.toFixed(3)));
    }

    function sanitizeQuantityInputValue(rawValue, unit) {
        var inputVal = String(rawValue == null ? '' : rawValue);

        if (isDecimalQuantityUnit(unit)) {
            var decVal = inputVal.replace(/[^0-9.]/g, '');
            var parts = decVal.split('.');
            var cleanVal = parts.length > 2
                ? parts[0] + '.' + parts.slice(1).join('')
                : decVal;
            if (cleanVal.includes('.')) {
                var pieces = cleanVal.split('.');
                return pieces[0] + '.' + pieces[1].slice(0, 3);
            }
            return cleanVal;
        }

        if (!/^\d*$/.test(inputVal)) {
            return inputVal.split('.')[0].replace(/\D/g, '');
        }
        return inputVal;
    }

    function enforceQuantityInputByUnit(inputEl, unit, options) {
        options = options || {};
        if (!inputEl) {
            return '';
        }
        var before = inputEl.value;
        var cleaned = sanitizeQuantityInputValue(before, unit);
        if (before !== cleaned) {
            if (options.showAlert !== false) {
                var unitNorm = normalizeUnit(unit);
                if (unitNorm === 'nos') {
                    alert(options.nosMessage || 'Please use whole numbers only for the "Nos" unit.');
                } else if (!isDecimalQuantityUnit(unit)) {
                    alert(options.decimalOnlyMessage || 'Decimal quantities are only allowed for Kg, Mtr, and Lit units.');
                }
            }
            inputEl.value = cleaned;
        }
        if (typeof options.onChange === 'function') {
            options.onChange(inputEl, unit);
        }
        return cleaned;
    }

    function getRowPurchaseUnit(row) {
        if (!row) {
            return '';
        }
        if (row instanceof Element) {
            var stockInput = row.querySelector('.stock-quantity');
            if (stockInput && stockInput.dataset.purchaseUnit) {
                return String(stockInput.dataset.purchaseUnit).trim();
            }
            var qtyInput = row.querySelector('.quantity-input, input[name^="quantity"], .quantity');
            if (qtyInput && qtyInput.dataset.purchaseUnit) {
                return String(qtyInput.dataset.purchaseUnit).trim();
            }
            var purchaseEl = row.querySelector('.stock-purchase');
            if (purchaseEl) {
                var purchaseText = purchaseEl.textContent || purchaseEl.value || '';
                if (String(purchaseText).trim()) {
                    return String(purchaseText).trim();
                }
            }
            var groupUnit = row.querySelector('.input-group-text');
            if (groupUnit && groupUnit.textContent) {
                return String(groupUnit.textContent).trim();
            }
            var badgeUnit = row.querySelector('.badge small');
            if (badgeUnit && badgeUnit.textContent) {
                return String(badgeUnit.textContent).trim();
            }
        }
        var $row = row instanceof Element && global.jQuery ? global.jQuery(row) : row;
        if ($row && $row.find) {
            var fromStockData = $row.find('.stock-quantity').data('purchase-unit');
            if (fromStockData) {
                return String(fromStockData).trim();
            }
            var fromQtyData = $row.find('.quantity-input, input[name^="quantity"], .quantity').data('purchase-unit');
            if (fromQtyData) {
                return String(fromQtyData).trim();
            }
            var fromHidden = $row.find('.stock-purchase').first().text() || $row.find('.stock-purchase').first().val();
            if (fromHidden) {
                return String(fromHidden).trim();
            }
            var fromAppend = $row.find('.input-group-text').first().text();
            if (fromAppend) {
                return String(fromAppend).trim();
            }
        }
        return '';
    }

    /**
     * Update available-quantity badge for new sale and edit sale rows.
     * Default: shows warehouse stock from database.
     * With recalculateRemaining: shows remaining after entered qty
     *   (new sale: warehouse - entered; edit sale: warehouse + saved - entered).
     */
    function updateSaleRemainingBadge(row, options) {
        options = options || {};
        if (!row) {
            return;
        }

        var rowEl = row instanceof Element ? row : (row[0] || row);
        if (!rowEl) {
            return;
        }

        var stockInput = rowEl.querySelector('.stock-quantity');
        var quantityInput = rowEl.querySelector('.quantity-input, input[name^="quantity"], .quantity');
        var badge = rowEl.querySelector('.badge');
        if (!stockInput || !quantityInput || !badge) {
            return;
        }

        var unit = stockInput.dataset.purchaseUnit
            || quantityInput.dataset.purchaseUnit
            || getRowPurchaseUnit(rowEl);
        var warehouseQty = roundQty(
            stockInput.dataset.warehouseQty || stockInput.value || '0',
            unit
        );
        stockInput.dataset.warehouseQty = String(warehouseQty);

        var savedSaleQty = 0;
        if (options.editMode) {
            savedSaleQty = roundQty(
                quantityInput.dataset.savedQty || quantityInput.defaultValue || '0',
                unit
            );
        }

        var originalTotal = roundQty(warehouseQty + savedSaleQty, unit);
        stockInput.dataset.originalQty = originalTotal;

        var entered = roundQty(quantityInput.value || '0', unit);
        var remaining = roundQty(Math.max(0, originalTotal - entered), unit);
        var displayQty = options.recalculateRemaining ? remaining : warehouseQty;
        var formatted = formatQtyDisplay(displayQty, unit);
        var qtyText = badge.querySelector('.available-qty-text');
        if (qtyText) {
            qtyText.textContent = formatted;
        } else {
            var unitEl = badge.querySelector('small');
            var unitHtml = unitEl ? unitEl.outerHTML : '';
            badge.innerHTML = '<span class="available-qty-text">' + formatted + '</span> ' + unitHtml;
        }

        var stockAlert = roundQty(stockInput.dataset.stockAlert || '0');
        badge.classList.remove('success', 'danger');
        badge.classList.add(displayQty > stockAlert ? 'success' : 'danger');
    }

    global.isDecimalQuantityUnit = isDecimalQuantityUnit;
    global.normalizePurchaseUnit = normalizeUnit;
    global.roundQty = function (value, unit) {
        if (arguments.length > 1) {
            return roundQty(value, unit);
        }
        return roundQty(value);
    };
    global.formatQtyDisplay = formatQtyDisplay;
    global.sanitizeQuantityInputValue = sanitizeQuantityInputValue;
    global.enforceQuantityInputByUnit = enforceQuantityInputByUnit;
    global.getRowPurchaseUnit = getRowPurchaseUnit;
    global.updateSaleRemainingBadge = updateSaleRemainingBadge;
    global.parseQtyValue = parseQtyValue;
})(window);
