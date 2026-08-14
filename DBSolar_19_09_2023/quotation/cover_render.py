"""Paint the Standard & Industrial cover as a full A4 PNG (EST-001 layout)."""

from __future__ import annotations

import os
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont


A4_W = 1191  # 595.27pt at 2x
A4_H = 1684  # 841.89pt at 2x
YELLOW = (255, 210, 0)
NAVY = (10, 37, 64)
BLACK = (17, 17, 17)
WHITE = (255, 255, 255)


def _font(size, bold=False):
    names = []
    if bold:
        names += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ]
    else:
        names += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]
    for path in names:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _text_w(font, text):
    if hasattr(font, "getlength"):
        return font.getlength(text)
    if hasattr(font, "getbbox"):
        box = font.getbbox(text)
        return box[2] - box[0]
    return font.getsize(text)[0]


def _wrap(text, font, max_width):
    text = (text or "").replace("\r", "").strip()
    if not text:
        return []
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if _text_w(font, trial) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def _cover_fit(im, tw, th):
    im = im.convert("RGB")
    scale = max(tw / float(im.width), th / float(im.height))
    nw = max(1, int(round(im.width * scale)))
    nh = max(1, int(round(im.height * scale)))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return im.crop((left, top, left + tw, top + th))


def _open_image(field_or_path):
    if field_or_path is None:
        return None
    path = field_or_path
    if hasattr(field_or_path, "path"):
        try:
            if field_or_path and getattr(field_or_path, "name", ""):
                path = field_or_path.path
            else:
                return None
        except Exception:
            return None
    if not path or not os.path.isfile(str(path)):
        return None
    try:
        return Image.open(path)
    except Exception:
        return None


def _static_cover_path():
    candidates = [
        settings.BASE_DIR / "static" / "quotation" / "proposal" / "cover_left.png",
        settings.BASE_DIR / "asert" / "quotation" / "proposal" / "cover_left.png",
        settings.BASE_DIR / "staticfiles" / "quotation" / "proposal" / "cover_left.png",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return str(path)
    return None


def _draw_right(draw, x_right, y, lines, font, fill, line_gap):
    for line in lines:
        draw.text((x_right - _text_w(font, line), y), line, font=font, fill=fill)
        y += line_gap
    return y


def _draw_left(draw, x, y, lines, font, fill, line_gap):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_gap
    return y


def render_proposal_cover_png(quotation, master, formatted_date, this_year):
    """
    Return filesystem path of a generated A4 cover PNG.
    Left: full-height photo (50% width). Right: yellow / navy / yellow like EST-001.
    """
    canvas = Image.new("RGB", (A4_W, A4_H), WHITE)
    mid = A4_W // 2

    photo = None
    if master is not None:
        photo = _open_image(getattr(master, "proposal_cover_image", None))
    if photo is None:
        photo = _open_image(_static_cover_path())
    if photo is not None:
        canvas.paste(_cover_fit(photo, mid, A4_H), (0, 0))
        photo.close()
    else:
        ImageDraw.Draw(canvas).rectangle((0, 0, mid, A4_H), fill=(20, 60, 90))

    y1 = int(A4_H * 0.18)
    y2 = int(A4_H * 0.50)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((mid, 0, A4_W, y1), fill=YELLOW)
    draw.rectangle((mid, y1, A4_W, y2), fill=NAVY)
    draw.rectangle((mid, y2, A4_W, A4_H), fill=YELLOW)

    pad = 36
    x_left = mid + pad
    x_right = A4_W - pad
    col_w = x_right - x_left

    title_font = _font(42, bold=True)
    ty = 48
    for line in ("Roof Top Solar", "Proposal"):
        draw.text((x_right - _text_w(title_font, line), ty), line, font=title_font, fill=BLACK)
        ty += 52

    ny = y1 + 28
    logo = _open_image(getattr(master, "company_logo", None) if master else None)
    if logo is not None:
        logo = logo.convert("RGBA")
        max_h, max_w = 90, 220
        scale = min(max_w / float(logo.width), max_h / float(logo.height), 1.0)
        logo = logo.resize(
            (max(1, int(logo.width * scale)), max(1, int(logo.height * scale))),
            Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS,
        )
        bg = Image.new("RGB", (logo.width + 12, logo.height + 12), WHITE)
        if logo.mode == "RGBA":
            bg.paste(logo, (6, 6), logo)
        else:
            bg.paste(logo.convert("RGB"), (6, 6))
        canvas.paste(bg, (x_left, ny))
        ny += bg.height + 16
        logo.close()

    name_font = _font(30, bold=True)
    body_font = _font(20)
    company = (getattr(master, "company_name", None) or "Heramb Industries") if master else "Heramb Industries"
    ny = _draw_left(draw, x_left, ny, _wrap(company, name_font, col_w), name_font, WHITE, 36)
    ny += 10
    address = ""
    if master is not None:
        address = (getattr(master, "from_address", None) or getattr(master, "address", None) or "").strip()
    if not address:
        address = (
            "Bhagya Banglow, Near Sant Eknath Rang Mandir,\n"
            "New Osman Pura, Chh. Sambhajinagar (MH) - 431001"
        )
    _draw_left(draw, x_left, ny, _wrap(address, body_font, col_w), body_font, WHITE, 28)

    consumer = "{} {}".format(
        getattr(quotation, "title", "") or "",
        getattr(quotation, "consumer_name", "") or "",
    ).strip()
    addr1 = getattr(quotation, "consumer_address1", "") or ""
    addr2 = getattr(quotation, "consumer_address2", "") or ""
    consumer_addr = ",\n".join([line for line in (addr1, addr2) if line])

    ctype = getattr(quotation, "consumer_type", "") or ""
    qno = getattr(quotation, "quotation_no", "") or quotation.pk
    if ctype == "Residential":
        qid = "DB/Res/{}/{}".format(qno, this_year)
    elif ctype == "Commercial":
        qid = "DB/Comm/{}/{}".format(qno, this_year)
    elif ctype == "Industrial":
        qid = "DB/Ind/{}/{}".format(qno, this_year)
    else:
        qid = str(qno)

    by_name = getattr(quotation, "employee_name", "") or ""
    meta = [
        "ID : {}".format(qid),
        "Date : {}".format(formatted_date or ""),
        "By : {}".format(by_name),
    ]

    cy = y2 + 36
    cy = _draw_right(draw, x_right, cy, _wrap(consumer, name_font, col_w), name_font, BLACK, 36)
    cy += 8
    cy = _draw_right(draw, x_right, cy, _wrap(consumer_addr, body_font, col_w), body_font, BLACK, 28)
    cy += 18
    draw.line((x_left, cy, x_right, cy), fill=BLACK, width=2)
    cy += 22
    _draw_right(draw, x_right, cy, meta, body_font, BLACK, 30)

    out_name = "cover_{}.jpg".format(quotation.pk)
    try:
        out_dir = os.path.join(str(settings.MEDIA_ROOT), "quotation", "generated")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, out_name)
        canvas.convert("RGB").save(out_path, "JPEG", quality=85)
        media_url = settings.MEDIA_URL.rstrip("/") + "/quotation/generated/" + out_name
        return media_url
    except Exception:
        import tempfile
        fd, out_path = tempfile.mkstemp(prefix="cover_", suffix=".jpg")
        os.close(fd)
        canvas.convert("RGB").save(out_path, "JPEG", quality=85)
        return out_path
