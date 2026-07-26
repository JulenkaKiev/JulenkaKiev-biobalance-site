from playwright.sync_api import sync_playwright

OUT = "/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video/site_shots"
W, H = 390, 844

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=2)
    page.goto("http://localhost:5173/", wait_until="networkidle")
    page.wait_for_timeout(500)
    # hide sticky header/marquee for clean stitching, disable animations for deterministic capture
    page.add_style_tag(content="""
        .site-header, .marquee-bar, .sticky-cta { display: none !important; }
        * { animation-duration: 0s !important; transition-duration: 0s !important; }
        html { scroll-behavior: auto !important; }
    """)
    page.wait_for_timeout(300)

    positions = [0, 784, 1568, 2352, 3136, 3920, 4704]
    for i, y in enumerate(positions):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(400)
        page.screenshot(path=f"{OUT}/shot_{i:02d}.png")
        print(f"saved shot_{i:02d}.png at scrollY={y}")

    browser.close()
