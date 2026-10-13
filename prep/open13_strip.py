import re, sys, html as htmlmod

for name in sys.argv[1:]:
    src = open(f"/tmp/open13/{name}.html", encoding="utf-8", errors="replace").read()
    txt = re.sub(r"<script[\s\S]*?</script>", " ", src, flags=re.I)
    txt = re.sub(r"<style[\s\S]*?</style>", " ", txt, flags=re.I)
    txt = re.sub(r"<[^>]+>", "\n", txt)
    txt = htmlmod.unescape(txt)
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    out = "\n".join(lines)
    open(f"/tmp/open13/{name}.txt", "w", encoding="utf-8").write(out)
    print(name, len(out), "chars", len(lines), "lines")
    hrefs = sorted(set(re.findall(r'href="(/[^"#]*)"', src)))
    print(" hrefs:", " ".join(hrefs[:40]))
