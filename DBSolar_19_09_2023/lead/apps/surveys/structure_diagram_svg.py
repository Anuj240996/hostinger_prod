"""
2D solar structure diagram (plan + side elevation) for survey reports.
Mirrors the layout logic in survey_detail.html renderSolarStructureDiagram (2D portion).
"""

from __future__ import annotations

import io
import math
from typing import Any, Dict, Optional, Tuple


def survey_has_structure_layout(survey) -> bool:
    return bool(
        survey.structure_leg_count
        and survey.structure_rafter_count
        and survey.structure_purlin_count
    )


def get_survey_diagram_opts(survey) -> Optional[Dict[str, Any]]:
    if not survey_has_structure_layout(survey):
        return None
    legs = int(survey.structure_leg_count)
    rafters = int(survey.structure_rafter_count)
    purlins = int(survey.structure_purlin_count)
    panels = survey.structure_solar_panel_count
    front_h = float(survey.structure_front_height_ft or 0)
    back_h = float(survey.structure_back_height_ft or 0)
    return {
        'legs': legs,
        'rafters': rafters,
        'purlins': purlins,
        'solarPanels': int(panels) if panels else 0,
        'frontHeight': front_h,
        'backHeight': back_h,
    }


def _solar_panel_svg_defs() -> str:
    return (
        '<pattern id="solarPvCells" width="10" height="10" patternUnits="userSpaceOnUse">'
        '<rect width="10" height="10" fill="#0f1f33"/>'
        '<rect x="0.5" y="0.5" width="4" height="4" fill="#1a3358"/>'
        '<rect x="5.5" y="5.5" width="4" height="4" fill="#1a3358"/>'
        '<rect x="5.5" y="0.5" width="4" height="4" fill="#122a47"/>'
        '<rect x="0.5" y="5.5" width="4" height="4" fill="#122a47"/>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="rgba(148,163,184,0.4)" stroke-width="0.35"/>'
        '<line x1="0" y1="5" x2="10" y2="5" stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>'
        '<line x1="0" y1="0" x2="0" y2="10" stroke="rgba(148,163,184,0.4)" stroke-width="0.35"/>'
        '<line x1="5" y1="0" x2="5" y2="10" stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>'
        '</pattern>'
        '<filter id="planPanelShadow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="1" stdDeviation="1.2" flood-color="#0c1929" flood-opacity="0.3"/>'
        '</filter>'
    )


def _svg_solar_panel_grid_lines(x: float, y: float, w: float, h: float) -> str:
    rows = max(3, min(12, round(h / 8)))
    ch = h / rows
    parts = []
    for i in range(1, rows):
        yy = y + i * ch
        parts.append(
            f'<line x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}" '
            f'stroke="rgba(148,163,184,0.35)" stroke-width="0.35"/>'
        )
    return ''.join(parts)


def _svg_solar_panel_rect(x: float, y: float, w: float, h: float) -> str:
    if w < 3 or h < 3:
        return ''
    frame = 2
    s = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c5ced8" '
        f'stroke="#94a3b8" stroke-width="0.8" rx="1" filter="url(#planPanelShadow)"/>'
    )
    ix, iy = x + frame, y + frame
    iw, ih = w - frame * 2, h - frame * 2
    if iw > 2 and ih > 2:
        s += (
            f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="url(#solarPvCells)" '
            f'stroke="#152238" stroke-width="0.5" rx="0.5"/>'
        )
        s += _svg_solar_panel_grid_lines(ix, iy, iw, ih)
    return s


def _svg_solar_panel_side_slab(
    b0: Tuple[float, float],
    b1: Tuple[float, float],
    up: Tuple[float, float],
    profile_px: float,
) -> str:
    t0 = (b0[0] + up[0] * profile_px, b0[1] + up[1] * profile_px)
    t1 = (b1[0] + up[0] * profile_px, b1[1] + up[1] * profile_px)
    d = (
        f'M{b0[0]} {b0[1]} L{b1[0]} {b1[1]} L{t1[0]} {t1[1]} L{t0[0]} {t0[1]} Z'
    )
    return (
        f'<path d="{d}" fill="#1a3358" stroke="#152238" stroke-width="0.75" stroke-linejoin="round"/>'
        f'<line x1="{t0[0]}" y1="{t0[1]}" x2="{t1[0]}" y2="{t1[1]}" '
        f'stroke="rgba(148,163,184,0.45)" stroke-width="0.5"/>'
    )


def _build_layout(opts: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    legs = int(opts.get('legs') or 0)
    rafters = int(opts.get('rafters') or 0)
    purlins = int(opts.get('purlins') or 0)
    if legs < 1 or rafters < 1 or purlins < 1:
        return None

    solar_panels = int(opts.get('solarPanels') or 0)
    front_h = float(opts.get('frontHeight') or 0)
    back_h = float(opts.get('backHeight') or 0)
    max_h = max(front_h, back_h, 1)
    front_px = 22 + (front_h / max_h) * 72
    back_px = 22 + (back_h / max_h) * 72

    front_leg_count = math.ceil(legs / 2)
    back_leg_count = math.floor(legs / 2)
    leg_cols = max(front_leg_count, back_leg_count, 1)
    rafter_cols = rafters
    span_cols = max(leg_cols, rafter_cols)
    panel_count = solar_panels if solar_panels >= 1 else 0
    panel_rows = max(1, math.floor(purlins / 2))
    panel_cols_w = max(1, math.ceil(panel_count / panel_rows)) if panel_count > 0 else 0
    panel_grid = (
        {'rows': panel_rows, 'cols': panel_cols_w, 'total': panel_count}
        if panel_count > 0
        else {'rows': 0, 'cols': 0, 'total': 0}
    )

    def purlin_t(index: int) -> float:
        return 0.5 if purlins == 1 else index / (purlins - 1)

    def panel_depth_span(row: int) -> Dict[str, Any]:
        p0 = row * 2
        p1 = p0 + 1
        if p0 >= purlins:
            return {
                't0': row / panel_grid['rows'],
                't1': (row + 1) / panel_grid['rows'],
                'p0': -1,
                'p1': -1,
            }
        if p1 >= purlins:
            p1 = purlins - 1
        if p0 == p1 and p0 > 0:
            p0 -= 1
        ta, tb = purlin_t(p0), purlin_t(p1)
        return {'t0': min(ta, tb), 't1': max(ta, tb), 'p0': p0, 'p1': p1}

    def panel_portrait_span(row: int) -> Dict[str, float]:
        mount = panel_depth_span(row)
        gap = mount['t1'] - mount['t0'] or 0.15
        overhang = max(gap * 0.24, 0.035)
        t0 = max(0, mount['t0'] - overhang)
        t1 = min(1, mount['t1'] + overhang)
        if row > 0:
            prev = panel_depth_span(row - 1)
            t0 = max(t0, prev['t1'] + 0.012)
        if row < panel_grid['rows'] - 1:
            nxt = panel_depth_span(row + 1)
            t1 = min(t1, nxt['t0'] - 0.012)
        return {'t0': t0, 't1': t1}

    def rafter_bay_col(r: int) -> int:
        if rafter_cols <= 1:
            return 0
        if leg_cols == rafter_cols:
            return r
        return round(r * (leg_cols - 1) / (rafter_cols - 1))

    return {
        'legs': legs,
        'rafters': rafters,
        'purlins': purlins,
        'panel_count': panel_count,
        'front_h': front_h,
        'back_h': back_h,
        'front_px': front_px,
        'back_px': back_px,
        'front_leg_count': front_leg_count,
        'back_leg_count': back_leg_count,
        'leg_cols': leg_cols,
        'rafter_cols': rafter_cols,
        'span_cols': span_cols,
        'panel_grid': panel_grid,
        'purlin_t': purlin_t,
        'panel_portrait_span': panel_portrait_span,
        'rafter_bay_col': rafter_bay_col,
    }


def build_structure_diagram_inner_svg(opts: Dict[str, Any]) -> Optional[str]:
    layout = _build_layout(opts)
    if not layout:
        return None

    legs = layout['legs']
    rafters = layout['rafters']
    purlins = layout['purlins']
    panel_count = layout['panel_count']
    front_h = layout['front_h']
    back_h = layout['back_h']
    front_px = layout['front_px']
    back_px = layout['back_px']
    front_leg_count = layout['front_leg_count']
    back_leg_count = layout['back_leg_count']
    leg_cols = layout['leg_cols']
    rafter_cols = layout['rafter_cols']
    panel_grid = layout['panel_grid']
    purlin_t = layout['purlin_t']
    panel_portrait_span = layout['panel_portrait_span']
    rafter_bay_col = layout['rafter_bay_col']

    svg = ''
    svg += (
        '<defs><marker id="planArrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">'
        '<path d="M0,0 L6,3 L0,6 Z" fill="#64748b"/></marker>'
        + _solar_panel_svg_defs()
        + '</defs>'
    )
    svg += '<rect x="0" y="34" width="280" height="318" fill="#fff" stroke="none" rx="0"/>'

    px0, py0, pw, pd = 8, 48, 264, 118
    svg += (
        '<text x="138" y="46" text-anchor="middle" font-size="12" font-weight="600" fill="#1e293b">'
        'Plan view (top)</text>'
    )
    plan_pad = 2
    plan_inner_l = px0 + plan_pad
    plan_inner_r = px0 + pw - plan_pad
    plan_front_y = py0 + pd - 16
    plan_back_y = py0 + 16
    plan_depth_span = plan_front_y - plan_back_y
    plan_u_gap = 3 if panel_grid['cols'] > 1 else 0
    plan_row_gap = 4 if panel_grid['rows'] > 1 else 0

    def plan_x_at(col: int, total: int) -> float:
        if total > 1:
            return plan_inner_l + (plan_inner_r - plan_inner_l) * col / (total - 1)
        return plan_inner_l + (plan_inner_r - plan_inner_l) / 2

    def plan_purlin_y(idx: int) -> float:
        if purlins == 1:
            return (plan_front_y + plan_back_y) / 2
        return plan_back_y + (plan_depth_span * idx / (purlins - 1))

    svg += (
        f'<rect x="{plan_inner_l}" y="{plan_back_y}" width="{plan_inner_r - plan_inner_l}" '
        f'height="{plan_depth_span}" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1" rx="2"/>'
    )
    for g in range(1, 4):
        gx = plan_inner_l + (plan_inner_r - plan_inner_l) * g / 4
        gy = plan_back_y + plan_depth_span * g / 4
        svg += (
            f'<line x1="{gx}" y1="{plan_back_y}" x2="{gx}" y2="{plan_front_y}" '
            f'stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="2,4"/>'
        )
        svg += (
            f'<line x1="{plan_inner_l}" y1="{gy}" x2="{plan_inner_r}" y2="{gy}" '
            f'stroke="#cbd5e1" stroke-width="0.5" stroke-dasharray="2,4"/>'
        )

    def draw_plan_leg_foundation(lx: float, ly: float) -> str:
        fw, fd = 22, 12
        return (
            f'<rect x="{lx - fw / 2}" y="{ly - fd / 2}" width="{fw}" height="{fd}" '
            f'fill="#78716c" stroke="#44403c" stroke-width="1" rx="2"/>'
            f'<rect x="{lx - 5}" y="{ly - 4}" width="10" height="8" fill="#57534e" '
            f'stroke="#44403c" stroke-width="0.6" rx="1"/>'
        )

    for c in range(leg_cols):
        lx = plan_x_at(c, leg_cols)
        if c < front_leg_count:
            svg += draw_plan_leg_foundation(lx, plan_front_y)
        if c < back_leg_count:
            svg += draw_plan_leg_foundation(lx, plan_back_y)

    for r in range(rafter_cols):
        rcx = plan_x_at(rafter_bay_col(r), leg_cols)
        svg += (
            f'<line x1="{rcx}" y1="{plan_front_y + 2}" x2="{rcx}" y2="{plan_back_y - 2}" '
            f'stroke="#ea580c" stroke-width="5" stroke-linecap="round" opacity="0.95"/>'
        )

    for p in range(purlins):
        py = plan_purlin_y(p)
        svg += (
            f'<rect x="{plan_inner_l}" y="{py - 5}" width="{plan_inner_r - plan_inner_l}" '
            f'height="10" fill="#2563eb" stroke="#1d4ed8" stroke-width="0.8" rx="1" opacity="0.9"/>'
        )
        if purlins <= 6:
            svg += (
                f'<text x="{plan_inner_r + 4}" y="{py + 3}" font-size="6" fill="#1e40af">P{p + 1}</text>'
            )

    for row in range(panel_grid['rows']):
        visual = panel_portrait_span(row)
        for col in range(panel_grid['cols']):
            idx = row * panel_grid['cols'] + col
            if idx >= panel_count:
                continue
            t0, t1 = visual['t0'], visual['t1']
            u0 = col / panel_grid['cols']
            u1 = (col + 1) / panel_grid['cols']
            y_top = plan_back_y + plan_depth_span * t0 + (plan_row_gap / 2 if row > 0 else 1)
            y_bot = plan_back_y + plan_depth_span * t1 - (
                plan_row_gap / 2 if row < panel_grid['rows'] - 1 else 1
            )
            x_l = plan_inner_l + (plan_inner_r - plan_inner_l) * u0 + plan_u_gap
            x_r = plan_inner_l + (plan_inner_r - plan_inner_l) * u1 - plan_u_gap
            w, h = x_r - x_l, y_bot - y_top
            if w >= 4 and h >= 4:
                svg += _svg_solar_panel_rect(x_l, y_top, w, h)
                if panel_count <= 12:
                    fs = 6 if panel_grid['cols'] > 4 else 7
                    svg += (
                        f'<text x="{(x_l + x_r) / 2}" y="{(y_top + y_bot) / 2 + 4}" '
                        f'text-anchor="middle" font-size="{fs}" fill="#e2e8f0" font-weight="600" '
                        f'stroke="#0f1f33" stroke-width="0.4">M{idx + 1}</text>'
                    )

    for r in range(min(rafter_cols, 4)):
        rlx = plan_x_at(rafter_bay_col(r), leg_cols)
        svg += (
            f'<text x="{rlx}" y="{plan_front_y + 14}" text-anchor="middle" font-size="7" '
            f'fill="#c2410c" font-weight="600">R{r + 1}</text>'
        )

    mid_x = (plan_inner_l + plan_inner_r) / 2
    svg += (
        f'<text x="{mid_x}" y="{plan_front_y + 12}" text-anchor="middle" font-size="7" '
        f'fill="#16a34a" font-weight="600">FRONT</text>'
        f'<text x="{mid_x}" y="{plan_back_y - 6}" text-anchor="middle" font-size="7" '
        f'fill="#16a34a" font-weight="600">BACK</text>'
        f'<line x1="{mid_x}" y1="{plan_front_y + 16}" x2="{mid_x}" y2="{plan_back_y - 8}" '
        f'stroke="#64748b" stroke-width="1" marker-end="url(#planArrow)"/>'
        f'<line x1="{plan_inner_l}" y1="{py0 + pd / 2}" x2="{plan_inner_r}" y2="{py0 + pd / 2}" '
        f'stroke="#64748b" stroke-width="1" marker-end="url(#planArrow)"/>'
        f'<text x="{plan_inner_r + 2}" y="{py0 + pd / 2 + 3}" font-size="7" fill="#64748b">Width â†’</text>'
    )
    if panel_count > 0:
        svg += (
            f'<text x="{mid_x}" y="{py0 + 6}" text-anchor="middle" font-size="7" fill="#0369a1">'
            f'{panel_count} panels Â· {panel_grid["cols"]} wide Ã— {panel_grid["rows"]} deep</text>'
        )

    side_mid = 140
    sgy = 318
    rf_x, rb_x = 86, 194
    sf_top = sgy - front_px
    sb_top = sgy - back_px
    rdx, rdy = rb_x - rf_x, sb_top - sf_top
    r_len = math.sqrt(rdx * rdx + rdy * rdy) or 1
    tang_x, tang_y = (rdx / r_len) * 7, (rdy / r_len) * 7
    panel_up_nx, panel_up_ny = (rdy / r_len) * 18, (-rdx / r_len) * 18
    side_purlin_top_lift = 10
    side_panel_base_lift = 13
    side_panel_edge_thick = 2.2
    side_panel_profile_px = 14
    tang_len = math.sqrt(tang_x * tang_x + tang_y * tang_y) or 1
    tux, tuy = tang_x / tang_len, tang_y / tang_len

    def side_on_rafter(t: float) -> Tuple[float, float]:
        return (rf_x + rdx * t, sf_top + rdy * t)

    def side_panel_up_unit() -> Tuple[float, float]:
        ln = math.sqrt(panel_up_nx ** 2 + panel_up_ny ** 2) or 1
        return (panel_up_nx / ln, panel_up_ny / ln)

    def side_point_lifted(t: float, lift: float) -> Tuple[float, float]:
        pt = side_on_rafter(t)
        up = side_panel_up_unit()
        return (pt[0] + up[0] * lift, pt[1] + up[1] * lift)

    svg += (
        f'<text x="{side_mid}" y="180" text-anchor="middle" font-size="12" font-weight="600" '
        f'fill="#1e293b">Side elevation</text>'
        f'<line x1="48" y1="{sgy}" x2="228" y2="{sgy}" stroke="#94a3b8" stroke-width="2"/>'
    )
    side_found_h = 0
    svg += (
        f'<rect x="88" y="{sf_top}" width="8" height="{sgy - sf_top}" fill="#64748b"/>'
        f'<rect x="172" y="{sb_top}" width="8" height="{sgy - sb_top}" fill="#64748b"/>'
        f'<line x1="{rf_x}" y1="{sf_top}" x2="{rb_x}" y2="{sb_top}" stroke="#ea580c" stroke-width="4"/>'
    )

    def draw_side_c_channel(pt: Tuple[float, float], label: str) -> str:
        bx, by = pt
        lip = 11
        return (
            f'<path d="M{bx} {by} L{bx + tang_x} {by + tang_y} '
            f'L{bx + tang_x + panel_up_nx * 0.4} {by + tang_y + panel_up_ny * 0.4 - lip} '
            f'L{bx - tang_x + panel_up_nx * 0.4} {by - tang_y + panel_up_ny * 0.4 - lip} '
            f'L{bx - tang_x} {by - tang_y} Z" fill="#93c5fd" stroke="#1d4ed8" stroke-width="1.2"/>'
            f'<line x1="{bx + tang_x + panel_up_nx * 0.4}" y1="{by + tang_y + panel_up_ny * 0.4 - lip}" '
            f'x2="{bx - tang_x + panel_up_nx * 0.4}" y2="{by - tang_y + panel_up_ny * 0.4 - lip}" '
            f'stroke="#1e40af" stroke-width="1.5"/>'
            + (f'<text x="{bx + panel_up_nx * 0.5 + 8}" y="{by + panel_up_ny * 0.5}" '
               f'font-size="7" fill="#1d4ed8">{label}</text>' if label else '')
        )

    up = side_panel_up_unit()
    half_t = side_panel_edge_thick / 2

    for side_row in range(panel_grid['rows']):
        mount = panel_portrait_span(side_row)
        b0 = side_point_lifted(mount['t0'], side_panel_base_lift)
        b1 = side_point_lifted(mount['t1'], side_panel_base_lift)
        b_l0 = (b0[0] - tux * half_t, b0[1] - tuy * half_t)
        b_l1 = (b1[0] - tux * half_t, b1[1] - tuy * half_t)
        svg += _svg_solar_panel_side_slab(b_l0, b_l1, up, side_panel_profile_px)
        if panel_count <= 12:
            row_start = side_row * panel_grid['cols']
            side_label_start = row_start + 1
            side_label_end = min(row_start + panel_grid['cols'], panel_count)
            side_label = (
                f'M{side_label_start}'
                if side_label_start == side_label_end
                else f'M{side_label_start}\u2013M{side_label_end}'
            )
            lx = (b0[0] + b1[0]) / 2 + up[0] * (side_panel_profile_px * 0.45)
            ly = (b0[1] + b1[1]) / 2 + up[1] * (side_panel_profile_px * 0.45)
            svg += (
                f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="6" fill="#e2e8f0" '
                f'font-weight="600" stroke="#0f1f33" stroke-width="0.35">{side_label}</text>'
            )

    for p in range(purlins):
        svg += draw_side_c_channel(side_on_rafter(purlin_t(p)), f'P{p + 1}')

    svg += (
        '<text x="52" y="170" font-size="7" fill="#1d4ed8">âŠ C-channel purlin</text>'
        f'<line x1="52" y1="{sf_top}" x2="52" y2="{sgy}" stroke="#16a34a" stroke-width="1"/>'
        f'<line x1="48" y1="{sf_top}" x2="56" y2="{sf_top}" stroke="#16a34a" stroke-width="1"/>'
        f'<line x1="48" y1="{sgy}" x2="56" y2="{sgy}" stroke="#16a34a" stroke-width="1"/>'
        f'<text x="38" y="{(sgy + sf_top) / 2}" font-size="9" fill="#16a34a" text-anchor="end">'
        f'{front_h or "â€”"} ft</text>'
        f'<line x1="212" y1="{sb_top}" x2="212" y2="{sgy}" stroke="#16a34a" stroke-width="1"/>'
        f'<line x1="208" y1="{sb_top}" x2="216" y2="{sb_top}" stroke="#16a34a" stroke-width="1"/>'
        f'<line x1="208" y1="{sgy}" x2="216" y2="{sgy}" stroke="#16a34a" stroke-width="1"/>'
        f'<text x="222" y="{(sgy + sb_top) / 2}" font-size="9" fill="#16a34a">{back_h or "â€”"} ft</text>'
        f'<line x1="60" y1="{sgy + 6}" x2="216" y2="{sgy + 6}" stroke="#64748b" stroke-width="1" '
        f'marker-end="url(#planArrow)"/>'
        f'<text x="138" y="{sgy + 18}" text-anchor="middle" font-size="7" fill="#64748b">Front â†’ Back</text>'
        f'<text x="{rf_x}" y="{sgy + 14}" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">'
        f'FRONT</text>'
        f'<text x="{rb_x}" y="{sgy + 14}" text-anchor="middle" font-size="7" fill="#16a34a" font-weight="600">'
        f'BACK</text>'
    )

    return svg


def build_structure_legend_svg(layout_opts: Dict[str, Any]) -> str:
    layout = _build_layout(layout_opts)
    if not layout:
        return ''
    legs = layout['legs']
    rafters = layout['rafters']
    purlins = layout['purlins']
    panel_count = layout['panel_count']
    panel_grid = layout['panel_grid']
    panel_txt = (
        f' ({panel_grid["cols"]}Ã—{panel_grid["rows"]})' if panel_count > 0 else ''
    )
    return (
        '<svg viewBox="0 0 820 36" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Structure legend">'
        '<rect x="0" y="0" width="820" height="36" rx="4" fill="#fff" stroke="#e2e8f0"/>'
        '<rect x="10" y="11" width="12" height="8" fill="#78716c"/>'
        f'<text x="26" y="22" font-size="9" fill="#334155">Foundation + leg Ã—{legs}</text>'
        '<line x1="188" y1="18" x2="212" y2="10" stroke="#ea580c" stroke-width="3"/>'
        f'<text x="220" y="22" font-size="9" fill="#334155">Rafter Ã—{rafters}</text>'
        '<line x1="298" y1="18" x2="322" y2="18" stroke="#2563eb" stroke-width="3"/>'
        f'<text x="330" y="22" font-size="9" fill="#334155">C-purlin Ã—{purlins}</text>'
        '<rect x="408" y="11" width="22" height="14" fill="#c5ced8" stroke="#94a3b8" '
        'stroke-width="0.6" rx="1"/>'
        '<rect x="411" y="14" width="16" height="8" fill="#1a3358" stroke="#152238" '
        'stroke-width="0.5" rx="0.5"/>'
        f'<text x="434" y="22" font-size="9" fill="#334155">Panel Ã—{panel_count}{panel_txt}</text>'
        '</svg>'
    )


def build_structure_legend_for_survey(survey) -> str:
    opts = get_survey_diagram_opts(survey)
    return build_structure_legend_svg(opts) if opts else ''


def build_structure_diagram_svg_document(survey) -> Optional[str]:
    """Full SVG document (plan + side elevation) for embedding in HTML or PDF."""
    opts = get_survey_diagram_opts(survey)
    if not opts:
        return None
    inner = build_structure_diagram_inner_svg(opts)
    if not inner:
        return None
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<svg xmlns="http://www.w3.org/2000/svg" class="structure-diagram-main" viewBox="0 0 280 400" '
        'role="img" aria-label="Solar structure plan and side elevation">'
        '<rect x="0" y="0" width="280" height="400" fill="#ffffff" rx="6"/>'
        f'{inner}'
        '</svg>'
    )


def structure_measurement_rows(survey):
    """Return (label, value) rows for the structure measurement summary table."""
    def fmt_num(val):
        try:
            num = float(val)
        except (TypeError, ValueError):
            return str(val)
        if num.is_integer():
            return str(int(num))
        return ('%f' % num).rstrip('0').rstrip('.')

    opts = get_survey_diagram_opts(survey)
    if not opts:
        return []
    layout = _build_layout(opts)
    if not layout:
        return []
    rows = [
        ('Front Height', f'{fmt_num(layout["front_h"])} ft'),
        ('Back Height', f'{fmt_num(layout["back_h"])} ft'),
        ('Legs', f'{fmt_num(layout["legs"])} Nos.'),
        ('Rafters', f'{fmt_num(layout["rafters"])} Nos.'),
        ('Purlins', f'{fmt_num(layout["purlins"])} Nos.'),
    ]
    if layout['panel_count'] > 0:
        rows.append((
            'Panels',
            f'{layout["panel_count"]} ({layout["panel_grid"]["cols"]}×{layout["panel_grid"]["rows"]})',
        ))
    return rows


def structure_diagram_summary_text(survey) -> str:
    opts = get_survey_diagram_opts(survey)
    if not opts:
        return ''
    layout = _build_layout(opts)
    if not layout:
        return ''
    front_h = layout['front_h']
    back_h = layout['back_h']
    panel_count = layout['panel_count']
    panel_grid = layout['panel_grid']
    summary = f'Front {front_h or "â€”"} ft Â· Back {back_h or "â€”"} ft'
    if panel_count > 0:
        summary += (
            f' Â· Panels {panel_count} ({panel_grid["cols"]}Ã—{panel_grid["rows"]})'
            f' Â· Purlin {opts["purlins"]} Â· Rafter {opts["rafters"]}'
        )
    else:
        summary += f' Â· Purlin {opts["purlins"]} Â· Rafter {opts["rafters"]}'
    return summary


def build_structure_front3d_svg_document(survey) -> Optional[str]:
    """
    Build a static front-side 3D-style SVG (non-interactive) for PDF reports.
    This intentionally mirrors the front-view intent from the interactive 3D widget.
    """
    opts = get_survey_diagram_opts(survey)
    if not opts:
        return None
    layout = _build_layout(opts)
    if not layout:
        return None

    legs = layout['legs']
    rafters = layout['rafters']
    purlins = layout['purlins']
    panel_count = layout['panel_count']
    panel_grid = layout['panel_grid']
    front_h = layout['front_h']
    back_h = layout['back_h']
    front_leg_count = layout['front_leg_count']
    back_leg_count = layout['back_leg_count']
    leg_cols = layout['leg_cols']
    rafter_cols = layout['rafter_cols']
    span_cols = layout['span_cols']
    purlin_t = layout['purlin_t']
    rafter_bay_col = layout['rafter_bay_col']

    w = 700
    h = 360
    foundation_y = 300
    left_x = 90
    span_w = 250
    # Keep a very small depth offset so the figure reads as FRONT view,
    # not an isometric top/side view.
    depth_dx = 22
    depth_dy = -12
    max_h_ft = max(front_h, back_h, 1.0)
    h_px_per_ft = 145.0 / max_h_ft
    front_leg_h = front_h * h_px_per_ft
    back_leg_h = back_h * h_px_per_ft
    panel_lift = 4.0
    foundation_block_h = 12
    leg_base_front = foundation_y
    leg_base_back = foundation_y + depth_dy

    def x_at(col: int, total: int) -> float:
        if total <= 1:
            return left_x + span_w / 2
        return left_x + (span_w * col / (total - 1))

    def roof_pt(t_depth: float, width_frac: float) -> Tuple[float, float]:
        rf = width_frac * (rafter_cols - 1)
        r0 = int(math.floor(rf))
        r1 = min(r0 + 1, rafter_cols - 1)
        rw = 0 if rafter_cols <= 1 else (rf - r0)
        x0 = x_at(rafter_bay_col(r0), span_cols)
        x1 = x_at(rafter_bay_col(r1), span_cols)
        x = x0 * (1 - rw) + x1 * rw + depth_dx * t_depth
        y_front = leg_base_front - front_leg_h
        y_back = leg_base_back - back_leg_h
        y = y_front + (y_back - y_front) * t_depth
        return (x, y)

    def panel_span(row: int) -> Tuple[float, float]:
        rows = max(panel_grid['rows'], 1)
        p0 = row * 2
        p1 = min(p0 + 1, purlins - 1)
        if p0 >= purlins:
            return (row / rows, (row + 1) / rows)
        if p0 == p1 and p0 > 0:
            p0 -= 1
        t0 = purlin_t(p0)
        t1 = purlin_t(p1)
        if t1 < t0:
            t0, t1 = t1, t0
        gap = t1 - t0 or 0.15
        over = max(gap * 0.22, 0.03)
        return (max(0.0, t0 - over), min(1.0, t1 + over))

    fx_dim = left_x - 28
    bx_dim = left_x + depth_dx + span_w + 18
    f_top_y = leg_base_front - front_leg_h
    b_top_y = leg_base_back - back_leg_h
    structure_top = min(f_top_y, b_top_y) - 48
    structure_bottom = max(leg_base_front, leg_base_back) + foundation_block_h
    c_min_x = fx_dim - 20
    c_max_x = bx_dim + 36
    c_min_y = structure_top - 6
    c_max_y = structure_bottom + 10
    vb_w = c_max_x - c_min_x
    vb_h = c_max_y - c_min_y
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{c_min_x} {c_min_y} {vb_w} {vb_h}" role="img" aria-label="Front side 3D structure view">',
        '<defs>'
        '<linearGradient id="panelG" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="#1e3a5f"/>'
        '<stop offset="100%" stop-color="#0f1f33"/>'
        '</linearGradient>'
        '</defs>',
        f'<rect x="{c_min_x}" y="{c_min_y}" width="{vb_w}" height="{vb_h}" fill="#ffffff"/>',
    ]

    foundation_block_w = 18
    for c in range(leg_cols):
        fx = x_at(c, leg_cols)
        bx = fx + depth_dx
        if c < front_leg_count:
            svg_parts.append(
                f'<rect x="{fx - foundation_block_w / 2}" y="{leg_base_front}" '
                f'width="{foundation_block_w}" height="{foundation_block_h}" fill="#78716c" stroke="#44403c" stroke-width="0.8" rx="1"/>'
            )
        if c < back_leg_count:
            svg_parts.append(
                f'<rect x="{bx - foundation_block_w / 2}" y="{leg_base_back}" '
                f'width="{foundation_block_w}" height="{foundation_block_h}" fill="#78716c" stroke="#44403c" stroke-width="0.8" rx="1"/>'
            )

    for c in range(leg_cols):
        fx = x_at(c, leg_cols)
        bx = fx + depth_dx
        f_top = leg_base_front - front_leg_h
        b_top = leg_base_back - back_leg_h
        if c < back_leg_count:
            svg_parts.append(
                f'<rect x="{bx - 5}" y="{b_top}" width="10" height="{leg_base_back - b_top}" fill="#6b7280" opacity="0.95"/>'
            )
        if c < front_leg_count:
            svg_parts.append(
                f'<rect x="{fx - 6}" y="{f_top}" width="12" height="{leg_base_front - f_top}" fill="#57534e"/>'
            )

    for r in range(rafter_cols):
        col = rafter_bay_col(r)
        fx = x_at(col, span_cols)
        bx = fx + depth_dx
        fy = leg_base_front - front_leg_h
        by = leg_base_back - back_leg_h
        svg_parts.append(
            f'<line x1="{fx}" y1="{fy}" x2="{bx}" y2="{by}" stroke="#ea580c" stroke-width="4.5" stroke-linecap="round"/>'
        )

    for p in range(purlins):
        t = purlin_t(p)
        lx, ly = roof_pt(t, 0.0)
        rx, ry = roof_pt(t, 1.0)
        svg_parts.append(
            f'<line x1="{lx}" y1="{ly}" x2="{rx}" y2="{ry}" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>'
        )

    # Prominent dimension lines for fallback image.
    svg_parts.extend([
        f'<line x1="{fx_dim}" y1="{f_top_y}" x2="{fx_dim}" y2="{leg_base_front}" stroke="#16a34a" stroke-width="2"/>',
        f'<line x1="{fx_dim - 4}" y1="{f_top_y}" x2="{fx_dim + 4}" y2="{f_top_y}" stroke="#16a34a" stroke-width="2"/>',
        f'<line x1="{fx_dim - 4}" y1="{leg_base_front}" x2="{fx_dim + 4}" y2="{leg_base_front}" stroke="#16a34a" stroke-width="2"/>',
        f'<text x="{fx_dim - 10}" y="{(f_top_y + leg_base_front) / 2}" text-anchor="end" font-size="16" font-weight="700" fill="#16a34a">{front_h or "—"} ft</text>',
        f'<line x1="{bx_dim}" y1="{b_top_y}" x2="{bx_dim}" y2="{leg_base_back}" stroke="#16a34a" stroke-width="2"/>',
        f'<line x1="{bx_dim - 4}" y1="{b_top_y}" x2="{bx_dim + 4}" y2="{b_top_y}" stroke="#16a34a" stroke-width="2"/>',
        f'<line x1="{bx_dim - 4}" y1="{leg_base_back}" x2="{bx_dim + 4}" y2="{leg_base_back}" stroke="#16a34a" stroke-width="2"/>',
        f'<text x="{bx_dim + 10}" y="{(b_top_y + leg_base_back) / 2}" font-size="16" font-weight="700" fill="#16a34a">{back_h or "—"} ft</text>',
    ])

    if panel_count > 0 and panel_grid['rows'] > 0 and panel_grid['cols'] > 0:
        idx = 0
        for row in range(panel_grid['rows']):
            t0, t1 = panel_span(row)
            for col in range(panel_grid['cols']):
                if idx >= panel_count:
                    break
                u0 = col / panel_grid['cols']
                u1 = (col + 1) / panel_grid['cols']
                # Fallback portrait module shaping (narrow width, longer height).
                u_mid = (u0 + u1) / 2
                u_half = (u1 - u0) * 0.49
                pu0 = max(0.0, u_mid - u_half)
                pu1 = min(1.0, u_mid + u_half)
                t_mid = (t0 + t1) / 2
                t_half = (t1 - t0) * 0.7
                pt0 = max(0.0, t_mid - t_half)
                pt1 = min(1.0, t_mid + t_half)

                a = roof_pt(pt0, pu0)
                b = roof_pt(pt0, pu1)
                c = roof_pt(pt1, pu1)
                d = roof_pt(pt1, pu0)
                a = (a[0], a[1] - panel_lift)
                b = (b[0], b[1] - panel_lift)
                c = (c[0], c[1] - panel_lift)
                d = (d[0], d[1] - panel_lift)
                svg_parts.append(
                    f'<polygon points="{a[0]},{a[1]} {b[0]},{b[1]} {c[0]},{c[1]} {d[0]},{d[1]}" fill="url(#panelG)" stroke="#c5ced8" stroke-width="0.9"/>'
                )
                idx += 1

    svg_parts.append('</svg>')
    return ''.join(svg_parts)


def _reportlab_image_from_svg(svg_doc: Optional[str], width: float, height: float):
    if not svg_doc:
        return None
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        from reportlab.platypus import Image as RLImage
        from reportlab.lib.utils import ImageReader
    except ImportError:
        return None

    drawing = svg2rlg(io.BytesIO(svg_doc.encode('utf-8')))
    if not drawing:
        return None

    pil_img = renderPM.drawToPIL(drawing)
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG')
    buf.seek(0)
    aspect = pil_img.height / pil_img.width if pil_img.width else 1
    img_h = width * aspect
    return RLImage(ImageReader(buf), width=width, height=min(img_h, height))


def structure_diagram_reportlab_image(survey, width: float = 480, height: float = 320):
    """Return a reportlab Image flowable for the 2D structure diagram, or None."""
    return _reportlab_image_from_svg(
        build_structure_diagram_svg_document(survey),
        width=width,
        height=height,
    )


def structure_front3d_reportlab_image(survey, width: float = 480, height: float = 250):
    """Return a reportlab Image flowable for the static front-side 3D view, or None."""
    return _reportlab_image_from_svg(
        build_structure_front3d_svg_document(survey),
        width=width,
        height=height,
    )
