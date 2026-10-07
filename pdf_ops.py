"""PDF operations: page info and preview rendering."""

import pymupdf


class PdfError(Exception):
    """A user-facing problem with the uploaded PDF; `code` is translated by the frontend."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def open_pdf(data: bytes) -> pymupdf.Document:
    return pymupdf.open(stream=data, filetype="pdf")


def validate_pdf(data: bytes) -> int:
    """Return the page count, or raise PdfError for anything we cannot stamp."""
    if not data.lstrip()[:1024].startswith(b"%PDF"):
        raise PdfError("not_pdf")
    try:
        with open_pdf(data) as doc:
            if doc.needs_pass:
                raise PdfError("encrypted")
            if doc.page_count == 0:
                raise PdfError("no_pages")
            return doc.page_count
    except PdfError:
        raise
    except Exception:
        raise PdfError("corrupt") from None


def page_sizes(data: bytes) -> list[dict]:
    """Visual page sizes in points (CropBox after rotation)."""
    with open_pdf(data) as doc:
        return [{"w": p.rect.width, "h": p.rect.height} for p in doc]


def render_page(data: bytes, index: int, zoom: float) -> bytes:
    """Render one page to PNG as it appears on screen (rotation and CropBox applied)."""
    with open_pdf(data) as doc:
        page = doc[index]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        return pix.tobytes("png")


def stamp_rect(page: pymupdf.Page, x_rel: float, y_rel: float, aspect: float) -> pymupdf.Rect:
    """Stamp rectangle in visual page space, centred on the click and kept inside the page.

    Width is 7/21 of the visual page width (7 cm on A4 portrait); height follows the stamp aspect.
    """
    page_w, page_h = page.rect.width, page.rect.height
    w = page_w * 7 / 21
    h = w / aspect
    if h > page_h:  # extremely flat pages
        h = page_h
        w = h * aspect
    cx = min(max(x_rel * page_w, w / 2), page_w - w / 2)
    cy = min(max(y_rel * page_h, h / 2), page_h - h / 2)
    return pymupdf.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def stamp_pdf(data: bytes, index: int, x_rel: float, y_rel: float, png: bytes, aspect: float) -> bytes:
    """Insert the stamp image so it appears upright at the clicked spot; return the new PDF."""
    with open_pdf(data) as doc:
        page = doc[index]
        visual = stamp_rect(page, x_rel, y_rel, aspect)
        # Map to unrotated (CropBox-relative) coordinates, then insert with /Rotate temporarily
        # cleared: PyMuPDF misplaces images on rotated pages whose CropBox is offset.
        rotation = page.rotation
        rect = visual * page.derotation_matrix
        page.set_rotation(0)
        page.insert_image(rect, stream=png, rotate=rotation)
        page.set_rotation(rotation)
        return doc.tobytes(garbage=3, deflate=True)
