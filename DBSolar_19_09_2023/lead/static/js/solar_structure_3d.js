/* Solar structure 3D viewer (survey detail + report PDF capture) */
(function (global) {
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
    var panelRowsFromPurlins = Math.max(1, Math.floor(purlins / 2));
    var panelColsWidth = panelCount > 0 ? Math.max(1, Math.ceil(panelCount / panelRowsFromPurlins)) : 0;
    var panelGrid = panelCount > 0 ? {
        rows: panelRowsFromPurlins,
        cols: panelColsWidth,
        total: panelCount
    } : { rows: 0, cols: 0, total: 0 };

    var PANEL_WIDTH_FT = 4;
    var PANEL_LENGTH_FT = 8;
    var structureWidthFt = panelGrid.cols > 0
        ? panelGrid.cols * PANEL_WIDTH_FT
        : Math.max(legCols - 1, 1) * PANEL_WIDTH_FT;
    var structureDepthFt = panelGrid.rows > 0
        ? panelGrid.rows * PANEL_LENGTH_FT
        : PANEL_LENGTH_FT;

    function purlinT(index) {
        return purlins === 1 ? 0.5 : index / (purlins - 1);
    }
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
        structureWidthFt: structureWidthFt,
        structureDepthFt: structureDepthFt,
        purlinT: purlinT,
        panelDepthSpan: panelDepthSpan,
        panelPortraitSpan: panelPortraitSpan,
        rafterBayCol: rafterBayCol
    };
}

function build3dSummaryOverlayHtml(layout) {
    var html = '<span class="solar-3d-summary-title">Summary</span>';
    html += '<div>Front <strong>' + layout.frontH + ' ft</strong></div>';
    html += '<div>Back <strong>' + layout.backH + ' ft</strong></div>';
    if (layout.panelCount > 0) {
        html += '<div>Panels <strong>' + layout.panelCount + '</strong> (' + layout.panelGrid.cols + '×' + layout.panelGrid.rows + ')</div>';
    }
    html += '<div>Purlin <strong>' + layout.purlins + '</strong> · Rafter <strong>' + layout.rafters + '</strong></div>';
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
    var viewDist = (Math.max(spanW * 0.95 + depth * 0.95, maxH * 2.8) + 1.6) * 0.68;
    camera.position.set(
        spanW * 0.34 + 1.0,
        targetY + maxH * 0.14 + 0.1,
        -viewDist
    );
    controls.update();
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

function buildSolarPanel3DGroup(panelW, panelLen, panelThick) {
    var group = new THREE.Group();
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
        var pad = 6;
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d', { alpha: true });
        ctx.font = '700 ' + fontPx + 'px Arial, sans-serif';
        var textW = Math.ceil(ctx.measureText(text).width);
        canvas.width = textW + pad * 2;
        canvas.height = fontPx + pad * 2;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var textColor = opts.color || '#334155';
        ctx.font = '700 ' + fontPx + 'px Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = textColor;
        ctx.fillText(text, canvas.width / 2, canvas.height / 2);
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
        spr.scale.set(opts.scaleX || 0.85, opts.scaleY || 0.24, 1);
        return spr;
    }

    // xAt(0)=left edge, xAt(1)=right edge of full structure width.
    var xL = xAt(0);
    var xR = xAt(1);
    var dimFrontX = xL - 0.48;
    var dimBackX = xR + 0.48;
    var sprFront = addVerticalDim(dimFrontX, 0, frontTopY, layout.frontH + ' ft');
    sprFront.position.set(dimFrontX - 0.52, (foundationH + frontTopY) / 2, 0);
    scene.add(sprFront);
    var sprBack = addVerticalDim(dimBackX, depth, backTopY, layout.backH + ' ft');
    sprBack.position.set(dimBackX + 0.52, (foundationH + backTopY) / 2, depth);
    scene.add(sprBack);

    var footY = 0.04;
    var wA = new THREE.Vector3(xL, footY, 0);
    var wB = new THREE.Vector3(xR, footY, 0);
    addLine(wA, wB);
    addCap(wA, new THREE.Vector3(0, 0, 1), 0.12);
    addCap(wB, new THREE.Vector3(0, 0, 1), 0.12);
    var widthLabel = (layout.structureWidthFt || Math.round(Math.abs(xR - xL) / 0.09)) + ' ft';
    var sprWidth = createTextSprite(widthLabel, { color: '#16a34a', scaleX: 0.9, scaleY: 0.24, fontSize: 22 });
    sprWidth.position.set((xL + xR) / 2, footY, -0.32);
    scene.add(sprWidth);

    var dA = new THREE.Vector3(xL - 0.38, footY, 0);
    var dB = new THREE.Vector3(xL - 0.38, footY, depth);
    addLine(dA, dB);
    addCap(dA, new THREE.Vector3(1, 0, 0), 0.12);
    addCap(dB, new THREE.Vector3(1, 0, 0), 0.12);
    var depthLabel = (layout.structureDepthFt || Math.round(depth / 0.09)) + ' ft';
    var sprDepth = createTextSprite(depthLabel, { color: '#16a34a', scaleX: 0.9, scaleY: 0.24, fontSize: 20 });
    sprDepth.position.set(xL - 0.78, footY, depth / 2);
    scene.add(sprDepth);

    var sprFrontLbl = createTextSprite('FRONT', { color: '#16a34a', scaleX: 0.68, scaleY: 0.22, fontSize: 22 });
    sprFrontLbl.position.set((xL + xR) / 2, footY, -0.55);
    scene.add(sprFrontLbl);
    var sprBackLbl = createTextSprite('BACK', { color: '#16a34a', scaleX: 0.65, scaleY: 0.22, fontSize: 22 });
    sprBackLbl.position.set((xL + xR) / 2, footY, depth + 0.5);
    scene.add(sprBackLbl);
}

function initSolarStructure3DView(viewportEl, layout, options) {
        options = options || {};
        var reportMode = !!options.reportMode;
    disposeSolar3DView(viewportEl);
    if (typeof THREE === 'undefined') {
        viewportEl.innerHTML = '<p class="text-muted small p-3 mb-0">3D viewer could not load. Check your internet connection.</p>';
        return;
    }

    var dirsEl = document.createElement('div');
    dirsEl.className = 'solar-3d-overlay-dirs';
    dirsEl.innerHTML = '<span>↑</span> Height · <span>→</span> Width · <span>↕</span> Front→Back depth · scroll/+− zoom';

    var zoomWrap = document.createElement('div');
    zoomWrap.className = 'solar-3d-zoom-controls';
    zoomWrap.setAttribute('aria-label', '3D zoom controls');
    zoomWrap.innerHTML =
        '<button type="button" class="solar-3d-zoom-btn" data-solar-3d-zoom="in" title="Zoom in" aria-label="Zoom in">+</button>' +
        '<button type="button" class="solar-3d-zoom-btn" data-solar-3d-zoom="out" title="Zoom out" aria-label="Zoom out">−</button>';
    viewportEl.appendChild(zoomWrap);
    viewportEl.appendChild(dirsEl);

    var hScale = 0.09;
    var foundationH = 0.1;
    var frontY = layout.frontH * hScale;
    var backY = layout.backH * hScale;
    var frontTopY = foundationH + frontY;
    var backTopY = foundationH + backY;
    var PANEL_WIDTH_FT = 4;
    var PANEL_LENGTH_FT = 8;
    var structureWidthFt = layout.structureWidthFt || ((layout.panelGrid && layout.panelGrid.cols)
        ? layout.panelGrid.cols * PANEL_WIDTH_FT
        : Math.max(layout.spanCols - 1, 1) * PANEL_WIDTH_FT);
    var structureDepthFt = layout.structureDepthFt || ((layout.panelGrid && layout.panelGrid.rows)
        ? layout.panelGrid.rows * PANEL_LENGTH_FT
        : PANEL_LENGTH_FT);
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
    scene.background = new THREE.Color(0xf8fafc);

    var width = viewportEl.clientWidth || 480;
    var height = viewportEl.clientHeight || 380;
    var camera = new THREE.PerspectiveCamera(34, width / height, 0.05, 200);
    var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
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

    var ground = new THREE.Mesh(
        new THREE.PlaneGeometry(12, 12),
        new THREE.MeshLambertMaterial({ color: 0xe2e8f0 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = 0;
    scene.add(ground);
    scene.add(new THREE.GridHelper(10, 20, 0xcbd5e1, 0xe2e8f0));

    var foundationMat = new THREE.MeshLambertMaterial({ color: 0x78716c });
    var legMat = new THREE.MeshLambertMaterial({ color: 0x57534e });
    var rafterMat = new THREE.MeshLambertMaterial({ color: 0xea580c });
    var foundationW = 0.32;
    var foundationD = 0.28;
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

    for (p = 0; p < layout.purlins; p++) {
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
    var panelLift = 0.11;
    var row3d, col3d, idx3d, u0, u1, t0, t1;
    var pA, pB, pC, pD, panelGroup, panelFront, panelBack, faceW, faceL;
    var cols3d = Math.max(layout.panelGrid.cols, 1);
    var rows3d = Math.max(layout.panelGrid.rows, 1);

    for (row3d = 0; row3d < layout.panelGrid.rows; row3d++) {
        t0 = row3d / rows3d;
        t1 = (row3d + 1) / rows3d;
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

    addSolar3DMeasurements(scene, layout, xAt, frontTopY, backTopY, depth, foundationH);

    setSolar3DFrontView(camera, controls, layout, xAt, frontTopY, backTopY, depth);

    var zoomScale = 1.12;
    if (zoomWrap) {
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
    function renderOnly3D(container, opts, options) {
        options = options || {};
        if (!container) return null;
        var layout = buildSolarStructureLayout(opts);
        initSolarStructure3DView(container, layout, options);
        return layout;
    }

    function capturePng(viewportEl) {
        var state = viewportEl && viewportEl._solar3dState;
        if (!state || !state.renderer) return null;
        if (state.rafId) {
            cancelAnimationFrame(state.rafId);
            state.rafId = null;
        }
        if (state.applyFrontView) state.applyFrontView();
        if (state.controls) state.controls.update();
        state.renderer.render(state.scene, state.camera);
        try {
            return state.renderer.domElement.toDataURL('image/png');
        } catch (e) {
            return null;
        }
    }

    global.SolarStructure3D = {
        dispose: disposeSolar3DView,
        buildLayout: buildSolarStructureLayout,
        initView: initSolarStructure3DView,
        renderOnly3D: renderOnly3D,
        capturePng: capturePng,
        setFrontView: setSolar3DFrontView
    };
})(typeof window !== 'undefined' ? window : this);
