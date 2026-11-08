import os
import re
import argparse
import urllib.parse
from bs4 import BeautifulSoup
import pymupdf
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://egyankosh.ac.in"
visited_urls = set()

ALLOWED_SEMESTERS = {
    "Semester-I",
    "Semester-II",
    "Semester-III",
    "Semester-IV", 
    "semester-1",
    "semester-2",
    "semester-3",
    "semester-4"
}
ALLOWED_SEMESTERS_NORMALIZED = {semester.casefold() for semester in ALLOWED_SEMESTERS}
SUBJECT_CONTAINER_TITLES = {
    "ignou self learning material",
    "ignou self learning material slm",
    "self learning material",
    "self learning material slm",
    "slm",
}

def sanitize_name(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:120]  # Avoid Windows long-path limits

def is_subject_container(title: str) -> bool:
    normalized = re.sub(r"[^\w]+", " ", title.casefold()).strip()
    return normalized in SUBJECT_CONTAINER_TITLES

def is_unit_pdf(page_title: str, file_name: str, link_text: str) -> bool:
    unit_pattern = re.compile(r"\bunits?\s*[-_]?\s*\d*\b", re.IGNORECASE)
    return any(unit_pattern.search(value) for value in (page_title, file_name, link_text))

def is_unit_title(title: str) -> bool:
    unit_pattern = re.compile(r"\bunits?\s*[-_]?\s*\d*\b", re.IGNORECASE)
    return bool(unit_pattern.search(title))

def is_block_pdf(page_title: str, file_name: str, link_text: str) -> bool:
    block_pattern = re.compile(r"\bblocks?\s*[-_]?\s*\d*\b", re.IGNORECASE)
    return any(block_pattern.search(value) for value in (page_title, file_name, link_text))

def get_soup(url: str):
    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=30)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
    return None

def get_clean_title(soup: BeautifulSoup, default="Unknown_Section") -> str:
    """Accurately identifies the subject/block/item heading from eGyanKosh pages."""
    # Check page-header or main headings
    header = soup.find(["h1", "h2", "h3"], class_=lambda c: c and "page-header" in c)
    if not header:
        header = soup.find(["h1", "h2"])
    
    if header:
        clone = BeautifulSoup(str(header), "html.parser")
        for tag in clone.find_all(class_=["badge", "glyphicon", "label"]):
            tag.decompose()
        text = clone.get_text().strip()
        text = re.sub(r"(Community|Collection)\s+home\s+page.*", "", text, flags=re.IGNORECASE).strip()
        if text and text.lower() not in {"dspace jspui", "egyankosh", "home"}:
            return sanitize_name(text)

    # Check breadcrumb trail
    breadcrumbs = soup.find(["ol", "ul"], class_=lambda c: c and "breadcrumb" in c)
    if breadcrumbs:
        items = [li.get_text().strip() for li in breadcrumbs.find_all("li") if li.get_text().strip()]
        if items:
            last = items[-1]
            if last.lower() not in {"home", "dspace jspui"}:
                return sanitize_name(last)

    return default

def get_main_content(soup: BeautifulSoup):
    """Restricts link discovery to the main central column to prevent sidebar bleeding."""
    main = soup.find("div", {"id": "content"}) or soup.find("main") or soup.find("div", class_="main-content")
    return main if main else soup

def get_child_links(content_area):
    """Returns community, collection, and item links without navigation links."""
    links = []
    for heading in content_area.find_all(["h3", "h4"]):
        heading_text = heading.get_text(" ", strip=True).casefold()
        if heading_text not in {
            "sub-communities within this community",
            "collections in this community",
        }:
            continue

        section = heading.find_parent("div", class_="col-md-12")
        if section:
            links.extend(section.select(".list-group a[href]"))

    for table in content_area.select("table.table"):
        links.extend(table.select('a[href*="/handle/123456789/"]'))

    child_links = []
    seen_urls = set()
    base_url = urllib.parse.urlparse(BASE_URL)

    for link in links:
        href = link["href"]
        if any(key in href for key in ["browse", "sort_by=", "offset=", "mode=full"]):
            continue

        parsed_url = urllib.parse.urlparse(href)
        if parsed_url.netloc and parsed_url.netloc.casefold() != base_url.netloc.casefold():
            continue

        path = "/" + parsed_url.path.lstrip("/")
        if not path.startswith("/handle/123456789/"):
            continue

        full_url = urllib.parse.urlunparse(
            (base_url.scheme, base_url.netloc, path, "", parsed_url.query, "")
        )
        if full_url not in seen_urls:
            seen_urls.add(full_url)
            child_links.append((full_url, link.get_text().strip()))

    return child_links

def crawl_tree(
    current_url: str,
    current_dir: str,
    inside_semester: bool = False,
    semester_root: bool = False,
    subject_dir: str | None = None,
    subject_name: str | None = None,
):
    """
    Crawls semester contents and saves all PDFs under Semester -> Subject folders.
    """
    if current_url in visited_urls:
        return
    visited_urls.add(current_url)

    soup = get_soup(current_url)
    if not soup:
        return

    content_area = get_main_content(soup)

    node_title = get_clean_title(soup)
    if inside_semester and not semester_root and subject_dir is None:
        folder_name = subject_name or node_title
        if not is_subject_container(folder_name):
            subject_dir = os.path.join(current_dir, sanitize_name(folder_name))

    download_dir = subject_dir or current_dir

    # Keep block PDFs, but omit unit PDFs and other non-block downloads.
    pdf_links = []
    seen_pdf_urls = set()
    for link in content_area.find_all("a", href=True):
        href = link["href"]
        if "/bitstream/" in href and urllib.parse.urlparse(href).path.lower().endswith(".pdf"):
            pdf_url = urllib.parse.urljoin(BASE_URL, href)
            if pdf_url in seen_pdf_urls:
                continue
            seen_pdf_urls.add(pdf_url)

            raw_name = os.path.basename(urllib.parse.urlparse(href).path)
            file_name = urllib.parse.unquote(raw_name)
            link_text = link.get_text().strip()
            if is_unit_pdf(node_title, file_name, link_text):
                print(f"[-] Skipping unit PDF: {file_name}")
            elif is_block_pdf(node_title, file_name, link_text):
                pdf_links.append(link)
            else:
                print(f"[-] Skipping non-block PDF: {file_name}")

    if pdf_links and inside_semester:
        os.makedirs(download_dir, exist_ok=True)
        for link in pdf_links:
            pdf_url = urllib.parse.urljoin(BASE_URL, link["href"])
            raw_path = urllib.parse.urlparse(link["href"]).path
            raw_name = os.path.basename(raw_path)
            clean_name = sanitize_name(urllib.parse.unquote(raw_name))

            if not clean_name.lower().endswith(".pdf"):
                clean_name += ".pdf"

            file_path = os.path.join(download_dir, clean_name)
            if not os.path.exists(file_path):
                print(f"[+] Downloading: {file_path}")
                try:
                    r = requests.get(pdf_url, headers=HEADERS, stream=True, verify=False, timeout=60)
                    if r.status_code == 200:
                        with open(file_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    f.write(chunk)
                except Exception as e:
                    print(f"[!] Download failed for {pdf_url}: {e}")
            else:
                print(f"[-] Already exists: {file_path}")

    # Find Semester 1 through 4 only at the top level.
    if not inside_semester:
        for child_url, title_text in get_child_links(content_area):
            if title_text.casefold() in ALLOWED_SEMESTERS_NORMALIZED:
                sem_dir = os.path.join(current_dir, sanitize_name(title_text))
                crawl_tree(
                    child_url,
                    current_dir=sem_dir,
                    inside_semester=True,
                    semester_root=True,
                )
        return

    child_links = [
        (url, link_text)
        for url, link_text in get_child_links(content_area)
        if url not in visited_urls
    ]

    for child_url, link_text in child_links:
        if is_unit_title(link_text):
            print(f"[-] Skipping unit: {link_text}")
            continue

        if semester_root:
            crawl_tree(
                child_url,
                current_dir=current_dir,
                inside_semester=True,
                subject_name=link_text or None,
            )
        elif subject_dir is None:
            crawl_tree(
                child_url,
                current_dir=current_dir,
                inside_semester=True,
                subject_name=link_text or None,
            )
        else:
            crawl_tree(
                child_url,
                current_dir=subject_dir,
                inside_semester=True,
                subject_dir=subject_dir,
            )

def extract_corpus(root_dir="data/courses", output_txt="data/corpus.txt"):
    """Reads every PDF under the course directory tree into one corpus."""
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"Course data directory not found: {root_dir}")

    os.makedirs(os.path.dirname(output_txt), exist_ok=True)
    full_corpus = []
    pdf_count = 0

    print("\nExtracting text from downloaded PDFs...")
    for dirpath, _, filenames in os.walk(root_dir):
        pdf_files = sorted([f for f in filenames if f.lower().endswith(".pdf")])
        for fname in pdf_files:
            file_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(file_path, root_dir)
            print(f"Reading: {rel_path}")

            try:
                doc = pymupdf.open(file_path)
                full_corpus.append(f"\n\n=== SOURCE: {rel_path} ===\n\n")
                for page in doc:
                    text = page.get_text()
                    text = re.sub(r"\n+", "\n", text)
                    full_corpus.append(text)
                doc.close()
                pdf_count += 1
            except Exception as e:
                print(f"[!] Error parsing {fname}: {e}")

    if not pdf_count:
        raise FileNotFoundError(f"No readable PDF files found under {root_dir}")

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(full_corpus))

    print(f"\nRead {pdf_count} PDFs. Combined training corpus saved to: {output_txt}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build a text corpus from IGNOU course PDFs.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--extract-only",
        action="store_true",
        help="(Legacy) Combine PDFs already present in data/courses without downloading files.",
    )
    mode.add_argument(
        "--crawl",
        action="store_true",
        help="Download MCA PDFs from eGyanKosh before extracting the local course PDFs.",
    )
    args = parser.parse_args()

    data_dir = "data/courses"
    corpus_file = "data/corpus.txt"

    if args.crawl:
        mca_root_url = "https://egyankosh.ac.in/handle/123456789/72354"
        print("Starting crawl of Semester I-IV...")
        crawl_tree(mca_root_url, current_dir=data_dir, inside_semester=False)
    else:
        print(f"Using course PDFs already stored locally in: {data_dir}")

    print("\nCompiling corpus from local course PDFs...")
    extract_corpus(root_dir=data_dir, output_txt=corpus_file)