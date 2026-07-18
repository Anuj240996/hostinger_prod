    function disposeSolar3DView(container) {
        var state = container._solar3dState;
        if (state) {
            if (state.rafId) cancelAnimationFrame(state.rafId);
            if (state.resizeObserver) state.resizeObserver.disconnect();
            if (state.controls) state.controls.dispose();
            if (state.renderer) state.renderer.dispose();
        }
        container._solar3dState = null;
        var zoomEl = container.querySelector('.solar-3d-zoom-controls');
        if (zoomEl) zoomEl.remove();
        container.innerHTML = '';
        var stage = container.parentElement;
        if (stage && stage.classList.contains('solar-3d-stage')) {
            var overlay = stage.querySelector('.solar-3d-overlay');
            if (overlay) overlay.remove();
        }
    }

    // Keep print/embed 3D in sync with Survey Details interactive view.
    var SOLAR_PANEL_WIDTH_FT = 4;
    var SOLAR_PANEL_LENGTH_FT = 8;
    var SOLAR_PANEL_ROW_GAP_FT = 2;

    function solarStructureDepthFt(rows) {
        var r = Math.max(rows || 0, 0);
        if (r < 1) return SOLAR_PANEL_LENGTH_FT;
        return r * SOLAR_PANEL_LENGTH_FT + Math.max(r - 1, 0) * SOLAR_PANEL_ROW_GAP_FT;
    }

    function panelRowDepthFrac(row, rows) {
        var r = Math.max(rows, 1);
        var totalFt = solarStructureDepthFt(r);
        var startFt = row * (SOLAR_PANEL_LENGTH_FT + SOLAR_PANEL_ROW_GAP_FT);
        return {
            t0: startFt / totalFt,
            t1: (startFt + SOLAR_PANEL_LENGTH_FT) / totalFt
        };
    }

    function buildSolarStructureLayout(opts) {
        var legs = parseInt(opts.legs, 10) || 0;
        var rafters = parseInt(opts.rafters, 10) || 0;
        var purlins = parseInt(opts.purlins, 10) || 0;
        var solarPanels = parseInt(opts.solarPanels, 10);
        var frontH = parseFloat(opts.frontHeight);
        var backH = parseFloat(opts.backHeight);
        frontH = isNaN(frontH) ? 10 : frontH;
        backH = isNaN(backH) ? 20 : backH;
        var frontLegCount = Math.ceil(legs / 2);
        var backLegCount = Math.floor(legs / 2);
        var legCols = Math.max(frontLegCount, backLegCount, 1);
        var rafterCols = rafters;
        var spanCols = Math.max(legCols, rafterCols);
        var panelCount = isNaN(solarPanels) || solarPanels < 1 ? 0 : solarPanels;
        var hasWalkway = !!opts.hasWalkway;
        var hasLadder = !!opts.hasLadder;
        var squarePipeCount = parseInt(opts.squarePipeCount, 10);
        if (isNaN(squarePipeCount) || squarePipeCount < 1) squarePipeCount = hasLadder ? 6 : 0;
        var walkwayRafterBonus = hasWalkway ? 2 : 0;
        var walkwayPurlinBonus = hasWalkway ? 4 : 0;
        var panelPurlins = Math.max(0, purlins - walkwayPurlinBonus);
        if (panelPurlins < 1 && purlins >= 1) panelPurlins = purlins;
        // Upper panel rafters only (1 per leg column). Walkway +2 are separate lower left/right rafters.
        var mainRafterCols = Math.max(1, Math.ceil(legs / 2) || 1);
        if (!hasWalkway && rafters >= 1) {
            mainRafterCols = rafters;
        }
        rafterCols = mainRafterCols;
        spanCols = Math.max(legCols, rafterCols);
        var panelRowsFromPurlins = Math.max(1, Math.floor(Math.max(panelPurlins, 1) / 2));
        var panelColsWidth = panelCount > 0 ? Math.max(1, Math.ceil(panelCount / panelRowsFromPurlins)) : 0;
        var panelGrid = panelCount > 0 ? {
            rows: panelRowsFromPurlins,
            cols: panelColsWidth,
            total: panelCount
        } : { rows: 0, cols: 0, total: 0 };

        var PANEL_WIDTH_FT = SOLAR_PANEL_WIDTH_FT;
        var PANEL_LENGTH_FT = SOLAR_PANEL_LENGTH_FT;
        var PANEL_ROW_GAP_FT = SOLAR_PANEL_ROW_GAP_FT;
        var structureWidthFt = panelGrid.cols > 0
            ? panelGrid.cols * PANEL_WIDTH_FT
            : Math.max(legCols - 1, 1) * PANEL_WIDTH_FT;
        var structureDepthFt = panelGrid.rows > 0
            ? solarStructureDepthFt(panelGrid.rows)
            : PANEL_LENGTH_FT;

        function purlinT(index) {
            return panelPurlins === 1 ? 0.5 : index / (panelPurlins - 1);
        }
        function panelDepthSpan(row) {
            var p0 = row * 2;
            var p1 = p0 + 1;
            if (p0 >= panelPurlins) {
                return { t0: row / panelGrid.rows, t1: (row + 1) / panelGrid.rows, p0: -1, p1: -1 };
            }
            if (p1 >= panelPurlins) p1 = panelPurlins - 1;
            if (p0 === p1 && p0 > 0) p0 = p0 - 1;
            var tA = purlinT(p0);
            var tB = purlinT(p1);
            return { t0: Math.min(tA, tB), t1: Math.max(tA, tB), p0: p0, p1: p1 };
        }
        function panelPortraitSpan(row) {
            var mount = panelDepthSpan(row);
            var gap = mount.t1 - mount.t0 || 0.15;
            var overhang = Math.max(gap * 0.24, 0.035);
            var t0 = Math.max(0, mount.t0 - overhang);
            var t1 = Math.min(1, mount.t1 + overhang);
            if (row > 0) {
                var prev = panelDepthSpan(row - 1);
                t0 = Math.max(t0, prev.t1 + 0.003);
            }
            if (row < panelGrid.rows - 1) {
                var next = panelDepthSpan(row + 1);
                t1 = Math.min(t1, next.t0 - 0.003);
            }
            return {
                t0: t0,
                t1: t1,
                mountT0: mount.t0,
                mountT1: mount.t1,
                p0: mount.p0,
                p1: mount.p1
            };
        }
        function rafterBayCol(r) {
            if (rafterCols <= 1) return 0;
            if (legCols === rafterCols) return r;
            return Math.round(r * (legCols - 1) / (rafterCols - 1));
        }

        return {
            legs: legs,
            rafters: rafters,
            purlins: purlins,
            panelCount: panelCount,
            frontH: frontH,
            backH: backH,
            frontLegCount: frontLegCount,
            backLegCount: backLegCount,
            legCols: legCols,
            rafterCols: rafterCols,
            spanCols: spanCols,
            panelGrid: panelGrid,
            panelWidthFt: PANEL_WIDTH_FT,
            panelLengthFt: PANEL_LENGTH_FT,
            panelRowGapFt: PANEL_ROW_GAP_FT,
            panelPurlins: panelPurlins,
            structureWidthFt: structureWidthFt,
            structureDepthFt: structureDepthFt,
            hasWalkway: hasWalkway,
            hasLadder: hasLadder,
            squarePipeCount: squarePipeCount,
            walkwayRafterBonus: walkwayRafterBonus,
            walkwayPurlinBonus: walkwayPurlinBonus,
            purlinT: purlinT,
            panelDepthSpan: panelDepthSpan,
            panelPortraitSpan: panelPortraitSpan,
            rafterBayCol: rafterBayCol,
            embedMode: !!opts.embedMode
        };
    }

    function build3dSummaryOverlayHtml(layout) {
        var html = '<span class="solar-3d-summary-title">Summary</span>';
        html += '<div>Front <strong>' + layout.frontH + ' ft</strong></div>';
        html += '<div>Back <strong>' + layout.backH + ' ft</strong></div>';
        if (layout.panelCount > 0) {
            html += '<div>Panels <strong>' + layout.panelCount + '</strong> (' + layout.panelGrid.cols + '\u00d7' + layout.panelGrid.rows + ')</div>';
            html += '<div>Array <strong>' + layout.structureWidthFt + ' \u00d7 ' + layout.structureDepthFt + ' ft</strong></div>';
            html += '<div>Module <strong>' + layout.panelWidthFt + ' \u00d7 ' + layout.panelLengthFt + ' ft</strong></div>';
        }
        html += '<div>Purlin <strong>' + layout.purlins + '</strong> Â· Rafter <strong>' + layout.rafters + '</strong></div>';
        html += '<div>Legs <strong>' + layout.legs + '</strong> (' + layout.frontLegCount + ' front + ' + layout.backLegCount + ' back)</div>';
        return html;
    }

    function setSolar3DFrontView(camera, controls, layout, xAt, frontTopY, backTopY, depth) {
        var xL = xAt(0);
        var xR = xAt(1);
        var spanW = Math.max(Math.abs(xR - xL), 1.15);
        var midY = (frontTopY + backTopY) / 2;
        var maxH = Math.max(frontTopY, backTopY, 0.5);
        var targetY = midY * 0.9;
        var targetZ = depth * 0.45;
        controls.target.set(0, targetY, targetZ);
        // Match Survey Details camera framing (including print/embed capture).
        var viewDist = (Math.max(spanW * 0.95 + depth * 0.95, maxH * 2.8) + 1.6) * 0.68;
        camera.position.set(
            spanW * 0.34 + 1.0,
            targetY + maxH * 0.14 + 0.1,
            -viewDist
        );
        if (layout.embedMode) {
            camera.fov = 34;
            camera.updateProjectionMatrix();
        }
        controls.update();
    }

    function buildMeasurementSummaryLines(layout) {
        if (!layout) return [];
        var lines = [
            'Front Height: ' + layout.frontH + ' ft   |   Back Height: ' + layout.backH + ' ft',
            'Legs: ' + layout.legs + '   |   Rafters: ' + layout.rafters + '   |   Purlins: ' + layout.purlins
        ];
        if (layout.panelCount > 0) {
            lines.push(
                'Solar Panels: ' + layout.panelCount + ' (' + layout.panelGrid.cols + ' \u00d7 ' + layout.panelGrid.rows + ')'
            );
        }
        return lines;
    }

    function findCanvasContentBounds(ctx, w, h) {
        var step = Math.max(1, Math.floor(Math.min(w, h) / 400));
        var data = ctx.getImageData(0, 0, w, h).data;
        var minX = w;
        var minY = h;
        var maxX = 0;
        var maxY = 0;
        var x;
        var y;
        var i;
        var r;
        var g;
        var b;
        var a;
        for (y = 0; y < h; y += step) {
            for (x = 0; x < w; x += step) {
                i = (y * w + x) * 4;
                r = data[i];
                g = data[i + 1];
                b = data[i + 2];
                a = data[i + 3];
                if (a < 12) continue;
                if (r > 248 && g > 248 && b > 248) continue;
                if (x < minX) minX = x;
                if (y < minY) minY = y;
                if (x > maxX) maxX = x;
                if (y > maxY) maxY = y;
            }
        }
        if (maxX <= minX || maxY <= minY) {
            return { x: 0, y: 0, w: w, h: h };
        }
            var pad = Math.max(18, Math.round(Math.min(w, h) * 0.035));
        minX = Math.max(0, minX - pad);
        minY = Math.max(0, minY - pad);
        maxX = Math.min(w - 1, maxX + pad);
        maxY = Math.min(h - 1, maxY + pad);
        return { x: minX, y: minY, w: maxX - minX + 1, h: maxY - minY + 1 };
    }

    function formatMeasureNumber(value) {
        var num = Number(value);
        if (!isFinite(num)) return String(value);
        if (Math.abs(num % 1) < 0.000001) return String(Math.trunc(num));
        return String(num).replace(/(\.\d*?[1-9])0+$/, '$1').replace(/\.0+$/, '');
    }

    function getMeasurementTableRows(layout) {
        var rows = [
            ['Front Height', formatMeasureNumber(layout.frontH) + ' ft'],
            ['Back Height', formatMeasureNumber(layout.backH) + ' ft'],
            ['Legs', formatMeasureNumber(layout.legs) + ' Nos.'],
            ['Rafters', formatMeasureNumber(layout.rafters) + ' Nos.'],
            ['Purlins', formatMeasureNumber(layout.purlins) + ' Nos.']
        ];
        if (layout.panelCount > 0) {
            rows.push([
                'Panels',
                formatMeasureNumber(layout.panelCount) + ' (' +
                formatMeasureNumber(layout.panelGrid.cols) + '\u00d7' +
                formatMeasureNumber(layout.panelGrid.rows) + ')'
            ]);
        }
        return rows;
    }

    function drawMeasurementTableTopRight(ctx, layout, x, y, tableW) {
        var rows = getMeasurementTableRows(layout);
        var rowH = 12;
        var headerH = 15;
        var pad = 5;
        var tableH = headerH + rows.length * rowH + pad;
        var i;
        var ry;

        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 1;
        ctx.fillRect(x, y, tableW, tableH);
        ctx.strokeRect(x + 0.5, y + 0.5, tableW - 1, tableH - 1);
        ctx.fillStyle = '#f1f5f9';
        ctx.fillRect(x + 1, y + 1, tableW - 2, headerH - 1);
        ctx.fillStyle = '#1f4e79';
        ctx.font = '700 9px Arial, sans-serif';
        ctx.textBaseline = 'middle';
        ctx.fillText('Measurements', x + pad, y + headerH / 2);

        ry = y + headerH + 2;
        for (i = 0; i < rows.length; i++) {
            ctx.strokeStyle = '#e2e8f0';
            ctx.beginPath();
            ctx.moveTo(x + 4, ry - 1);
            ctx.lineTo(x + tableW - 4, ry - 1);
            ctx.stroke();
            ctx.fillStyle = '#64748b';
            ctx.font = '9px Arial, sans-serif';
            ctx.textAlign = 'left';
            ctx.fillText(rows[i][0], x + pad, ry + rowH / 2);
            ctx.fillStyle = '#0f172a';
            ctx.font = '600 9px Arial, sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText(rows[i][1], x + tableW - pad, ry + rowH / 2);
            ry += rowH;
        }
        ctx.textAlign = 'left';
        return tableH;
    }

    function composeCaptureWithSummary(croppedCanvas, layout) {
        var tableW = 158;
        var gap = 14;
        var pad = 6;
        var scale = 0.64;
        var structW = Math.max(1, Math.round(croppedCanvas.width * scale));
        var structH = Math.max(1, Math.round(croppedCanvas.height * scale));
        var tableH = 15 + (layout.panelCount > 0 ? 6 : 5) * 12 + 8;
        var outW = pad + structW + gap + tableW + pad;
        var outH = Math.max(structH, tableH) + pad * 2;
        var out = document.createElement('canvas');
        out.width = outW;
        out.height = outH;
        var ctx = out.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, out.width, out.height);
        var structY = Math.round((outH - structH) / 2);
        var tableX = pad + structW + gap;
        var tableY = Math.round((outH - tableH) / 2);
        ctx.drawImage(croppedCanvas, 0, 0, croppedCanvas.width, croppedCanvas.height, pad, structY, structW, structH);
        drawMeasurementTableTopRight(ctx, layout, tableX, tableY, tableW);
        return out;
    }

    var solarPanelTextureCache = null;
    function getSolarPanelTexture() {
        if (solarPanelTextureCache) return solarPanelTextureCache;
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 256;
        ctx.fillStyle = '#0f1f33';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        var cols = 6;
        var rows = 12;
        var cw = canvas.width / cols;
        var ch = canvas.height / rows;
        var ry, cx, shade;
        for (ry = 0; ry < rows; ry++) {
            for (cx = 0; cx < cols; cx++) {
                shade = (ry + cx) % 2 === 0 ? '#1a3358' : '#122a47';
                ctx.fillStyle = shade;
                ctx.fillRect(cx * cw + 1.5, ry * ch + 1.5, cw - 3, ch - 3);
            }
        }
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.45)';
        ctx.lineWidth = 0.8;
        for (cx = 0; cx <= cols; cx++) {
            ctx.beginPath();
            ctx.moveTo(cx * cw, 0);
            ctx.lineTo(cx * cw, canvas.height);
            ctx.stroke();
        }
        for (ry = 0; ry <= rows; ry++) {
            ctx.beginPath();
            ctx.moveTo(0, ry * ch);
            ctx.lineTo(canvas.width, ry * ch);
            ctx.stroke();
        }
        ctx.strokeStyle = 'rgba(203, 213, 225, 0.55)';
        ctx.lineWidth = 2;
        ctx.strokeRect(2, 2, canvas.width - 4, canvas.height - 4);
        var tex = new THREE.CanvasTexture(canvas);
        tex.wrapS = THREE.RepeatWrapping;
        tex.wrapT = THREE.RepeatWrapping;
        tex.needsUpdate = true;
        solarPanelTextureCache = tex;
        return tex;
    }

    // Module size helpers are defined near the top (shared with layout + 3D).

    function fitPortraitPanelInBay(xL, yTop, xR, yBot) {
        var bayW = xR - xL;
        var bayH = yBot - yTop;
        if (bayW < 4 || bayH < 4) return null;
        var padX = Math.max(0.35, bayW * 0.004);
        var padY = Math.max(0.35, bayH * 0.004);
        return {
            x: xL + padX,
            y: yTop + padY,
            w: Math.max(3, bayW - padX * 2),
            h: Math.max(3, bayH - padY * 2)
        };
    }

    function buildSolarPanel3DGroup(panelW, panelLen, panelThick) {
        var group = new THREE.Group();
        // Exact module face — all panels share the same 4 ft × 8 ft size.
        var faceW = panelW;
        var faceL = panelLen;
        var panelTex = getSolarPanelTexture();
        var faceMat = new THREE.MeshPhongMaterial({
            map: panelTex,
            color: 0xdce7f5,
            shininess: 70,
            specular: 0x8899aa,
            emissive: 0x050a12,
            emissiveIntensity: 0.15
        });
        var face = new THREE.Mesh(new THREE.BoxGeometry(faceW, panelThick, faceL), faceMat);
        group.add(face);
        var frameMat = new THREE.MeshPhongMaterial({
            color: 0xc5ced8,
            shininess: 90,
            specular: 0xf1f5f9
        });
        var frameThick = 0.014;
        var frameH = panelThick + 0.01;
        var frameSpecs = [
            [faceW / 2 + frameThick / 2, 0, 0, frameThick, frameH, faceL + frameThick * 2],
            [-faceW / 2 - frameThick / 2, 0, 0, frameThick, frameH, faceL + frameThick * 2],
            [0, 0, faceL / 2 + frameThick / 2, faceW + frameThick * 2, frameH, frameThick],
            [0, 0, -faceL / 2 - frameThick / 2, faceW + frameThick * 2, frameH, frameThick]
        ];
        frameSpecs.forEach(function (f) {
            var frameMesh = new THREE.Mesh(new THREE.BoxGeometry(f[3], f[4], f[5]), frameMat);
            frameMesh.position.set(f[0], f[1], f[2]);
            group.add(frameMesh);
        });
        return group;
    }

    function solarPanelSvgDefs() {
        return '<pattern id="solarPvCells" width="10" height="10" patternUnits="userSpaceOnUse">' +
            '<rect width="10" height="10" fill="#0f1f33"/>' +
            '<rect x="0.5" y="0.5" width="4" height="4" fill="#1a3358"/>' +
            '<rect x="5.5" y="5.5" width="4" height="4" fill="#1a3358"/>' +
            '<rect x="5.5" y="0.5" width="4" height="4" fill="#122a47"/>' +
            '<rect x="0.5" y="5.5" width="4" height="4" fill="#122a47"/>' +
            '<line x1="0" y1="0" x2="10" y2="0" stroke="rgba(148,163,184,0.4)" stroke-width="0.35"/>' +
            '<line x1="0" y1="5" x2="10" y2="5" stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>' +
            '<line x1="0" y1="0" x2="0" y2="10" stroke="rgba(148,163,184,0.4)" stroke-width="0.35"/>' +
            '<line x1="5" y1="0" x2="5" y2="10" stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>' +
            '</pattern>' +
            '<filter id="planPanelShadow" x="-20%" y="-20%" width="140%" height="140%">' +
            '<feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="#0c1929" flood-opacity="0.3"/></filter>';
    }

    function svgSolarPanelGridLines(x, y, w, h) {
        var rows = Math.max(3, Math.min(12, Math.round(h / 8)));
        var ch = h / rows;
        var s = '';
        var i;
        for (i = 1; i < rows; i++) {
            s += '<line x1="' + x + '" y1="' + (y + i * ch) + '" x2="' + (x + w) + '" y2="' + (y + i * ch) +
                '" stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>';
        }
        return s;
    }

    function svgSolarPanelRect(x, y, w, h) {
        if (w < 3 || h < 3) return '';
        var frame = 2;
        var s = '';
        s += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h +
            '" fill="#c5ced8" stroke="#94a3b8" stroke-width="0.8" rx="1" filter="url(#planPanelShadow)"/>';
        var ix = x + frame;
        var iy = y + frame;
        var iw = w - frame * 2;
        var ih = h - frame * 2;
        if (iw > 2 && ih > 2) {
            s += '<rect x="' + ix + '" y="' + iy + '" width="' + iw + '" height="' + ih +
                '" fill="url(#solarPvCells)" stroke="#152238" stroke-width="0.5" rx="0.5"/>';
            s += svgSolarPanelGridLines(ix, iy, iw, ih);
        }
        return s;
    }

    function svgSolarPanelQuadPath(d) {
        return '<path d="' + d + '" fill="url(#solarPvCells)" stroke="#c5ced8" stroke-width="2.2" stroke-linejoin="round" filter="url(#planPanelShadow)"/>' +
            '<path d="' + d + '" fill="none" stroke="#152238" stroke-width="0.55" opacity="0.65"/>';
    }

    /* Side elevation: one solid panel band per row (between purlin pairs). */
    function svgSolarPanelSideSlab(bL0, bL1, up, profilePx) {
        var tL0 = { x: bL0.x + up.x * profilePx, y: bL0.y + up.y * profilePx };
        var tL1 = { x: bL1.x + up.x * profilePx, y: bL1.y + up.y * profilePx };
        var d = 'M' + bL0.x + ' ' + bL0.y + ' L' + bL1.x + ' ' + bL1.y + ' L' + tL1.x + ' ' + tL1.y + ' L' + tL0.x + ' ' + tL0.y + ' Z';
        return '<path d="' + d + '" fill="#1a3358" stroke="#152238" stroke-width="0.75" stroke-linejoin="round"/>' +
            '<line x1="' + tL0.x + '" y1="' + tL0.y + '" x2="' + tL1.x + '" y2="' + tL1.y + '" stroke="rgba(148,163,184,0.45)" stroke-width="0.5"/>';
    }

    function sidePanelUpUnit(panelUpNx, panelUpNy) {
        var len = Math.sqrt(panelUpNx * panelUpNx + panelUpNy * panelUpNy) || 1;
        return { x: panelUpNx / len, y: panelUpNy / len, len: len };
    }

    function sidePointLifted(sideOnRafter, panelUpNx, panelUpNy, t, liftAlongUp) {
        var pt = sideOnRafter(t);
        var up = sidePanelUpUnit(panelUpNx, panelUpNy);
        return {
            x: pt.x + up.x * liftAlongUp,
            y: pt.y + up.y * liftAlongUp
        };
    }

    function addSolarWalkwayAndLadder(scene, layout, xAtLeg, roofPoint, alignMemberAlong, depth, frontTopY, backTopY, foundationH) {
        if (!layout.hasWalkway) return;
        var rows = (layout.panelGrid && layout.panelGrid.rows) ? layout.panelGrid.rows : 0;
        var t0;
        var t1;
        if (rows >= 2) {
            t0 = panelRowDepthFrac(0, rows).t1;
            t1 = panelRowDepthFrac(1, rows).t0;
        } else {
            t0 = 0.38;
            t1 = 0.62;
        }
        if (t1 - t0 < 0.07) {
            var midGap = (t0 + t1) / 2;
            t0 = Math.max(0.2, midGap - 0.08);
            t1 = Math.min(0.8, midGap + 0.08);
        }
        var midT = (t0 + t1) / 2;
        var z0 = t0 * depth;
        var z1 = t1 * depth;
        var zMid = midT * depth;
        var roofAtGap = roofPoint(midT, 0.5).y;
        // Level height on the legs — clearly BELOW sloping panel rafters (marked attachment line).
        var walkY = Math.max(foundationH + 0.55, roofAtGap - 0.52);
        // Keep below the lower of front/back leg tops so members sit on the posts.
        walkY = Math.min(walkY, Math.min(frontTopY, backTopY) - 0.35);
        walkY = Math.max(walkY, foundationH + 0.45);
        var xLeft = xAtLeg(0);
        var xRight = xAtLeg(Math.max(layout.legCols - 1, 0));
        var axisY = new THREE.Vector3(0, 1, 0);
        var axisX = new THREE.Vector3(1, 0, 0);
        var axisZ = new THREE.Vector3(0, 0, 1);

        // --- 2 walkway rafters ATTACHED to LEFT + RIGHT legs (full front→back) ---
        var walkRafterMat = new THREE.MeshLambertMaterial({ color: 0xea580c });
        var legHalf = 0.07;
        [xLeft, xRight].forEach(function (x) {
            // Span through front leg (z=0) to back leg (z=depth) so ends sit in the posts.
            var a = new THREE.Vector3(x, walkY, -legHalf);
            var b = new THREE.Vector3(x, walkY, depth + legHalf);
            var len = a.distanceTo(b);
            if (len < 0.05) return;
            var mesh = new THREE.Mesh(new THREE.BoxGeometry(0.09, len, 0.09), walkRafterMat);
            alignMemberAlong(mesh, a, b, axisY);
            scene.add(mesh);
        });

        // --- Walkway grate RESTS on the 2 lower rafters (between panel rows) ---
        var deckW = Math.max(Math.abs(xRight - xLeft) * 0.92, 0.5);
        var deckD = Math.max(Math.abs(z1 - z0) * 0.95, 0.28);
        var deckY = walkY + 0.09;
        var plate = new THREE.Mesh(
            new THREE.BoxGeometry(deckW, 0.05, deckD),
            new THREE.MeshLambertMaterial({ color: 0xcbd5e1 })
        );
        plate.position.set((xLeft + xRight) / 2, deckY, zMid);
        scene.add(plate);

        var frameMat = new THREE.MeshLambertMaterial({ color: 0x1f2937 });
        var barMat = new THREE.MeshLambertMaterial({ color: 0x4b5563 });
        var cx = (xLeft + xRight) / 2;
        var ft = 0.045;
        [
            [0, deckD / 2, deckW + 0.02, ft, ft],
            [0, -deckD / 2, deckW + 0.02, ft, ft],
            [-deckW / 2, 0, ft, ft, deckD + 0.02],
            [deckW / 2, 0, ft, ft, deckD + 0.02]
        ].forEach(function (f) {
            var fm = new THREE.Mesh(new THREE.BoxGeometry(f[2], f[3], f[4]), frameMat);
            fm.position.set(cx + f[0], deckY + 0.032, zMid + f[1]);
            scene.add(fm);
        });
        var nLong = Math.max(10, Math.round(deckW / 0.09));
        var li;
        for (li = 1; li < nLong; li++) {
            var gx = -deckW / 2 + (deckW * li) / nLong;
            var bar = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.03, deckD * 0.92), barMat);
            bar.position.set(cx + gx, deckY + 0.036, zMid);
            scene.add(bar);
        }
        var nCross = Math.max(4, Math.round(deckD / 0.07));
        var cxi;
        for (cxi = 1; cxi < nCross; cxi++) {
            var gz = -deckD / 2 + (deckD * cxi) / nCross;
            var cbar = new THREE.Mesh(new THREE.BoxGeometry(deckW * 0.92, 0.026, 0.028), barMat);
            cbar.position.set(cx, deckY + 0.04, zMid + gz);
            scene.add(cbar);
        }

        // +4 walkway purlins across the deck.
        var walkPurlinMat = new THREE.MeshLambertMaterial({ color: 0x1d4ed8 });
        var wp;
        for (wp = 0; wp < 4; wp++) {
            var zt = z0 + (z1 - z0) * (wp + 0.5) / 4;
            var left = new THREE.Vector3(xLeft + 0.05, deckY - 0.02, zt);
            var right = new THREE.Vector3(xRight - 0.05, deckY - 0.02, zt);
            var pm = new THREE.Mesh(new THREE.BoxGeometry(left.distanceTo(right), 0.055, 0.075), walkPurlinMat);
            alignMemberAlong(pm, left, right, axisX);
            scene.add(pm);
        }

        if (!layout.hasLadder) return;

        // Ladder from GROUND up to walkway (gentle lean, rests on ground in front).
        var pipeN = Math.max(4, Math.min(layout.squarePipeCount || 8, 28));
        var railMat = new THREE.MeshLambertMaterial({ color: 0xb91c1c });
        var rungMat = new THREE.MeshLambertMaterial({ color: 0xdc2626 });
        var halfW = 0.18;
        var topX = xLeft + Math.max(deckW * 0.18, 0.35);
        var topZ = z0 + 0.02;
        var topY = deckY + 0.04;
        var botX = topX - 0.12;
        var botZ = -Math.max(0.35, depth * 0.08);
        var botY = 0.02;
        [
            new THREE.Vector3(-halfW, 0, 0),
            new THREE.Vector3(halfW, 0, 0)
        ].forEach(function (off) {
            var a = new THREE.Vector3(botX + off.x, botY, botZ);
            var b = new THREE.Vector3(topX + off.x, topY, topZ);
            var rail = new THREE.Mesh(new THREE.BoxGeometry(0.055, a.distanceTo(b), 0.055), railMat);
            alignMemberAlong(rail, a, b, axisY);
            scene.add(rail);
        });
        var ri;
        for (ri = 1; ri <= pipeN; ri++) {
            var u = ri / (pipeN + 1);
            var rung = new THREE.Mesh(new THREE.BoxGeometry(halfW * 2 + 0.06, 0.04, 0.04), rungMat);
            rung.position.set(
                botX + (topX - botX) * u,
                botY + (topY - botY) * u,
                botZ + (topZ - botZ) * u
            );
            scene.add(rung);
        }
    }

    function addSolar3DMeasurements(scene, layout, xAt, frontTopY, backTopY, depth, foundationH) {
        var dimColor = 0x16a34a;
        var dimMat = new THREE.LineBasicMaterial({ color: dimColor, linewidth: 2 });
        var capMat = new THREE.LineBasicMaterial({ color: dimColor });

        function addLine(a, b, mat) {
            var g = new THREE.BufferGeometry().setFromPoints([a, b]);
            scene.add(new THREE.Line(g, mat || dimMat));
        }
        function addCap(center, dir, half) {
            var p0 = center.clone().add(dir.clone().multiplyScalar(half));
            var p1 = center.clone().add(dir.clone().multiplyScalar(-half));
            addLine(p0, p1, capMat);
        }
        function addVerticalDim(x, z, yTop, label) {
            var y0 = foundationH * 0.5;
            var a = new THREE.Vector3(x, y0, z);
            var b = new THREE.Vector3(x, yTop, z);
            addLine(a, b);
            addCap(a, new THREE.Vector3(0, 0, 1), 0.14);
            addCap(b, new THREE.Vector3(0, 0, 1), 0.14);
            return createTextSprite(label, { color: '#16a34a', scaleX: 0.9, scaleY: 0.26, fontSize: 24 });
        }
        function createTextSprite(text, opts) {
            opts = opts || {};
            var fontPx = opts.fontSize || 22;
            var pad = 10;
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d', { alpha: true });
            ctx.font = '700 ' + fontPx + 'px Arial, sans-serif';
            var textW = Math.max(24, Math.ceil(ctx.measureText(String(text)).width));
            canvas.width = textW + pad * 2;
            canvas.height = fontPx + pad * 2;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            var textColor = opts.color || '#334155';
            ctx.font = '700 ' + fontPx + 'px Arial, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = textColor;
            ctx.fillText(String(text), canvas.width / 2, canvas.height / 2);
            var tex = new THREE.CanvasTexture(canvas);
            tex.premultiplyAlpha = false;
            tex.needsUpdate = true;
            var mat = new THREE.SpriteMaterial({
                map: tex,
                transparent: true,
                depthTest: false,
                depthWrite: false,
                alphaTest: 0.01
            });
            var spr = new THREE.Sprite(mat);
            // Scale from pixel aspect so full label (e.g. "6 ft") stays readable.
            var baseScaleX = opts.scaleX || 0.85;
            var aspect = canvas.width / Math.max(canvas.height, 1);
            spr.scale.set(baseScaleX, baseScaleX / aspect, 1);
            return spr;
        }

        var xL = xAt(0);
        var xR = xAt(1);
        var dimFrontX = xL - 0.7;
        var dimBackX = xR + 0.95;
        var sprFront = addVerticalDim(dimFrontX, 0, frontTopY, formatMeasureNumber(layout.frontH) + ' ft');
        sprFront.position.set(dimFrontX - 0.55, (foundationH + frontTopY) / 2, 0);
        scene.add(sprFront);
        var sprBack = addVerticalDim(dimBackX, depth, backTopY, formatMeasureNumber(layout.backH) + ' ft');
        sprBack.position.set(dimBackX + 0.55, (foundationH + backTopY) / 2, depth);
        scene.add(sprBack);

        var footY = 0.04;
        var wA = new THREE.Vector3(xL, footY, -0.2);
        var wB = new THREE.Vector3(xR, footY, -0.2);
        addLine(wA, wB);
        addCap(wA, new THREE.Vector3(0, 0, 1), 0.12);
        addCap(wB, new THREE.Vector3(0, 0, 1), 0.12);
        var widthLabel = formatMeasureNumber(layout.structureWidthFt || Math.round(Math.abs(xR - xL) / 0.09)) + ' ft';
        var sprWidth = createTextSprite(widthLabel, { color: '#16a34a', scaleX: 0.9, fontSize: 22 });
        sprWidth.position.set((xL + xR) / 2, footY + 0.02, -0.48);
        scene.add(sprWidth);

        var dA = new THREE.Vector3(xL - 0.55, footY, 0);
        var dB = new THREE.Vector3(xL - 0.55, footY, depth);
        addLine(dA, dB);
        addCap(dA, new THREE.Vector3(1, 0, 0), 0.12);
        addCap(dB, new THREE.Vector3(1, 0, 0), 0.12);
        var depthLabel = formatMeasureNumber(layout.structureDepthFt || Math.round(depth / 0.09)) + ' ft';
        var sprDepth = createTextSprite(depthLabel, { color: '#16a34a', scaleX: 0.9, fontSize: 20 });
        sprDepth.position.set(xL - 0.95, footY, depth / 2);
        scene.add(sprDepth);

        var rows = layout.panelGrid && layout.panelGrid.rows ? layout.panelGrid.rows : 0;
        var rowGapFt = layout.panelRowGapFt || SOLAR_PANEL_ROW_GAP_FT;
        if (rows > 1 && rowGapFt > 0) {
            var gapRi;
            for (gapRi = 0; gapRi < rows - 1; gapRi++) {
                var rowA = panelRowDepthFrac(gapRi, rows);
                var rowB = panelRowDepthFrac(gapRi + 1, rows);
                var zGap0 = rowA.t1 * depth;
                var zGap1 = rowB.t0 * depth;
                var gapX = xR + 0.42;
                var gA = new THREE.Vector3(gapX, footY, zGap0);
                var gB = new THREE.Vector3(gapX, footY, zGap1);
                addLine(gA, gB);
                addCap(gA, new THREE.Vector3(1, 0, 0), 0.1);
                addCap(gB, new THREE.Vector3(1, 0, 0), 0.1);
                var sprGap = createTextSprite(formatMeasureNumber(rowGapFt) + ' ft', { color: '#0369a1', scaleX: 0.78, fontSize: 18 });
                sprGap.position.set(gapX + 0.38, footY + 0.08, (zGap0 + zGap1) / 2);
                scene.add(sprGap);
            }
        }

        var sprFrontLbl = createTextSprite('FRONT', { color: '#16a34a', scaleX: 0.68, fontSize: 22 });
        sprFrontLbl.position.set((xL + xR) / 2, footY, -0.82);
        scene.add(sprFrontLbl);
        var sprBackLbl = createTextSprite('BACK', { color: '#16a34a', scaleX: 0.65, fontSize: 22 });
        sprBackLbl.position.set((xL + xR) / 2, footY, depth + 0.55);
        scene.add(sprBackLbl);
    }

    function initSolarStructure3DView(viewportEl, layout) {
        disposeSolar3DView(viewportEl);
        if (typeof THREE === 'undefined') {
            viewportEl.innerHTML = '<p class="text-muted small p-3 mb-0">3D viewer could not load. Check your internet connection.</p>';
            return;
        }

        var dirsEl = null;
        if (!layout.embedMode) {
            dirsEl = document.createElement('div');
            dirsEl.className = 'solar-3d-overlay-dirs';
            dirsEl.innerHTML = '<span>↑</span> Height · <span>→</span> Width · <span>↕</span> Front→Back depth · scroll/+− zoom';
        }

        var zoomWrap = null;
        if (!layout.embedMode) {
            zoomWrap = document.createElement('div');
            zoomWrap.className = 'solar-3d-zoom-controls';
            zoomWrap.setAttribute('aria-label', '3D zoom controls');
            zoomWrap.innerHTML =
                '<button type="button" class="solar-3d-zoom-btn" data-solar-3d-zoom="in" title="Zoom in" aria-label="Zoom in">+</button>' +
                '<button type="button" class="solar-3d-zoom-btn" data-solar-3d-zoom="out" title="Zoom out" aria-label="Zoom out">−</button>';
            viewportEl.appendChild(zoomWrap);
            if (dirsEl) viewportEl.appendChild(dirsEl);
        }

        var hScale = 0.09;
        var foundationH = 0.1;
        var frontY = layout.frontH * hScale;
        var backY = layout.backH * hScale;
        var frontTopY = foundationH + frontY;
        var backTopY = foundationH + backY;
        var structureWidthFt = layout.structureWidthFt || Math.max(layout.panelGrid.cols, 1) * SOLAR_PANEL_WIDTH_FT;
        var structureDepthFt = layout.structureDepthFt || solarStructureDepthFt(layout.panelGrid.rows || 1);
        var totalWidth = Math.max(structureWidthFt * hScale, 0.6);
        var depth = Math.max(structureDepthFt * hScale, 0.6);
        var legCols = layout.legCols;

        function xAtFrac(frac) {
            return (frac - 0.5) * totalWidth;
        }
        function xAtLeg(c) {
            return legCols > 1 ? xAtFrac(c / (legCols - 1)) : 0;
        }
        function xAtRafter(r) {
            return layout.rafterCols > 1 ? xAtFrac(r / (layout.rafterCols - 1)) : 0;
        }
        function xAt(edge) {
            return xAtFrac(edge);
        }
        function roofPoint(tDepth, widthFrac) {
            var x = xAtFrac(widthFrac);
            var z = tDepth * depth;
            var y = frontTopY + (backTopY - frontTopY) * tDepth;
            return new THREE.Vector3(x, y, z);
        }

        function alignMemberAlong(mesh, start, end, localAxis) {
            var dir = new THREE.Vector3().subVectors(end, start);
            var len = dir.length();
            if (len < 0.001) return;
            mesh.position.copy(start).add(end).multiplyScalar(0.5);
            mesh.quaternion.setFromUnitVectors(localAxis, dir.normalize());
        }

        var scene = new THREE.Scene();
        scene.background = new THREE.Color(layout.embedMode ? 0xffffff : 0xf8fafc);

        var width = viewportEl.clientWidth || 480;
        var height = viewportEl.clientHeight || 380;
        var camera = new THREE.PerspectiveCamera(34, width / height, 0.05, 200);
        // preserveDrawingBuffer ensures reliable PNG capture for PDF export.
        var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.setSize(width, height);
        viewportEl.appendChild(renderer.domElement);

        var controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.minDistance = 1.2;
        controls.maxDistance = 14;
        controls.maxPolarAngle = Math.PI * 0.49;
        controls.minPolarAngle = Math.PI * 0.12;

        scene.add(new THREE.AmbientLight(0xffffff, 0.65));
        var sun = new THREE.DirectionalLight(0xffffff, 0.85);
        sun.position.set(4, 8, 6);
        scene.add(sun);
        var fill = new THREE.DirectionalLight(0xffffff, 0.35);
        fill.position.set(-5, 3, -2);
        scene.add(fill);

        if (!layout.embedMode) {
            var ground = new THREE.Mesh(
                new THREE.PlaneGeometry(12, 12),
                new THREE.MeshLambertMaterial({ color: 0xe2e8f0 })
            );
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = 0;
            scene.add(ground);
            scene.add(new THREE.GridHelper(10, 20, 0xcbd5e1, 0xe2e8f0));
        }

        var legMat = new THREE.MeshLambertMaterial({ color: 0x57534e });
        var rafterMat = new THREE.MeshLambertMaterial({ color: 0xea580c });
        var foundationW = 0.32;
        var foundationD = 0.28;
        var foundationMat = new THREE.MeshLambertMaterial({ color: 0x78716c });
        var purlinMat = new THREE.MeshLambertMaterial({ color: 0x2563eb });

        var c, r, p;
        for (c = 0; c < legCols; c++) {
            var legX = xAtLeg(c);
            if (c < layout.frontLegCount) {
                var fBase = new THREE.Mesh(new THREE.BoxGeometry(foundationW, foundationH, foundationD), foundationMat);
                fBase.position.set(legX, foundationH / 2, 0);
                scene.add(fBase);
                var fLeg = new THREE.Mesh(new THREE.BoxGeometry(0.14, frontY, 0.14), legMat);
                fLeg.position.set(legX, foundationH + frontY / 2, 0);
                scene.add(fLeg);
            }
            if (c < layout.backLegCount) {
                var bBase = new THREE.Mesh(new THREE.BoxGeometry(foundationW, foundationH, foundationD), foundationMat);
                bBase.position.set(legX, foundationH / 2, depth);
                scene.add(bBase);
                var bLeg = new THREE.Mesh(new THREE.BoxGeometry(0.14, backY, 0.14), legMat);
                bLeg.position.set(legX, foundationH + backY / 2, depth);
                scene.add(bLeg);
            }
        }

        var axisY = new THREE.Vector3(0, 1, 0);
        var axisX = new THREE.Vector3(1, 0, 0);
        for (r = 0; r < layout.rafterCols; r++) {
            var raftX = xAtRafter(r);
            var pFront = new THREE.Vector3(raftX, frontTopY, 0);
            var pBack = new THREE.Vector3(raftX, backTopY, depth);
            var rafterLen = pFront.distanceTo(pBack);
            var rafterMesh = new THREE.Mesh(new THREE.BoxGeometry(0.12, rafterLen, 0.12), rafterMat);
            alignMemberAlong(rafterMesh, pFront, pBack, axisY);
            scene.add(rafterMesh);
        }

        for (p = 0; p < (layout.panelPurlins || layout.purlins); p++) {
            var t = layout.purlinT(p);
            var purlinLeft = roofPoint(t, 0);
            var purlinRight = roofPoint(t, 1);
            purlinLeft.y += 0.05;
            purlinRight.y += 0.05;
            var purlinLen = purlinLeft.distanceTo(purlinRight);
            var purlinMesh = new THREE.Mesh(new THREE.BoxGeometry(purlinLen, 0.08, 0.14), purlinMat);
            alignMemberAlong(purlinMesh, purlinLeft, purlinRight, axisX);
            scene.add(purlinMesh);
        }

        var panelThick = 0.032;
        var panelLift = 0.095;
        var row3d, col3d, idx3d, u0, u1, t0, t1;
        var pA, pB, pC, pD, panelGroup, panelFront, panelBack, faceW, faceL;
        var cols3d = Math.max(layout.panelGrid.cols, 1);
        var rows3d = Math.max(layout.panelGrid.rows, 1);

        for (row3d = 0; row3d < layout.panelGrid.rows; row3d++) {
            var rowFrac = panelRowDepthFrac(row3d, rows3d);
            t0 = rowFrac.t0;
            t1 = rowFrac.t1;
            for (col3d = 0; col3d < layout.panelGrid.cols; col3d++) {
                idx3d = row3d * layout.panelGrid.cols + col3d;
                if (idx3d >= layout.panelCount) continue;
                u0 = col3d / cols3d;
                u1 = (col3d + 1) / cols3d;
                pA = roofPoint(t0, u0);
                pB = roofPoint(t0, u1);
                pC = roofPoint(t1, u1);
                pD = roofPoint(t1, u0);
                panelFront = pA.clone().add(pB).multiplyScalar(0.5);
                panelBack = pC.clone().add(pD).multiplyScalar(0.5);
                panelFront.y += panelLift;
                panelBack.y += panelLift;
                if (panelFront.distanceTo(panelBack) < 0.001) continue;
                faceW = Math.max(pA.distanceTo(pB) * 0.998, 0.05);
                faceL = Math.max(panelFront.distanceTo(panelBack) * 0.998, 0.05);
                panelGroup = buildSolarPanel3DGroup(faceW, faceL, panelThick);
                alignMemberAlong(panelGroup, panelFront, panelBack, new THREE.Vector3(0, 0, 1));
                scene.add(panelGroup);
            }
        }

        addSolarWalkwayAndLadder(scene, layout, xAtLeg, roofPoint, alignMemberAlong, depth, frontTopY, backTopY, foundationH);
        addSolar3DMeasurements(scene, layout, xAt, frontTopY, backTopY, depth, foundationH);

        setSolar3DFrontView(camera, controls, layout, xAt, frontTopY, backTopY, depth);

        var zoomScale = 1.12;
        if (zoomWrap && !layout.embedMode) {
            zoomWrap.addEventListener('click', function (e) {
                var btn = e.target.closest('[data-solar-3d-zoom]');
                if (!btn) return;
                e.preventDefault();
                e.stopPropagation();
                var action = btn.getAttribute('data-solar-3d-zoom');
                if (action === 'in' && typeof controls.dollyIn === 'function') {
                    controls.dollyIn(zoomScale);
                } else if (action === 'out' && typeof controls.dollyOut === 'function') {
                    controls.dollyOut(zoomScale);
                } else {
                    var offset = new THREE.Vector3().subVectors(camera.position, controls.target);
                    var dist = offset.length();
                    if (action === 'in') {
                        dist = Math.max(controls.minDistance, dist / zoomScale);
                    } else {
                        dist = Math.min(controls.maxDistance, dist * zoomScale);
                    }
                    offset.setLength(dist);
                    camera.position.copy(controls.target).add(offset);
                }
                controls.update();
            });
        }

        var state = {
            renderer: renderer,
            controls: controls,
            scene: scene,
            camera: camera,
            layout: layout,
            rafId: null,
            applyFrontView: function () {
                setSolar3DFrontView(camera, controls, layout, xAt, frontTopY, backTopY, depth);
            },
            zoomIn: function () {
                if (typeof controls.dollyIn === 'function') controls.dollyIn(zoomScale);
                controls.update();
            },
            zoomOut: function () {
                if (typeof controls.dollyOut === 'function') controls.dollyOut(zoomScale);
                controls.update();
            }
        };

        function animate() {
            state.rafId = requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        function onResize() {
            var w = viewportEl.clientWidth || 480;
            var h = viewportEl.clientHeight || 380;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        }
        if (typeof ResizeObserver !== 'undefined') {
            state.resizeObserver = new ResizeObserver(onResize);
            state.resizeObserver.observe(viewportEl);
        } else {
            window.addEventListener('resize', onResize);
        }
        viewportEl._solar3dState = state;
        setTimeout(onResize, 0);
        setTimeout(onResize, 250);
    }

    function renderSolarStructureDiagram(container, opts) {
        if (!container) return;
        var legs = parseInt(opts.legs, 10) || 0;
        var rafters = parseInt(opts.rafters, 10) || 0;
        var purlins = parseInt(opts.purlins, 10) || 0;
        var solarPanels = parseInt(opts.solarPanels, 10);
        var frontH = parseFloat(opts.frontHeight);
        var backH = parseFloat(opts.backHeight);
        if (legs < 1 || rafters < 1 || purlins < 1) {
            container.innerHTML = '';
            return;
        }
        frontH = isNaN(frontH) ? 0 : frontH;
        backH = isNaN(backH) ? 0 : backH;
        var maxH = Math.max(frontH, backH, 1);
        var frontPx = 22 + (frontH / maxH) * 72;
        var backPx = 22 + (backH / maxH) * 72;

        var frontLegCount = Math.ceil(legs / 2);
        var backLegCount = Math.floor(legs / 2);
        var legCols = Math.max(frontLegCount, backLegCount, 1);
        var rafterCols = rafters;
        var spanCols = Math.max(legCols, rafterCols);
        var panelCount = isNaN(solarPanels) || solarPanels < 1 ? 0 : solarPanels;
        /* Rows = purlin pairs (frontâ†’back); cols = panels per row from total count */
        var panelRowsFromPurlins = Math.max(1, Math.floor(purlins / 2));
        var panelColsWidth = panelCount > 0 ? Math.max(1, Math.ceil(panelCount / panelRowsFromPurlins)) : 0;
        var panelGrid = panelCount > 0 ? {
            rows: panelRowsFromPurlins,
            cols: panelColsWidth,
            total: panelCount
        } : { rows: 0, cols: 0, total: 0 };

        function purlinT(index) {
            return purlins === 1 ? 0.5 : index / (purlins - 1);
        }

        /* Row 0 â†’ P1+P2; row 1 â†’ P3+P4; portrait panel extends slightly past both purlins. */
        function panelDepthSpan(row) {
            var p0 = row * 2;
            var p1 = p0 + 1;
            if (p0 >= purlins) {
                return { t0: row / panelGrid.rows, t1: (row + 1) / panelGrid.rows, p0: -1, p1: -1 };
            }
            if (p1 >= purlins) p1 = purlins - 1;
            if (p0 === p1 && p0 > 0) p0 = p0 - 1;
            var tA = purlinT(p0);
            var tB = purlinT(p1);
            return { t0: Math.min(tA, tB), t1: Math.max(tA, tB), p0: p0, p1: p1 };
        }

        function panelPortraitSpan(row) {
            var mount = panelDepthSpan(row);
            var gap = mount.t1 - mount.t0 || 0.15;
            var overhang = Math.max(gap * 0.24, 0.035);
            var t0 = Math.max(0, mount.t0 - overhang);
            var t1 = Math.min(1, mount.t1 + overhang);
            if (row > 0) {
                var prev = panelDepthSpan(row - 1);
                t0 = Math.max(t0, prev.t1 + 0.012);
            }
            if (row < panelGrid.rows - 1) {
                var next = panelDepthSpan(row + 1);
                t1 = Math.min(t1, next.t0 - 0.012);
            }
            return {
                t0: t0,
                t1: t1,
                mountT0: mount.t0,
                mountT1: mount.t1,
                p0: mount.p0,
                p1: mount.p1
            };
        }

        function panelVisualSpan(row) {
            return panelPortraitSpan(row);
        }

        var PURLIN_ON_RAFTER = 4;
        var PURLIN_TOP_3D = 6;

        function rafterBayCol(r) {
            if (rafterCols <= 1) return 0;
            if (legCols === rafterCols) return r;
            return Math.round(r * (legCols - 1) / (rafterCols - 1));
        }

        function drawAllPanelCells(drawFn) {
            var row, col, idx, visual;
            for (row = 0; row < panelGrid.rows; row++) {
                visual = panelVisualSpan(row);
                for (col = 0; col < panelGrid.cols; col++) {
                    idx = row * panelGrid.cols + col;
                    if (idx >= panelCount) continue;
                    drawFn(
                        visual.t0,
                        visual.t1,
                        col / panelGrid.cols,
                        (col + 1) / panelGrid.cols,
                        'M' + (idx + 1),
                        row,
                        visual
                    );
                }
            }
        }

        var svg = '';
        var c, r, p, bay;

        svg += '<defs><marker id="planArrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#64748b"/></marker>' +
            solarPanelSvgDefs() + '</defs>';
        // Remove the inner â€œcardâ€ rectangle so the background looks merged and we don't create extra margins.
        svg += '<rect x="0" y="34" width="280" height="318" fill="#fff" stroke="none" rx="0"/>';

        /* ========== Plan view (top) ========== */
        var px0 = 8, py0 = 48, pw = 264, pd = 118;
        var structWft = Math.max(1, panelGrid.cols || 1) * 4;
        var structDft = Math.max(1, panelGrid.rows || 1) * 8;
        svg += '<text x="138" y="46" text-anchor="middle" font-size="12" font-weight="600" fill="#1e293b">Plan view (top)</text>';
        var planPad = 2;
        var availW = pw - planPad * 2;
        var availH = pd - 32;
        var footprintAspect = structDft / structWft;
        var drawW = availW;
        var drawH = drawW * footprintAspect;
        if (drawH > availH) {
            drawH = availH;
            drawW = drawH / footprintAspect;
        }
        var planInnerL = px0 + planPad + (availW - drawW) / 2;
        var planInnerR = planInnerL + drawW;
        var planBackY = py0 + 16 + (availH - drawH) / 2;
        var planFrontY = planBackY + drawH;
        var planDepthSpan = planFrontY - planBackY;
        var planUGap = 0;
        var planRowGap = 0;

        var planXAt = function (col, total) {
            return planInnerL + (total > 1 ? (planInnerR - planInnerL) * col / (total - 1) : (planInnerR - planInnerL) / 2);
        };
        var planPurlinY = function (idx) {
            return purlins === 1 ? (planFrontY + planBackY) / 2 : planBackY + (planDepthSpan * idx / (purlins - 1));
        };

        svg += '<rect x="' + planInnerL + '" y="' + planBackY + '" width="' + (planInnerR - planInnerL) + '" height="' + planDepthSpan +
            '" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1" rx="2"/>';
        for (var g = 1; g < 4; g++) {
            var gx = planInnerL + (planInnerR - planInnerL) * g / 4;
            var gy = planBackY + planDepthSpan * g / 4;
            svg += '<line x1="' + gx + '" y1="' + planBackY + '" x2="' + gx + '" y2="' + planFrontY + '" stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="2,4"/>';
            svg += '<line x1="' + planInnerL + '" y1="' + gy + '" x2="' + planInnerR + '" y2="' + gy + '" stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="2,4"/>';
        }

        function drawPlanLegFoundation(lx, ly) {
            var fw = 22, fd = 12;
            svg += '<rect x="' + (lx - fw / 2) + '" y="' + (ly - fd / 2) + '" width="' + fw + '" height="' + fd +
                '" fill="#78716c" stroke="#44403c" stroke-width="1" rx="2"/>';
            svg += '<rect x="' + (lx - 5) + '" y="' + (ly - 4) + '" width="10" height="8" fill="#57534e" stroke="#44403c" stroke-width="0.6" rx="1"/>';
        }
        for (c = 0; c < legCols; c++) {
            var lx = planXAt(c, legCols);
            if (c < frontLegCount) {
                drawPlanLegFoundation(lx, planFrontY);
            }
            if (c < backLegCount) {
                drawPlanLegFoundation(lx, planBackY);
            }
        }
        for (r = 0; r < rafterCols; r++) {
            var rcx = planXAt(r, rafterCols);
            svg += '<line x1="' + rcx + '" y1="' + (planFrontY + 2) + '" x2="' + rcx + '" y2="' + (planBackY - 2) +
                '" stroke="#ea580c" stroke-width="5" stroke-linecap="round" opacity="0.95"/>';
        }
        for (p = 0; p < purlins; p++) {
            var py = planPurlinY(p);
            svg += '<rect x="' + planInnerL + '" y="' + (py - 5) + '" width="' + (planInnerR - planInnerL) + '" height="10" fill="#2563eb" stroke="#1d4ed8" stroke-width="0.8" rx="1" opacity="0.9"/>';
            if (purlins <= 6) {
                svg += '<text x="' + (planInnerR + 4) + '" y="' + (py + 3) + '" font-size="6" fill="#1e40af">P' + (p + 1) + '</text>';
            }
        }
        drawAllPanelCells(function (t0, t1, u0, u1, label, row, visual) {
            var t0eq = row / Math.max(panelGrid.rows, 1);
            var t1eq = (row + 1) / Math.max(panelGrid.rows, 1);
            var yTop = planBackY + planDepthSpan * t0eq + (row > 0 ? planRowGap / 2 : 0);
            var yBot = planBackY + planDepthSpan * t1eq - (row < panelGrid.rows - 1 ? planRowGap / 2 : 0);
            var xL = planInnerL + (planInnerR - planInnerL) * u0 + planUGap;
            var xR = planInnerL + (planInnerR - planInnerL) * u1 - planUGap;
            var fitted = fitPortraitPanelInBay(xL, yTop, xR, yBot);
            if (!fitted) return;
            svg += svgSolarPanelRect(fitted.x, fitted.y, fitted.w, fitted.h);
            if (panelCount <= 12) {
                svg += '<text x="' + (fitted.x + fitted.w / 2) + '" y="' + (fitted.y + fitted.h / 2 + 4) + '" text-anchor="middle" font-size="' +
                    (panelGrid.cols > 4 ? 6 : 7) + '" fill="#e2e8f0" font-weight="600" stroke="#0f1f33" stroke-width="0.4">' + label + '</text>';
            }
        });
        for (r = 0; r < rafterCols && rafterCols <= 4; r++) {
            var rlx = planXAt(r, rafterCols);
            svg += '<text x="' + rlx + '" y="' + (planFrontY + 14) + '" text-anchor="middle" font-size="7" fill="#c2410c" font-weight="600">R' + (r + 1) + '</text>';
        }
        svg += '<text x="' + ((planInnerL + planInnerR) / 2) + '" y="' + (planFrontY + 12) + '" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">FRONT</text>';
        svg += '<text x="' + ((planInnerL + planInnerR) / 2) + '" y="' + (planBackY - 6) + '" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">BACK</text>';
        svg += '<line x1="' + ((planInnerL + planInnerR) / 2) + '" y1="' + (planFrontY + 16) + '" x2="' + ((planInnerL + planInnerR) / 2) + '" y2="' + (planBackY - 8) +
            '" stroke="#64748b" stroke-width="1" marker-end="url(#planArrow)"/>';
        svg += '<line x1="' + planInnerL + '" y1="' + (py0 + pd / 2) + '" x2="' + planInnerR + '" y2="' + (py0 + pd / 2) +
            '" stroke="#64748b" stroke-width="1" marker-end="url(#planArrow)"/>';
        svg += '<text x="' + (planInnerR + 2) + '" y="' + (py0 + pd / 2 + 3) + '" font-size="7" fill="#64748b">Width â†’</text>';
        if (panelCount > 0) {
            svg += '<text x="' + ((planInnerL + planInnerR) / 2) + '" y="' + (py0 + 6) + '" text-anchor="middle" font-size="7" fill="#0369a1">' +
                panelCount + ' panels Â· ' + panelGrid.cols + ' wide Ã— ' + panelGrid.rows + ' deep</text>';
        }

        /* ========== Side elevation (purlins âŠ¥ rafter; panels between purlin pairs) ========== */
        // Side elevation: slightly widen to match enlarged plan view
        var sideMid = 140;
        var sgy = 318;
        var rfX = 86, rbX = 194;
        var sfTop = sgy - frontPx, sbTop = sgy - backPx;
        var rdx = rbX - rfX, rdy = sbTop - sfTop;
        var rLen = Math.sqrt(rdx * rdx + rdy * rdy) || 1;
        /* Panel above rafter (sky side); purlin = square pipe (side profile) */
        var tangX = (rdx / rLen) * 7;
        var tangY = (rdy / rLen) * 7;
        var normX = (-rdy / rLen) * 7;
        var normY = (rdx / rLen) * 7;
        var panelUpNx = (rdy / rLen) * 18;
        var panelUpNy = (-rdx / rLen) * 18;
        var panelThickNx = (rdy / rLen) * 6;
        var panelThickNy = (-rdx / rLen) * 6;

        function sideOnRafter(t) {
            return { x: rfX + rdx * t, y: sfTop + rdy * t };
        }

        svg += '<text x="' + sideMid + '" y="180" text-anchor="middle" font-size="12" font-weight="600" fill="#1e293b">Side elevation</text>';
        svg += '<line x1="48" y1="' + sgy + '" x2="228" y2="' + sgy + '" stroke="#94a3b8" stroke-width="2"/>';
        var sideFoundH = 12;
        svg += '<rect x="' + (rfX - 16) + '" y="' + (sgy - sideFoundH) + '" width="32" height="' + sideFoundH +
            '" fill="#78716c" stroke="#44403c" stroke-width="1" rx="1"/>';
        svg += '<rect x="' + (rbX - 16) + '" y="' + (sgy - sideFoundH) + '" width="32" height="' + sideFoundH +
            '" fill="#78716c" stroke="#44403c" stroke-width="1" rx="1"/>';
        svg += '<text x="54" y="' + (sgy - 2) + '" font-size="6" fill="#57534e">Foundation</text>';
        svg += '<rect x="88" y="' + sfTop + '" width="8" height="' + (sgy - sideFoundH - sfTop) + '" fill="#64748b"/>';
        svg += '<rect x="172" y="' + sbTop + '" width="8" height="' + (sgy - sideFoundH - sbTop) + '" fill="#64748b"/>';
        svg += '<line x1="' + rfX + '" y1="' + sfTop + '" x2="' + rbX + '" y2="' + sbTop + '" stroke="#ea580c" stroke-width="4"/>';

        function drawSideCChannel(pt, label) {
            var bx = pt.x, by = pt.y;
            var lip = 11;
            svg += '<path d="M' + bx + ' ' + by +
                ' L' + (bx + tangX) + ' ' + (by + tangY) +
                ' L' + (bx + tangX + panelUpNx * 0.4) + ' ' + (by + tangY + panelUpNy * 0.4 - lip) +
                ' L' + (bx - tangX + panelUpNx * 0.4) + ' ' + (by - tangY + panelUpNy * 0.4 - lip) +
                ' L' + (bx - tangX) + ' ' + (by - tangY) + ' Z" fill="#93c5fd" stroke="#1d4ed8" stroke-width="1.2"/>';
            svg += '<line x1="' + (bx + tangX + panelUpNx * 0.4) + '" y1="' + (by + tangY + panelUpNy * 0.4 - lip) +
                '" x2="' + (bx - tangX + panelUpNx * 0.4) + '" y2="' + (by - tangY + panelUpNy * 0.4 - lip) +
                '" stroke="#1e40af" stroke-width="1.5"/>';
            if (label) {
                svg += '<text x="' + (bx + panelUpNx * 0.5 + 8) + '" y="' + (by + panelUpNy * 0.5) + '" font-size="7" fill="#1d4ed8">' + label + '</text>';
            }
        }
        var sidePurlinTopLift = PURLIN_ON_RAFTER + PURLIN_TOP_3D;
        var sidePanelBaseLift = sidePurlinTopLift + 3;
        var sidePanelEdgeThickPx = 2.2;
        var sidePanelProfilePx = 14;
        var tangLen = Math.sqrt(tangX * tangX + tangY * tangY) || 1;
        var tux = tangX / tangLen;
        var tuy = tangY / tangLen;

        function sidePointOnPurlinTop(t) {
            return sidePointLifted(sideOnRafter, panelUpNx, panelUpNy, t, sidePurlinTopLift);
        }
        function sidePointOnPanelBottom(t) {
            return sidePointLifted(sideOnRafter, panelUpNx, panelUpNy, t, sidePanelBaseLift);
        }

        function drawSidePanelRow(sideRow) {
            var mount = panelPortraitSpan(sideRow);
            var up = sidePanelUpUnit(panelUpNx, panelUpNy);
            var b0 = sidePointOnPanelBottom(mount.t0);
            var b1 = sidePointOnPanelBottom(mount.t1);
            var cols = panelGrid.cols;
            var rowStartIdx = sideRow * cols;
            var halfT = sidePanelEdgeThickPx / 2;
            var bL0 = { x: b0.x - tux * halfT, y: b0.y - tuy * halfT };
            var bL1 = { x: b1.x - tux * halfT, y: b1.y - tuy * halfT };

            svg += svgSolarPanelSideSlab(bL0, bL1, up, sidePanelProfilePx);

            if (panelCount <= 12) {
                var sideLabelStart = rowStartIdx + 1;
                var sideLabelEnd = Math.min(rowStartIdx + cols, panelCount);
                var sideLabel = sideLabelStart === sideLabelEnd ? 'M' + sideLabelStart : 'M' + sideLabelStart + '\u2013M' + sideLabelEnd;
                var lx = (b0.x + b1.x) / 2 + up.x * (sidePanelProfilePx * 0.45);
                var ly = (b0.y + b1.y) / 2 + up.y * (sidePanelProfilePx * 0.45);
                svg += '<text x="' + lx + '" y="' + ly + '" text-anchor="middle" font-size="6" fill="#e2e8f0" font-weight="600" stroke="#0f1f33" stroke-width="0.35">' + sideLabel + '</text>';
            }
        }

        for (var sideRow = 0; sideRow < panelGrid.rows; sideRow++) {
            drawSidePanelRow(sideRow);
        }
        for (p = 0; p < purlins; p++) {
            drawSideCChannel(sideOnRafter(purlinT(p)), 'P' + (p + 1));
        }
        svg += '<text x="52" y="170" font-size="7" fill="#1d4ed8">âŠ C-channel purlin</text>';
        svg += '<line x1="52" y1="' + sfTop + '" x2="52" y2="' + sgy + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<line x1="48" y1="' + sfTop + '" x2="56" y2="' + sfTop + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<line x1="48" y1="' + sgy + '" x2="56" y2="' + sgy + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<text x="38" y="' + ((sgy + sfTop) / 2) + '" font-size="9" fill="#16a34a" text-anchor="end">' + (frontH || 'â€”') + ' ft</text>';
        svg += '<line x1="212" y1="' + sbTop + '" x2="212" y2="' + sgy + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<line x1="208" y1="' + sbTop + '" x2="216" y2="' + sbTop + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<line x1="208" y1="' + sgy + '" x2="216" y2="' + sgy + '" stroke="#16a34a" stroke-width="1"/>';
        svg += '<text x="222" y="' + ((sgy + sbTop) / 2) + '" font-size="9" fill="#16a34a">' + (backH || 'â€”') + ' ft</text>';
        svg += '<line x1="60" y1="' + (sgy + 6) + '" x2="216" y2="' + (sgy + 6) + '" stroke="#64748b" stroke-width="1" marker-end="url(#planArrow)"/>';
        svg += '<text x="138" y="' + (sgy + 18) + '" text-anchor="middle" font-size="7" fill="#64748b">Front â†’ Back</text>';
        svg += '<text x="' + rfX + '" y="' + (sgy + 14) + '" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">FRONT</text>';
        svg += '<text x="' + rbX + '" y="' + (sgy + 14) + '" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">BACK</text>';

        var layout3d = buildSolarStructureLayout(opts);
        var summaryHtml = '<strong>Front ' + (frontH || 'â€”') + ' ft</strong> Â· <strong>Back ' + (backH || 'â€”') + ' ft</strong>';
        if (panelCount > 0) {
            summaryHtml += '<br>Panels ' + panelCount + ' (' + panelGrid.cols + 'Ã—' + panelGrid.rows + ') Â· Purlin ' + purlins + ' Â· Rafter ' + rafters;
        } else {
            summaryHtml += '<br>Purlin ' + purlins + ' Â· Rafter ' + rafters;
        }

        var legendSvg =
            '<svg viewBox="0 0 820 36" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Structure legend">' +
            '<rect x="0" y="0" width="820" height="36" rx="4" fill="#fff" stroke="#e2e8f0"/>' +
            '<rect x="10" y="11" width="12" height="8" fill="#78716c"/><text x="26" y="22" font-size="9" fill="#334155">Foundation + leg Ã—' + legs + '</text>' +
            '<line x1="188" y1="18" x2="212" y2="10" stroke="#ea580c" stroke-width="3"/><text x="220" y="22" font-size="9" fill="#334155">Rafter Ã—' + rafters + '</text>' +
            '<line x1="298" y1="18" x2="322" y2="18" stroke="#2563eb" stroke-width="3"/><text x="330" y="22" font-size="9" fill="#334155">C-purlin Ã—' + purlins + '</text>' +
            '<rect x="408" y="11" width="22" height="14" fill="#c5ced8" stroke="#94a3b8" stroke-width="0.6" rx="1"/>' +
            '<rect x="411" y="14" width="16" height="8" fill="#1a3358" stroke="#152238" stroke-width="0.5" rx="0.5"/>' +
            '<text x="434" y="22" font-size="9" fill="#334155">Panel Ã—' + panelCount +
            (panelCount > 0 ? ' (' + panelGrid.cols + 'Ã—' + panelGrid.rows + ')' : '') + '</text>' +
            '</svg>';

        var oldViewport = container.querySelector('.solar-3d-viewport');
        if (oldViewport) disposeSolar3DView(oldViewport);
        container.innerHTML =
            '<div class="solar-diagram-composite">' +
            '<div class="solar-diagram-2d-wrap">' +
            '<svg viewBox="0 0 280 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Plan and side elevation">' +
            '<rect x="0" y="0" width="280" height="400" fill="#ffffff" rx="6"/>' +
            svg +
            '</svg></div>' +
            '<div class="solar-diagram-3d-wrap">' +
            '<div class="solar-3d-title">3D structure <span class="solar-3d-hint">â€” drag to rotate 360Â°, scroll to zoom</span></div>' +
            '<div class="solar-3d-stage">' +
            '<div class="solar-3d-viewport" role="img" aria-label="Interactive 3D solar structure"></div>' +
            '</div>' +
            '<div class="solar-3d-summary" aria-hidden="true">' + summaryHtml + '</div>' +
            '</div></div>' +
            '<div class="solar-diagram-legend">' + legendSvg + '</div>';

        var viewport = container.querySelector('.solar-3d-viewport');
        if (viewport) {
            initSolarStructure3DView(viewport, layout3d);
        }
    }

    window.renderSolarStructureDiagram = renderSolarStructureDiagram;

    window.captureSolar3DFrontPng = function () {
        var vp = document.querySelector('.solar-3d-viewport');
        var st = vp && vp._solar3dState;
        if (!st || !st.renderer || !st.camera) {
            return '';
        }
        if (typeof st.applyFrontView === 'function') {
            st.applyFrontView();
        }
        st.controls.update();
        st.renderer.render(st.scene, st.camera);
        try {
            var src = st.renderer.domElement;
            var layout = st.layout || {};
            var raw = document.createElement('canvas');
            raw.width = src.width;
            raw.height = src.height;
            var rawCtx = raw.getContext('2d');
            rawCtx.fillStyle = '#ffffff';
            rawCtx.fillRect(0, 0, raw.width, raw.height);
            rawCtx.drawImage(src, 0, 0);

            var bounds = findCanvasContentBounds(rawCtx, raw.width, raw.height);
            var cropped = document.createElement('canvas');
            cropped.width = bounds.w;
            cropped.height = bounds.h;
            cropped.getContext('2d').drawImage(
                raw,
                bounds.x, bounds.y, bounds.w, bounds.h,
                0, 0, bounds.w, bounds.h
            );

            var finalCanvas = composeCaptureWithSummary(cropped, layout);
            return finalCanvas.toDataURL('image/png');
        } catch (err) {
            return '';
        }
    };
