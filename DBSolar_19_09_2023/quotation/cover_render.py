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


def _draw_right_labeled(draw, x_right, y, label, value, label_font, value_font, fill, line_gap):
    value = value or ""
    label_text = label
    total = _text_w(label_font, label_text) + _text_w(value_font, value)
    x = x_right - total
    draw.text((x, y), label_text, font=label_font, fill=fill)
    draw.text((x + _text_w(label_font, label_text), y), value, font=value_font, fill=fill)
    return y + line_gap


def render_proposal_cover_png(quotation, master, formatted_date, this_year, formatted_expiry_date=None):
    """
    Full A4 JPEG with equal white margins on all four sides.
    Left photo + yellow / navy / yellow like the Sample 2 edit preview.
    """
    import tempfile

    m = 0  # bleed to the JPEG edges; PDF places this image on full A4
    ox, oy = m, m
    inner_r = A4_W - m
    inner_b = A4_H - m
    cw, ch = inner_r - ox, inner_b - oy
    mid = ox + cw // 2

    canvas = Image.new("RGB", (A4_W, A4_H), WHITE)

    photo = None
    if master is not None:
        photo = _open_image(getattr(master, "proposal_cover_image", None))
    if photo is None:
        photo = _open_image(_static_cover_path())
    left_w = mid - ox
    if photo is not None:
        canvas.paste(_cover_fit(photo, left_w, ch), (ox, oy))
        photo.close()
    else:
        ImageDraw.Draw(canvas).rectangle((ox, oy, mid, inner_b), fill=(20, 60, 90))

    # Navy band: slightly lower and shorter than the previous 18%–50% band
    y1 = oy + int(ch * 0.24)
    y2 = y1 + int(ch * 0.20)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((mid, oy, inner_r, y1), fill=YELLOW)
    draw.rectangle((mid, y1, inner_r, y2), fill=NAVY)
    draw.rectangle((mid, y2, inner_r, inner_b), fill=YELLOW)

    pad = 28
    x_left = mid + pad
    x_right = inner_r - pad
    col_w = max(40, x_right - x_left)

    title_font = _font(42, bold=True)
    ty = oy + 40
    for line in ("Roof Top Solar", "Proposal"):
        draw.text((x_right - _text_w(title_font, line), ty), line, font=title_font, fill=BLACK)
        ty += 52

    ny = y1 + 18
    logo = _open_image(getattr(master, "company_logo", None) if master else None)
    if logo is not None:
        logo = logo.convert("RGBA")
        max_h, max_w = 72, 200
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
        ny += bg.height + 10
        logo.close()

    name_font = _font(31, bold=True)
    body_font = _font(20)
    label_font = _font(20, bold=True)
    company = (getattr(master, "company_name", None) or "Heramb Industries") if master else "Heramb Industries"
    company = company.upper()
    ny = _draw_left(draw, x_left, ny, _wrap(company, name_font, col_w), name_font, WHITE, 36)
    ny += 8
    address = ""
    if master is not None:
        address = (getattr(master, "from_address", None) or getattr(master, "address", None) or "").strip()
    if not address:
        address = (
            "Bhagya Banglow, Near Sant Eknath Rang Mandir,\n"
            "New Osman Pura, Chh. Sambhajinagar (MH) - 431001"
        )
    _draw_left(draw, x_left, ny, _wrap(address, body_font, col_w), body_font, WHITE, 26)

    consumer = "{} {}".format(
        getattr(quotation, "title", "") or "",
        getattr(quotation, "consumer_name", "") or "",
    ).strip()
    addr1 = getattr(quotation, "consumer_address1", "") or ""
    addr2 = getattr(quotation, "consumer_address2", "") or ""
    consumer_addr = ",\n".join([line for line in (addr1, addr2) if line])
    consumer_mobile = getattr(quotation, "consumer_mobile", "") or ""

    ctype = getattr(quotation, "consumer_type", "") or ""
    qno = getattr(quotation, "quotation_no", "") or quotation.pk
    if ctype == "Residential":
        qid = "DB/Res/{}/{}".format(qno, this_year)
    elif ctype == "Commercial":
        qid = "DB/Comm/{}/{}".format(qno, this_year)
    elif ctype == "Industrial":
        qid = "DB/Ind/{}/{}".format(qno, this_year)
    elif ctype == "Government":
        qid = "DB/Gov/{}/{}".format(qno, this_year)
    else:
        qid = str(qno)

    by_name = getattr(quotation, "employee_name", "") or ""
    by_contact = ""
    try:
        reps = list(quotation.representatives.all())
        if reps:
            by_name = getattr(reps[0], "name", None) or by_name
            by_contact = getattr(reps[0], "contact", "") or ""
    except Exception:
        pass

    expiry = formatted_expiry_date or formatted_date or ""

    cy = y2 + 22
    type_label = ctype or ""
    if type_label:
        card_h = 50
        card_box = (x_left, cy, x_right, cy + card_h)
        try:
            draw.rounded_rectangle(card_box, radius=12, fill=WHITE, outline=NAVY, width=3)
        except Exception:
            draw.rectangle(card_box, fill=WHITE, outline=NAVY, width=3)
        type_font = _font(24, bold=True)
        tw = _text_w(type_font, type_label)
        draw.text((x_left + max(10, (col_w - tw) / 2), cy + 10), type_label, font=type_font, fill=NAVY)
        cy += card_h + 14

    cy = _draw_right(draw, x_right, cy, _wrap(consumer, name_font, col_w), name_font, BLACK, 34)
    cy += 6
    cy = _draw_right(draw, x_right, cy, _wrap(consumer_addr, body_font, col_w), body_font, BLACK, 26)
    if consumer_mobile:
        cy += 4
        cy = _draw_right_labeled(draw, x_right, cy, "Mobile : ", consumer_mobile, label_font, body_font, BLACK, 26)
    cy += 12
    draw.line((x_left, cy, x_right, cy), fill=BLACK, width=2)
    cy += 16
    cy = _draw_right_labeled(draw, x_right, cy, "ID : ", str(qid), label_font, body_font, BLACK, 28)
    cy = _draw_right_labeled(draw, x_right, cy, "Date : ", str(formatted_date or ""), label_font, body_font, BLACK, 28)
    cy = _draw_right_labeled(draw, x_right, cy, "Expiry Date : ", str(expiry), label_font, body_font, BLACK, 28)
    cy = _draw_right_labeled(draw, x_right, cy, "By : ", str(by_name), label_font, body_font, BLACK, 28)
    if by_contact:
        _draw_right_labeled(draw, x_right, cy, "Contact : ", str(by_contact), label_font, body_font, BLACK, 28)

    fd, out_path = tempfile.mkstemp(prefix="dbsolar_cover_", suffix=".jpg")
    os.close(fd)
    # 595x841 px at 72dpi = 595x841 pt so xhtml2pdf fills A4 even if CSS size is ignored.
    page = canvas.convert("RGB").resize((595, 841), Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
    page.save(out_path, "JPEG", quality=90, dpi=(72, 72))
    return out_path.replace("\\", "/")


def render_cover_left_photo(master):
    """Portrait-crop the cover photo and save a temp JPEG. Empty string if unavailable."""
    import tempfile
    photo = None
    if master is not None:
        photo = _open_image(getattr(master, "proposal_cover_image", None))
    if photo is None:
        photo = _open_image(_static_cover_path())
    if photo is None:
        return ""
    fitted = _cover_fit(photo, 594, 1560)
    photo.close()
    fd, out_path = tempfile.mkstemp(prefix="dbsolar_cover_left_", suffix=".jpg")
    os.close(fd)
    fitted.convert("RGB").save(out_path, "JPEG", quality=85)
    return out_path.replace("\\", "/")


PROPOSAL_ABOUT_MEDIA = "quotation/master/proposal_about.jpg"


def _uploaded_about_path():
    try:
        path = os.path.join(str(settings.MEDIA_ROOT), PROPOSAL_ABOUT_MEDIA.replace("/", os.sep))
    except Exception:
        return None
    return path if os.path.isfile(path) else None


def _static_about_path():
    candidates = [
        settings.BASE_DIR / "static" / "quotation" / "proposal" / "about_page.jpg",
        settings.BASE_DIR / "asert" / "quotation" / "proposal" / "about_page.jpg",
        settings.BASE_DIR / "staticfiles" / "quotation" / "proposal" / "about_page.jpg",
        settings.BASE_DIR / "static" / "quotation" / "proposal" / "about_hero.png",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return str(path)
    return None


def render_about_photo(master=None):
    """About-page photo as temp JPEG for PDF (uploaded media or static default)."""
    import tempfile
    photo = _open_image(_uploaded_about_path())
    if photo is None:
        photo = _open_image(_static_about_path())
    if photo is None:
        return ""
    fitted = _cover_fit(photo, 1040, 480)
    photo.close()
    fd, out_path = tempfile.mkstemp(prefix="dbsolar_about_", suffix=".jpg")
    os.close(fd)
    fitted.convert("RGB").save(out_path, "JPEG", quality=85)
    return out_path.replace("\\", "/")


def about_image_public_url():
    if not _uploaded_about_path():
        return ""
    base = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/")
    return "{}/{}".format(base, PROPOSAL_ABOUT_MEDIA)
