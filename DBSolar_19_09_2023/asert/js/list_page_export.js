/**
 * Shared PDF (HERAMB letterhead + jsPDF autoTable), Excel, Copy, Print for DataTables list pages.
 * Configure via ListPageExport.register({ ... }) after setting window.LIST_PAGE_EXPORT_LOGO_PATH from Django {% static %}.
 */
(function (global) {
    'use strict';

    function getLogoPath() {
        return global.LIST_PAGE_EXPORT_LOGO_PATH || '/static/images/db_logo_200.png';
    }

    function listPdfLogoAbsoluteUrl() {
        var p = getLogoPath();
        if (/^https?:\/\//i.test(p)) {
            return p;
        }
        if (typeof global.location === 'undefined' || !global.location || !global.location.origin) {
            return p;
        }
        return global.location.origin + (p.charAt(0) === '/' ? p : '/' + p);
    }

    function loadPdfHeaderImageDataUrl(url, callback) {
        function viaFetch() {
            if (typeof fetch === 'undefined') {
                callback(null);
                return;
            }
            fetch(url, { credentials: 'same-origin' })
                .then(function (r) {
                    if (!r.ok) {
                        throw new Error('fetch');
                    }
                    return r.blob();
                })
                .then(function (blob) {
                    var fr = new FileReader();
                    fr.onload = function () {
                        callback(fr.result);
                    };
                    fr.onerror = function () {
                        callback(null);
                    };
                    fr.readAsDataURL(blob);
                })
                .catch(function () {
                    callback(null);
                });
        }
        var img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function () {
            try {
                var canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                canvas.getContext('2d').drawImage(img, 0, 0);
                callback(canvas.toDataURL('image/png'));
            } catch (e) {
                viaFetch();
            }
        };
        img.onerror = function () {
            viaFetch();
        };
        img.src = url;
    }

    /* Matches transactions/templates/bill/purchase_bill.html header row (logo + centered company block). */
    function listPdfPrintLetterheadInnerHtml() {
        var logoSrc = listPdfLogoAbsoluteUrl();
        return '<div style="width:100%;box-sizing:border-box;color:#575757;font-family:Arial,Helvetica,sans-serif;">' +
            '<div style="display:flex;align-items:flex-end;justify-content:center;text-align:center;gap:6px;">' +
            '<div style="flex:0 0 auto;">' +
            '<img src="' + logoSrc + '" alt="" style="width:150px;max-width:40vw;height:auto;display:block;margin:0;padding:0;object-fit:contain;-webkit-print-color-adjust:exact;print-color-adjust:exact;" />' +
            '</div>' +
            '<div style="margin:0;padding:0;text-align:center;line-height:1.2;max-width:520px;">' +
            '<span style="font-size:300%;font-weight:bold;display:inline-block;">HERAMB INDUSTRIES</span><br>' +
            '<span style="font-size:120%;font-weight:bold;">Sales - On-Grid / Off-Grid Solar</span><br>' +
            '<span style="font-size:90%;line-height:1.5;display:inline-block;margin-top:0.2em;">' +
            '<span style="font-weight:bold;">REGD ADDRESS :</span> Bhagya Bangla, Block No. 2, Opp - Sant Eknamth Mandir,<br>' +
            'New Osmanpura, Chh.Sambhaji Nagar. Maharashtra, 431001<br>' +
            '<span><b>EMAIL :</b> &nbsp;herambasd1@gmail.com , &nbsp; <b>GSTIN/UIN :</b>&nbsp;  27AIPPD9639R1Z6</span><br><br>' +
            '</span>' +
            '</div></div>' +
            '<hr style="border:none;border-top:1px solid #999;margin:10px 0 8px 0;padding:0;width:100%;max-width:100%;" />' +
            '</div>';
    }

    function listPdfAddLogoImage(doc, logoDataUrl, x, y, w, h) {
        if (!logoDataUrl || w <= 0 || h <= 0) {
            return;
        }
        var fmt = 'PNG';
        if (/data:image\/jpe?g/i.test(logoDataUrl)) {
            fmt = 'JPEG';
        }
        try {
            doc.addImage(logoDataUrl, fmt, x, y, w, h);
        } catch (e1) {
            try {
                doc.addImage(logoDataUrl, fmt === 'PNG' ? 'JPEG' : 'PNG', x, y, w, h);
            } catch (e2) { /* ignore */ }
        }
    }

    function listPdfGetLetterheadGeom(pdf, logoDataUrl, sideM, yStart) {
        var pageW = pdf.internal.pageSize.getWidth();
        var contentW = pageW - 2 * sideM;
        /* ~150px logo width on purchase bill → ~40 mm on A4 */
        var logoColMaxW = Math.min(42, contentW * 0.28);
        var logoMaxH = 32;
        var logoToTextGap = -20;
        var logoY = yStart;
        var logoWUsed = 0;
        var logoHmm = 0;
        if (logoDataUrl && typeof pdf.getImageProperties === 'function') {
            var ip = pdf.getImageProperties(logoDataUrl);
            logoHmm = (ip.height / ip.width) * logoColMaxW;
            if (logoHmm > logoMaxH) {
                logoHmm = logoMaxH;
                logoWUsed = (ip.width / ip.height) * logoHmm;
            } else {
                logoWUsed = logoColMaxW;
                logoHmm = (ip.height / ip.width) * logoWUsed;
            }
        }
        var textW = logoWUsed > 0
            ? Math.min(175, Math.max(78, contentW - logoWUsed - logoToTextGap))
            : Math.min(175, contentW);
        var groupW = (logoWUsed > 0 ? logoWUsed + logoToTextGap : 0) + textW;
        if (groupW > contentW) {
            textW = Math.max(78, contentW - (logoWUsed > 0 ? logoWUsed + logoToTextGap : 0));
            groupW = (logoWUsed > 0 ? logoWUsed + logoToTextGap : 0) + textW;
        }
        var startX = sideM + (contentW - groupW) / 2;
        var logoX = startX;
        var textX = logoWUsed > 0 ? startX + logoWUsed + logoToTextGap : startX;
        var textCenterX = textX + textW / 2;
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(9);
        var addr1 = 'REGD ADDRESS : Bhagya Bangla, Block No. 2, Opp - Sant Eknamth Mandir,';
        var addr2 = 'New Osmanpura, Chh.Sambhaji Nagar. Maharashtra, 431001';
        var addrLines1 = pdf.splitTextToSize(addr1, textW);
        var addrLines2 = pdf.splitTextToSize(addr2, textW);
        pdf.setFontSize(8);
        var emLine = 'EMAIL : herambasd1@gmail.com , GSTIN/UIN : 27AIPPD9639R1Z6';
        var emLines = pdf.splitTextToSize(emLine, textW);
        var lineH9 = 3.5;
        var lineH8 = 3.35;
        var nAddr = addrLines1.length + addrLines2.length;
        var ne = emLines.length;
        var tySpan = 6.8 + 5.2 + nAddr * lineH9 + ne * lineH8;
        var lastStep = ne > 0 ? lineH8 : (nAddr > 0 ? lineH9 : 5.2);
        var offsetFirstToLastBaseline = tySpan - lastStep;
        var descenderPad = 2;
        var logoBottom = logoWUsed > 0 ? logoY + logoHmm : logoY;
        var firstBaselineY;
        var bottom;
        if (logoWUsed > 0 && logoHmm > 0) {
            firstBaselineY = logoBottom - descenderPad - offsetFirstToLastBaseline;
            bottom = logoBottom + 3;
        } else {
            firstBaselineY = logoY + 5.5;
            bottom = firstBaselineY + tySpan + 3;
        }
        var contentBottom = bottom;
        var ruleTopGap = 2;
        var ruleBelowGap = 2.4;
        var ruleLineY = contentBottom + ruleTopGap;
        bottom = ruleLineY + ruleBelowGap;
        return {
            logoX: logoX,
            logoY: logoY,
            logoWUsed: logoWUsed,
            logoHmm: logoHmm,
            textX: textX,
            textW: textW,
            textCenterX: textCenterX,
            textTopY: firstBaselineY,
            addrLines1: addrLines1,
            addrLines2: addrLines2,
            emLines: emLines,
            ruleLineY: ruleLineY,
            bottom: bottom
        };
    }

    function listPdfLetterheadBottomMm(pdf, logoDataUrl, sideM, yStart) {
        return listPdfGetLetterheadGeom(pdf, logoDataUrl, sideM, yStart).bottom;
    }

    function listPdfResolveCaption(cfg) {
        if (cfg && cfg.pdfCaption != null && String(cfg.pdfCaption).trim() !== '') {
            return String(cfg.pdfCaption).trim();
        }
        if (cfg && cfg.printDocumentTitle) {
            return String(cfg.printDocumentTitle).trim();
        }
        return '';
    }

    function listPdfMeasureCaptionBlock(pdf, captionText, sideM) {
        var out = { lines: [], lineH: 4.15, extraBelowLetterheadMm: 0 };
        if (!captionText) {
            return out;
        }
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(11);
        var cw = pdf.internal.pageSize.getWidth() - 2 * sideM;
        out.lines = pdf.splitTextToSize(String(captionText).trim(), cw);
        out.extraBelowLetterheadMm = 4 + out.lines.length * out.lineH + 2;
        return out;
    }

    function listPdfDrawCaptionAfterLetterhead(doc, capBlock, sideM, hb, pageNum) {
        if (!capBlock || !capBlock.lines || !capBlock.lines.length) {
            return;
        }
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        var pageW = doc.internal.pageSize.getWidth();
        var cx = pageW / 2;
        var y = hb + 4;
        var i;
        for (i = 0; i < capBlock.lines.length; i++) {
            doc.text(capBlock.lines[i], cx, y, { align: 'center' });
            y += capBlock.lineH;
        }
    }

    function drawListPdfLetterhead(doc, logoDataUrl, sideM, yStart) {
        var g = listPdfGetLetterheadGeom(doc, logoDataUrl, sideM, yStart);
        listPdfAddLogoImage(doc, logoDataUrl, g.logoX, g.logoY, g.logoWUsed, g.logoHmm);
        var cx = g.textCenterX;
        var ty = g.textTopY;
        doc.setTextColor(87, 87, 87);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(18);
        doc.text('HERAMB INDUSTRIES', cx, ty, { align: 'center' });
        ty += 6.8;
        doc.setFontSize(11);
        doc.text('Sales - On-Grid / Off-Grid Solar', cx, ty, { align: 'center' });
        ty += 5.2;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        var li;
        for (li = 0; li < g.addrLines1.length; li++) {
            doc.text(g.addrLines1[li], cx, ty, { align: 'center' });
            ty += 3.5;
        }
        for (li = 0; li < g.addrLines2.length; li++) {
            doc.text(g.addrLines2[li], cx, ty, { align: 'center' });
            ty += 3.5;
        }
        doc.setFontSize(8);
        for (li = 0; li < g.emLines.length; li++) {
            doc.text(g.emLines[li], cx, ty, { align: 'center' });
            ty += 3.35;
        }
        doc.setTextColor(0, 0, 0);
        if (typeof g.ruleLineY === 'number') {
            var pageW = doc.internal.pageSize.getWidth();
            doc.setDrawColor(150, 150, 150);
            doc.setLineWidth(0.25);
            doc.line(sideM, g.ruleLineY, pageW - sideM, g.ruleLineY);
            doc.setDrawColor(0, 0, 0);
        }
    }

    function stripHtml(html) {
        try {
            var doc = new DOMParser().parseFromString(String(html || ''), 'text/html');
            return doc.body.textContent || '';
        } catch (e) {
            return String(html || '');
        }
    }

    function defaultExcludeHeader(label) {
        var t = (label || '').trim();
        return t === 'Action' || t === 'Actions';
    }

    function defaultIsSrHeader(label) {
        var h = (label || '').trim();
        return h === 'Sr No' || h === 'Sr No.' || h === 'Sr.No.';
    }

    function buildExportApi(table, cfg) {
        function headerText(tableObj, colIndex) {
            var node = tableObj.column(colIndex).header();
            return (node ? (node.innerText || '') : '').trim();
        }
        function excludeLabel(label) {
            if (cfg.excludeHeader && typeof cfg.excludeHeader === 'function') {
                return cfg.excludeHeader(label);
            }
            return defaultExcludeHeader(label);
        }
        function isSr(label) {
            if (cfg.isSrHeader && typeof cfg.isSrHeader === 'function') {
                return cfg.isSrHeader(label);
            }
            return defaultIsSrHeader(label);
        }
        function exportColumnIndexes() {
            return table.columns(':visible').indexes().toArray().filter(function (i) {
                return !excludeLabel(headerText(table, i));
            });
        }
        function buildExportMatrix() {
            var cols = exportColumnIndexes();
            var headers = cols.map(function (i) { return headerText(table, i); });
            var rowIdxs = table.rows({ search: 'applied', order: 'applied' }).indexes().toArray();
            var body = rowIdxs.map(function (rowIdx, displayIdx) {
                return cols.map(function (colIndex) {
                    var h = headerText(table, colIndex);
                    if (isSr(h)) {
                        return String(displayIdx + 1);
                    }
                    var html = table.cell(rowIdx, colIndex).render('display');
//                    return stripHtml(html).replace(/\s+/g, ' ').trim();

//                    var clean = stripHtml(html).replace(/\s+/g, ' ').trim();
//
//                    /* 👉 FIX: break values into new lines */
////                    if (h.toLowerCase().includes('serial') || h.toLowerCase().includes('stocks purchased')) {
////                        clean = clean.replace(/(\d+)\s+/g, '$1\n');
////                    }
//                    if (h.toLowerCase().includes('serial') || h.toLowerCase().includes('stocks purchased')) {
////                        clean = clean.split(/\s*(\d+\)).join('\n');
//                        clean = clean.replace(/\s*(\d+\))\s*/g, '\n$1 ');
//                    }
//                    return clean;
//                    var clean = stripHtml(html).replace(/\s+/g, ' ').trim();
//
//                    /* universal list formatter */
//                    clean = clean
//                        .replace(/\s*(\d+[.)])\s*/g, '\n$1 ')
//                        .replace(/^\n/, '');
//
//                    return clean;
//                     var clean = stripHtml(html).replace(/\s+/g, ' ').trim();
//
//                    /* detect numbered list (stock column) */
//                    if (/\d+[.)]/.test(clean)) {
//                        clean = clean
//                            .replace(/\s*(\d+[.)])\s*/g, '\n$1 ')
//                            .replace(/^\n/, '');
//                    }
//
//                    /* ✅ FIX for quantity column (Nos values) */
//                    else if (/(\d+\s*Nos)/i.test(clean)) {
//                        clean = clean
//                            .replace(/\s*(\d+\s*Nos)\s*/gi, '\n$1 ')
//                            .replace(/^\n/, '');
//                    }
//
//                    return clean;

                    var clean = stripHtml(html).replace(/\s+/g, ' ').trim();

                    /* ✅ Handle numbered lists (stock column) */
                    if (/\d+[.)]/.test(clean)) {
                        clean = clean
                            .replace(/\s*(\d+[.)])\s*/g, '\n$1 ')
                            .replace(/^\n/, '');
                    }

                    /* ✅ Handle quantity column (Nos, Ltr, Bunch etc.) */
                    else if (/(Nos|Ltr|Bunch)/i.test(clean)) {
                        clean = clean
                            .replace(/\s*(\d+\s*(Nos|Ltr|Bunch))/gi, '\n$1')
                            .replace(/^\n/, '');
                    }

                    return clean;

                });
            });
            return { headers: headers, body: body };
        }
        return {
            buildExportMatrix: buildExportMatrix,
            headerText: headerText
        };
    }

    function escapeHtml(s) {
        return String(s == null ? '' : s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function pdfTableMetrics(columnCount) {
        var n = Math.max(1, columnCount);
        if (n <= 9) {
            return { fontSize: 8, cellPadding: 1.5 };
        }
        if (n <= 12) {
            return { fontSize: 7, cellPadding: 1.25 };
        }
        if (n <= 15) {
            return { fontSize: 6, cellPadding: 1 };
        }
        if (n <= 18) {
            return { fontSize: 5.5, cellPadding: 0.9 };
        }
        return { fontSize: 5, cellPadding: 0.85 };
    }

    /**
     * Portrait if few columns and estimated equal column width fits comfortably; landscape otherwise.
     * Uses pdfTableMetrics() only for fontSize/cellPadding in the width estimate — tier breakpoints unchanged.
     * @param {number} columnCount
     * @param {number} sideM margin mm (same as PDF margins)
     * @returns {'p'|'l'}
     */
    function choosePdfOrientation(columnCount, sideM) {
        var n = Math.max(1, columnCount);
        var m = pdfTableMetrics(n);
        /* Many columns: always landscape */
        if (n >= 12) {
            return 'l';
        }
        var portraitInnerW = 210 - 2 * sideM;
        /* Rough minimum mm per column at the font size used for that column count (comfortable grid cells) */
        var minColMm = 7.5 + m.fontSize * 0.95 + m.cellPadding * 2.4;
        var estimatedNeed = n * minColMm;
        if (estimatedNeed <= portraitInnerW * 0.94) {
            return 'p';
        }
        return 'l';
    }

    function listExportIsConsumerFirmNameHeader(label) {
        var t = (label || '').trim().toLowerCase();
        return t.indexOf('consumer') !== -1 && (t.indexOf('firm') !== -1 || t.indexOf('farm') !== -1 || (t.indexOf('name') !== -1 && t.indexOf('/') !== -1));
    }

    /** Name + phone merge targets (Consumer/Firm/Farm, staff Full Name, complaint Name / Customer Name). */
    function listExportIsNameColumnForPhoneMerge(label) {
        var t = (label || '').trim().toLowerCase();
        return listExportIsConsumerFirmNameHeader(label) || t === 'full name' || t === 'name' || t === 'customer name';
    }

    function listExportIsPhoneColumnHeader(label) {
        var t = (label || '').trim().toLowerCase();
        if (t === 'mobile' || t === 'phone') {
            return true;
        }
        if (t === 'mobile number' || t === 'phone number' || t === 'contact number') {
            return true;
        }
        if (t.indexOf('mobile') !== -1 && t.indexOf('number') !== -1) {
            return true;
        }
        return false;
    }

    /**
     * Columns that should get extra PDF width and (optionally) UI class col-primary-name-field.
     */
    function listExportIsWideNameColumnHeader(label) {
        var t = (label || '').trim().toLowerCase();
        if (listExportIsConsumerFirmNameHeader(label)) {
            return true;
        }
        if (t === 'full name') {
            return true;
        }
        if (t.indexOf('supplier name') !== -1) {
            return true;
        }
        if (t.indexOf('favorite list name') !== -1 || t.indexOf('favourite list name') !== -1) {
            return true;
        }
        if (t === 'name') {
            return true;
        }
        if (t.indexOf('stock name') !== -1) {
            return true;
        }
        if (t.indexOf('category name') !== -1) {
            return true;
        }
        if (t === 'consumer name') {
            return true;
        }
        if (t === 'customer name') {
            return true;
        }
        return false;
    }

    /** Supplier Name / Consumer Name cells with "Ph No :" in HTML → split for PDF (same as purchase list). */
    function listExportIsInlinePhNoSplitColumnHeader(label) {
        var t = (label || '').trim().toLowerCase();
        return t === 'supplier name' || t === 'consumer name';
    }

    /**
     * Minimum height for merged name + Ph No (two lines). Keep close to real content height so rows are not stretched.
     */
    function pdfLandscapeNameColumnMinHeight(tblMetrics) {
        var fs = tblMetrics.fontSize;
        var pad = tblMetrics.cellPadding;
        var fsSmall = Math.max(4.8, fs * 0.72);
        var h = pad * 1.35 + fs * 0.52 + fsSmall * 0.48 + 0.45;
        return Math.max(6.8, Math.min(13.5, h));
    }

    function pdfPortraitNameColumnMinHeight(tblMetrics) {
        var fs = tblMetrics.fontSize;
        var pad = tblMetrics.cellPadding;
        var fsSmall = Math.max(4.8, fs * 0.72);
        var h = pad * 1.45 + fs * 0.55 + fsSmall * 0.5 + 0.5;
        return Math.max(7.2, Math.min(14.5, h));
    }

    /** @param {'p'|'l'} [orient] */
    function applyPdfWideNameColumnStyles(autoOpts, headers, tblMetrics, pack, orient) {
        if (!headers || !headers.length) {
            return;
        }
        autoOpts.columnStyles = autoOpts.columnStyles || {};
        var isL = orient === 'l';
        var i;
        for (i = 0; i < headers.length; i++) {
            if (!listExportIsWideNameColumnHeader(headers[i])) {
                continue;
            }
            var base = { minCellWidth: 48, valign: 'top', halign: 'left' };
            /* Inline name+Ph split: per-cell min height in hooks — avoid tall empty bands on single-line rows */
            if (pack && pack.merged && i === pack.nameColIndex && !pack.inlinePhNoSplit && !pack.supplierInlineSplit) {
                base.minCellHeight = isL ? pdfLandscapeNameColumnMinHeight(tblMetrics) : pdfPortraitNameColumnMinHeight(tblMetrics);
            }
            autoOpts.columnStyles[i] = Object.assign({}, base, autoOpts.columnStyles[i] || {});
        }
    }

    /**
     * Extra top inset; minimal bottom so text sits top-aligned with less gap above grid line and less dead space below.
     * Left/right must be large enough (mm) or PDF renders text flush on the cell border.
     */
    function pdfTableCellPaddingForOrientation(tblMetrics, orient) {
        var raw = tblMetrics.cellPadding;
        var sideBase = Math.max(0.24, raw * 0.46);
        var horizontal = Math.max(1.65, sideBase + 1.05);
        var topBoost = orient === 'l' ? 0.58 : 0.68;
        var t = sideBase + topBoost;
        var b = orient === 'l'
            ? Math.max(0.04, sideBase * 0.1)
            : Math.max(0.05, sideBase * 0.12);
        return { top: t, right: horizontal, left: horizontal, bottom: b };
    }

    /**
     * jsPDF-AutoTable sometimes ignores object cellPadding on global styles; re-apply per cell after other hooks.
     */
    function attachPdfEnforceCellLayout(autoOpts, cellPadObj) {
        var prev = autoOpts.didParseCell;
        autoOpts.didParseCell = function (data) {
            if (typeof prev === 'function') {
                prev(data);
            }
            if (!data.cell) {
                return;
            }
            data.cell.styles = data.cell.styles || {};
            data.cell.styles.valign = 'top';
            data.cell.styles.halign = 'left';
            if (cellPadObj && typeof cellPadObj === 'object') {
                data.cell.styles.cellPadding = {
                    top: cellPadObj.top,
                    right: cellPadObj.right,
                    left: cellPadObj.left,
                    bottom: cellPadObj.bottom
                };
            }
        };
    }

    /** Body/header table text: landscape 8 pt, portrait 9 pt (jsPDF autoTable). */
    function pdfTableFontSizeForOrientation(orient) {
        return orient === 'l' ? 8 : 9;
    }

    /**
     * Merges the phone column into Consumer/Firm Name or Full Name for PDF/print only (Excel/copy stay separate).
     * @returns {{ headers: string[], body: string[][], nameColIndex: number, merged: boolean }}
     */
    function mergeNamePhoneColumnsForPdf(exp) {
        var headers = exp.headers.slice();
        var body = exp.body.map(function (r) { return r.slice(); });
        var nameIdx = -1;
        var phoneIdx = -1;
        var i;
        for (i = 0; i < headers.length; i++) {
            if (nameIdx < 0 && listExportIsNameColumnForPhoneMerge(headers[i])) {
                nameIdx = i;
            }
            if (phoneIdx < 0 && listExportIsPhoneColumnHeader(headers[i])) {
                phoneIdx = i;
            }
        }
        if (nameIdx >= 0 && listExportIsConsumerFirmNameHeader(headers[nameIdx])) {
            headers[nameIdx] = 'Consumer / Firm Name';
        }
        var out = {
            headers: headers,
            body: body,
            nameColIndex: nameIdx,
            merged: false
        };
        if (nameIdx < 0 || phoneIdx < 0 || nameIdx === phoneIdx) {
            return out;
        }
        var wasConsumer = listExportIsConsumerFirmNameHeader(headers[nameIdx]);
        for (i = 0; i < body.length; i++) {
            var name = String(body[i][nameIdx] || '').trim();
            var phone = String(body[i][phoneIdx] || '').trim();
            body[i][nameIdx] = phone ? (name + '\n' + 'Ph No : ' + phone) : name;
        }
        body.forEach(function (row) {
            row.splice(phoneIdx, 1);
        });
        headers.splice(phoneIdx, 1);
        var newNameIdx = phoneIdx < nameIdx ? nameIdx - 1 : nameIdx;
        out.headers = headers;
        out.body = body;
        out.nameColIndex = newNameIdx;
        out.merged = true;
        if (wasConsumer) {
            out.headers[newNameIdx] = 'Consumer / Firm Name';
        } else if ((out.headers[newNameIdx] || '').trim().toLowerCase() === 'full name') {
            out.headers[newNameIdx] = 'Full Name';
        }
        return out;
    }

    /**
     * Supplier/vendor lists: separate Name + Contact (phone) columns → one column with Ph No below name in PDF/print.
     */
    function mergeNameContactColumnsForPdf(exp) {
        var headers = exp.headers.slice();
        var body = exp.body.map(function (r) { return r.slice(); });
        var nameIdx = -1;
        var contactIdx = -1;
        var i;
        for (i = 0; i < headers.length; i++) {
            if (nameIdx < 0 && (headers[i] || '').trim().toLowerCase() === 'name') {
                nameIdx = i;
            }
            if (contactIdx < 0 && (headers[i] || '').trim().toLowerCase() === 'contact') {
                contactIdx = i;
            }
        }
        var out = {
            headers: headers,
            body: body,
            nameColIndex: nameIdx,
            merged: false
        };
        if (nameIdx < 0 || contactIdx < 0 || nameIdx === contactIdx) {
            return out;
        }
        for (i = 0; i < body.length; i++) {
            var name = String(body[i][nameIdx] || '').trim();
            var phone = String(body[i][contactIdx] || '').trim();
            body[i][nameIdx] = phone ? (name + '\n' + 'Ph No : ' + phone) : name;
        }
        body.forEach(function (row) {
            row.splice(contactIdx, 1);
        });
        headers.splice(contactIdx, 1);
        var newNameIdx = contactIdx < nameIdx ? nameIdx - 1 : nameIdx;
        out.headers = headers;
        out.body = body;
        out.nameColIndex = newNameIdx;
        out.merged = true;
        return out;
    }

    /**
     * Purchase / sales / return lists: one cell (Supplier Name or Consumer Name) contains "… Ph No : …" after stripHtml.
     */
    function splitInlinePhNoInNamedColumnForPdf(exp) {
        var headers = exp.headers.slice();
        var body = exp.body.map(function (r) { return r.slice(); });
        var idx = -1;
        var i;
        for (i = 0; i < headers.length; i++) {
            if (listExportIsInlinePhNoSplitColumnHeader(headers[i])) {
                idx = i;
                break;
            }
        }
        var out = {
            headers: headers,
            body: body,
            nameColIndex: idx,
            merged: false
        };
        if (idx < 0) {
            return out;
        }
        var did = false;
        for (i = 0; i < body.length; i++) {
            var s = String(body[i][idx] || '').trim();
            var phAt = s.search(/\s*Ph No\s*:\s*/i);
            if (phAt < 0) {
                continue;
            }
            var name = s.slice(0, phAt).replace(/\s+/g, ' ').trim();
            var phone = s.slice(phAt).replace(/^\s*Ph No\s*:\s*/i, '').replace(/\s+/g, ' ').trim();
            if (name && phone) {
                body[i][idx] = name + '\n' + 'Ph No : ' + phone;
                did = true;
            }
        }
        if (did) {
            out.merged = true;
            out.inlinePhNoSplit = true;
            out.supplierInlineSplit = true;
        }
        return out;
    }

    /**
     * PDF/print matrix: only apply name+phone rules when explicitly configured on ListPageExport.register().
     */
    function prepareListPagePdfExport(expRaw, cfg) {
        var cfgObj = cfg || {};
        if (cfgObj.pdfMergeNamePhoneColumns) {
            return mergeNamePhoneColumnsForPdf(expRaw);
        }
        if (cfgObj.pdfMergeNameContactColumns) {
            return mergeNameContactColumnsForPdf(expRaw);
        }
        if (cfgObj.pdfSplitInlinePhNoColumn || cfgObj.pdfSplitSupplierInlinePhone) {
            return splitInlinePhNoInNamedColumnForPdf(expRaw);
        }
        return {
            headers: expRaw.headers.slice(),
            body: expRaw.body.map(function (r) { return r.slice(); }),
            nameColIndex: -1,
            merged: false
        };
    }

    function listExportCellPad(cell, side, fallback) {
        if (typeof cell.padding === 'function') {
            return cell.padding(side);
        }
        var p = cell.padding;
        if (p && typeof p === 'object') {
            if (side === 'left' && typeof p.left === 'number') { return p.left; }
            if (side === 'right' && typeof p.right === 'number') { return p.right; }
            if (side === 'top' && typeof p.top === 'number') { return p.top; }
            if (side === 'bottom' && typeof p.bottom === 'number') { return p.bottom; }
        }
        if (cell.styles && typeof cell.styles.cellPadding === 'number') {
            return cell.styles.cellPadding;
        }
        return fallback;
    }

    /**
     * Two-line cell: name at table font size, phone smaller.
     * IMPORTANT: jsPDF-AutoTable fills the cell *after* willDrawCell, which painted over our text.
     * Draw in didDrawCell so name + Ph No appear on top of the finished cell.
     */
    function attachPdfNamePhoneCellHooks(autoOpts, ctx) {
        if (!ctx || !ctx.merged || ctx.nameColIndex < 0) {
            return;
        }
        var nameColIndex = ctx.nameColIndex;
        var tblMetrics = ctx.tblMetrics;
        var isLandscapePdf = ctx.pdfOrientation === 'l';
        var inlineCompact = !!(ctx.inlinePhNoSplit || ctx.supplierInlineSplit);
        var prevDidParse = autoOpts.didParseCell;
        autoOpts.didParseCell = function (data) {
            if (typeof prevDidParse === 'function') {
                prevDidParse(data);
            }
            if (data.section === 'body' && data.column.index === nameColIndex) {
                var raw = data.cell.raw;
                if (typeof raw === 'string' && raw.indexOf('\n') >= 0) {
                    data.cell.text = [];
                    if (inlineCompact) {
                        if (!data.cell.styles) {
                            data.cell.styles = {};
                        }
                        var fs = tblMetrics.fontSize;
                        var fsS = Math.max(4.8, fs * 0.72);
                        var padT = tblMetrics.cellPadding * 2;
                        /* Tight two-line block (supplier + Ph No), no column-wide min */
                        // var h = padT + fs * 0.92 + fsS * 0.48 + 0.7;
                        // data.cell.styles.minCellHeight = Math.max(9.5, Math.min(22, h));
//                        var h = padT + fs * 0.75 + fsS * 0.40; // reduced spacing
//                        data.cell.styles.minCellHeight = Math.max(8, Math.min(16, h));
                        var h = padT + fs * 0.52 + fsS * 0.32;
                        if (isLandscapePdf) {
                            h *= 0.88;
                        }
                        data.cell.styles.minCellHeight = Math.max(6.5, Math.min(isLandscapePdf ? 10 : 12.5, h));
                    }
                }
            }
        };
        var prevDidDraw = autoOpts.didDrawCell;
        autoOpts.didDrawCell = function (data) {
            if (typeof prevDidDraw === 'function') {
                prevDidDraw(data);
            }
            if (data.section !== 'body' || data.column.index !== nameColIndex) {
                return;
            }

            var rawFull = String(data.cell.raw || '');
            var ix = rawFull.indexOf('\n');
            if (ix < 0) {
                return;
            }
            var namePart = rawFull.slice(0, ix).trim() || '—';
            var phonePart = rawFull.slice(ix + 1).trim();
            if (!phonePart) {
                return;
            }
            var cell = data.cell;
            var doc = data.doc;
            var padL = listExportCellPad(cell, 'left', tblMetrics.cellPadding);
            var padR = listExportCellPad(cell, 'right', tblMetrics.cellPadding);
            var padT = listExportCellPad(cell, 'top', tblMetrics.cellPadding);
            var x = cell.x + padL;
            var maxW = Math.max(12, cell.width - padL - padR);
            var fs = tblMetrics.fontSize;
            var fsSmall = Math.max(4.8, fs * 0.72);
            var lineStepName = Math.max(2.85, fs * 0.47);
            var lineStepPhone = Math.max(2.55, fsSmall * 0.46);

            doc.setTextColor(0, 0, 0);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(fs);
            var nameLines = doc.splitTextToSize(namePart, maxW);
//            var y = cell.y + padT + lineStepName * 0.85;
            var y = cell.y + padT + 2.5;
            var li;
            for (li = 0; li < nameLines.length; li++) {
                doc.text(nameLines[li], x, y);
                y += lineStepName;
            }
            y += -0.3;
            doc.setFontSize(fsSmall);
            doc.setTextColor(45, 45, 45);
            var phoneLines = doc.splitTextToSize(phonePart, maxW);
            for (li = 0; li < phoneLines.length; li++) {
                doc.text(phoneLines[li], x, y);
                y += lineStepPhone;
            }
        };
    }

    function printTableCellHtml(cell, colIndex, pack, escapeHtmlFn) {
        if (pack && pack.merged && colIndex === pack.nameColIndex && String(cell).indexOf('\n') >= 0) {
            var p = String(cell).split('\n');
            var phoneLine = p.slice(1).join('\n').trim();
            return '<td class="td-export-name-phone"><span class="export-name">' + escapeHtmlFn(p[0].trim()) + '</span><span class="export-phone"><small>' + escapeHtmlFn(phoneLine) + '</small></span></td>';
        }
        return '<td>' + escapeHtmlFn(cell) + '</td>';
    }

    /** Resolve at click time — register() often runs before base.html loads jspdf.umd.min.js */
    function getJsPDFConstructor() {
        if (global.jspdf && global.jspdf.jsPDF) {
            return global.jspdf.jsPDF;
        }
        if (typeof global.jsPDF !== 'undefined') {
            return global.jsPDF;
        }
        return null;
    }

    /**
     * @param {Object} cfg
     * @param {string} cfg.apiPrefix e.g. 'supplierList' -> window.supplierListGeneratePDF
     * @param {string} [cfg.tableSelector='#yourDataTable']
     * @param {string} cfg.pdfFilename
     * @param {string} cfg.excelFilename
     * @param {string} cfg.excelSheetName
     * @param {string} cfg.printDocumentTitle
     * @param {function(string):boolean} [cfg.excludeHeader]
     * @param {function(string):boolean} [cfg.isSrHeader]
     * @param {boolean} [cfg.pdfMergeNamePhoneColumns] Merge phone column into name for PDF/print only: Consumer/Firm/Farm, Full Name, or complaint lists (Name + Mobile Number / Customer Name + Contact Number)
     * @param {boolean} [cfg.pdfMergeNameContactColumns] Merge Contact (phone) under Name column (supplier/vendor lists)
     * @param {boolean} [cfg.pdfSplitInlinePhNoColumn] Split "Supplier Name" / "Consumer Name" cells that contain "Ph No :" text onto two lines (purchase, sales, returns)
     * @param {boolean} [cfg.pdfSplitSupplierInlinePhone] Alias for pdfSplitInlinePhNoColumn (purchase lists)
     * @param {string} [cfg.pdfCaption] Bold heading below letterhead on page 1 (defaults to printDocumentTitle if omitted)
     */
    function register(cfg) {
        if (!cfg || !cfg.apiPrefix) {
            return;
        }
        var tableSel = cfg.tableSelector || '#yourDataTable';

        function getTable() {
            if (typeof global.jQuery === 'undefined' || !global.jQuery.fn.dataTable) {
                return null;
            }
            if (!global.jQuery.fn.dataTable.isDataTable(tableSel)) {
                return null;
            }
            return global.jQuery(tableSel).DataTable();
        }

        function runPdf(logoDataUrl) {
            var table = getTable();
            if (!table) {
                alert('Table is not ready yet.');
                return;
            }
            var api = buildExportApi(table, cfg);
            var expRaw = api.buildExportMatrix();
            var pack = prepareListPagePdfExport(expRaw, cfg);
            var exp = { headers: pack.headers, body: pack.body };
            var sideM = 10;
            var PDFCtor = getJsPDFConstructor();
            if (!PDFCtor) {
                alert('PDF library not loaded.');
                return;
            }
            var orient = choosePdfOrientation(exp.headers.length, sideM);
            var tblMetrics = pdfTableMetrics(exp.headers.length);
            tblMetrics.fontSize = pdfTableFontSizeForOrientation(orient);
            var pdf = new PDFCtor(orient, 'mm', 'a4');
            var y0 = 8;
            var hb = listPdfLetterheadBottomMm(pdf, logoDataUrl, sideM, y0);
            var capText = listPdfResolveCaption(cfg);
            var capBlock = listPdfMeasureCaptionBlock(pdf, capText, sideM);
            var bodyStart = hb + (capBlock.extraBelowLetterheadMm > 0 ? capBlock.extraBelowLetterheadMm : 3);
            var cellPad = pdfTableCellPaddingForOrientation(tblMetrics, orient);
            tblMetrics.cellPadding = typeof cellPad === 'object' ? cellPad.top : cellPad;
            var autoOpts = {
                head: [exp.headers],
                body: exp.body,
                theme: 'grid',
                styles: {
                    fontSize: tblMetrics.fontSize,
                    cellPadding: cellPad,
                    overflow: 'linebreak',
                    valign: 'top',
                    halign: 'left'
                },
                bodyStyles: {
                    fontSize: tblMetrics.fontSize,
                    cellPadding: cellPad,
                    valign: 'top',
                    halign: 'left'
                },
                headStyles: {
                    fillColor: [238, 238, 238],
                    textColor: [0, 0, 0],
                    fontStyle: 'bold',
                    fontSize: tblMetrics.fontSize,
                    cellPadding: cellPad,
                    valign: 'top',
                    halign: 'left'
                },
                startY: bodyStart + 2,
                margin: { top: bodyStart, left: sideM, right: sideM, bottom: 12 },
                didDrawPage: function (data) {
                    var doc = data.doc;
                    var pageNum = data.pageNumber != null ? data.pageNumber : 1;
                    if (typeof doc.setPage === 'function') {
                        doc.setPage(pageNum);
                    }
                    drawListPdfLetterhead(doc, logoDataUrl, sideM, y0);
                    listPdfDrawCaptionAfterLetterhead(doc, capBlock, sideM, hb, pageNum);
                }
            };
            applyPdfWideNameColumnStyles(autoOpts, exp.headers, tblMetrics, pack, orient);
            if (pack.merged) {
                attachPdfNamePhoneCellHooks(autoOpts, {
                    merged: true,
                    nameColIndex: pack.nameColIndex,
                    tblMetrics: tblMetrics,
                    inlinePhNoSplit: !!pack.inlinePhNoSplit,
                    supplierInlineSplit: !!(pack.inlinePhNoSplit || pack.supplierInlineSplit),
                    pdfOrientation: orient
                });
            }
            attachPdfEnforceCellLayout(autoOpts, cellPad);
            if (typeof pdf.autoTable === 'function') {
                pdf.autoTable(autoOpts);
            }
            pdf.save(cfg.pdfFilename || 'export.pdf');
        }

        global[cfg.apiPrefix + 'GeneratePDF'] = function () {
            loadPdfHeaderImageDataUrl(listPdfLogoAbsoluteUrl(), function (dataUrl) {
                runPdf(dataUrl);
            });
        };

        global[cfg.apiPrefix + 'GenerateExcel'] = function () {
            if (typeof XLSX === 'undefined') {
                alert('Excel library not loaded.');
                return;
            }
            var table = getTable();
            if (!table) {
                alert('Table is not ready yet.');
                return;
            }
            var api = buildExportApi(table, cfg);
            var exp = api.buildExportMatrix();
            var ws = XLSX.utils.aoa_to_sheet([exp.headers].concat(exp.body));
            var wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, cfg.excelSheetName || 'Sheet1');
            XLSX.writeFile(wb, cfg.excelFilename || 'export.xlsx');
        };

        global[cfg.apiPrefix + 'CopyToClipboard'] = function () {
            var table = getTable();
            if (!table) {
                alert('Table is not ready yet.');
                return;
            }
            var api = buildExportApi(table, cfg);
            var exp = api.buildExportMatrix();
            var data = [exp.headers].concat(exp.body);
            var plainTextData = data.map(function (row) {
                return row.map(function (cell) { return String(cell == null ? '' : cell); }).join('\t');
            }).join('\n');
            var ta = document.createElement('textarea');
            ta.value = plainTextData;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            alert('Current table (filtered & sorted) copied to clipboard.');
        };

        global[cfg.apiPrefix + 'PrintTable'] = function () {
            var table = getTable();
            if (!table) {
                alert('Table is not ready yet.');
                return;
            }
            var api = buildExportApi(table, cfg);
            var expRaw = api.buildExportMatrix();
            var pack = prepareListPagePdfExport(expRaw, cfg);
            var exp = { headers: pack.headers, body: pack.body };
            var n = exp.headers.length;
            var theadRow = '<tr>' + exp.headers.map(function (h) {
                return '<th>' + escapeHtml(h) + '</th>';
            }).join('') + '</tr>';
            var letterRow = '<tr class="dt-print-letterhead"><td colspan="' + n + '" style="border:none!important;padding:0 0 16px 0!important;vertical-align:top;background:#fff;">' +
                listPdfPrintLetterheadInnerHtml() + '</td></tr>';
            var capPrint = listPdfResolveCaption(cfg);
            var captionRow = capPrint ? '<tr class="dt-print-caption"><td colspan="' + n + '" style="border:none!important;padding:4px 8px 10px!important;text-align:center;font-weight:bold;font-size:13px;color:#111;">' +
                escapeHtml(capPrint) + '</td></tr>' : '';
            var tbodyHtml = exp.body.map(function (row) {
                return '<tr>' + row.map(function (cell, ci) {
                    return printTableCellHtml(cell, ci, pack, escapeHtml);
                }).join('') + '</tr>';
            }).join('');
            var w = global.open('', '_blank');
            w.document.open();
            w.document.write(
                '<html><head><title>' + escapeHtml(cfg.printDocumentTitle || 'Print') + '</title>' +
                '<style>' +
                'body{font-family:Arial,sans-serif;color:#000;margin:12px}' +
                'table.dt-print-main{width:100%;max-width:100%;border-collapse:collapse;border:2px solid #000;table-layout:auto}' +
                'thead{display:table-header-group}' +
                'tr.dt-print-letterhead td{border:none!important}' +
                'tr.dt-print-caption td{border:none!important}' +
                'thead tr:not(.dt-print-letterhead):not(.dt-print-caption) th{border:1px solid #000!important;padding:4px 6px 2px 8px;font-size:10px;vertical-align:top;text-align:left;background:#eee;font-weight:bold;white-space:nowrap}' +
                'tbody td{border:1px solid #000!important;padding:4px 6px 2px 8px;font-size:10px;vertical-align:top;text-align:left}' +
                '.td-export-name-phone .export-name{display:block;font-weight:600;line-height:1.25}' +
                '.td-export-name-phone .export-phone{display:block;margin-top:3px;line-height:1.25}' +
                '.td-export-name-phone .export-phone small{font-size:9px;color:#333;font-weight:normal}' +
                '@media print{' +
                '@page{size:A4 landscape;margin:8mm 10mm}' +
                'body{margin:0}' +
                'thead{display:table-header-group}' +
                'tr.dt-print-letterhead td{-webkit-print-color-adjust:exact;print-color-adjust:exact}' +
                'table.dt-print-main{width:100%;max-width:100%}' +
                'table,th,td{border-color:#000!important}' +
                '}' +
                '</style></head><body>' +
                '<table class="dt-print-main" border="0" cellspacing="0" cellpadding="0">' +
                '<thead>' + letterRow + captionRow + theadRow + '</thead><tbody>' + tbodyHtml + '</tbody></table></body></html>'
            );
            w.document.close();
            w.focus();
            w.print();
        };
    }

    global.ListPageExport = {
        register: register,
        listPdfLogoAbsoluteUrl: listPdfLogoAbsoluteUrl,
        listPdfResolveCaption: listPdfResolveCaption,
        listPdfMeasureCaptionBlock: listPdfMeasureCaptionBlock,
        listPdfDrawCaptionAfterLetterhead: listPdfDrawCaptionAfterLetterhead,
        mergeNamePhoneColumnsForPdf: mergeNamePhoneColumnsForPdf,
        mergeNameContactColumnsForPdf: mergeNameContactColumnsForPdf,
        splitInlinePhNoInNamedColumnForPdf: splitInlinePhNoInNamedColumnForPdf,
        prepareListPagePdfExport: prepareListPagePdfExport,
        attachPdfNamePhoneCellHooks: attachPdfNamePhoneCellHooks,
        printTableCellHtml: printTableCellHtml,
        applyPdfWideNameColumnStyles: applyPdfWideNameColumnStyles,
        listExportIsWideNameColumnHeader: listExportIsWideNameColumnHeader
    };
})(typeof window !== 'undefined' ? window : this);
