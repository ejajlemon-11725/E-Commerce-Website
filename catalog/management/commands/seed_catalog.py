import random
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from catalog.models import Category, Product
from django.utils.text import slugify

CATS = [
    "Different types of Books",
    "Different Lab tools",
    "Different Class notes",
    "Different Electronics & Gadgets",
    "Different Departmental T-Shirts",
    "Different Bags & Accessories",
]

SAMPLES = {
    "Different types of Books": [
        "Physics Guide (SSC)", "Higher Math Workbook", "Programming in Python",
        "Bangla 1st Paper Notes", "English Grammar Mastery"
    ],
    "Different Lab tools": [
        "Microscope", "Test Tube Set", "Digital Scale", "Beaker Set", "pH Meter"
    ],
    "Different Class notes": [
        "ICT Chapter 3 Notes", "Biology One-Shot Notes", "BGS Map Workbook",
        "Bangla 2nd Paper Model", "Chemistry Formula Sheet"
    ],
    "Different Electronics & Gadgets": [
        "Scientific Calculator", "USB Flash Drive 64GB", "Bluetooth Earbuds",
        "Raspberry Pi Kit", "LED Desk Lamp"
    ],
    "Different Departmental T-Shirts": [
        "CSE Dept Tee (Black)", "EEE Dept Tee (White)", "ME Dept Tee (Navy)",
        "Civil Dept Tee (Maroon)", "BBA Dept Tee (Grey)"
    ],
    "Different Bags & Accessories": [
        "Laptop Backpack", "Lab Tool Carry Bag", "Pencil Pouch Set",
        "Sling Bag", "Water Bottle (Steel)"
    ],
}

def ensure_font():
    # Try to get a default PIL font; system font fallback if available
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def make_image(text, save_path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    W, H = 900, 620
    bg = (random.randint(80,200), random.randint(120,220), random.randint(160,240))
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    font = ensure_font()
    # word-wrap rudimentary
    lines = []
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if len(test) > 20:
            lines.append(line)
            line = w
        else:
            line = test
    if line: lines.append(line)
    y = H//2 - (len(lines)*24)//2
    for ln in lines:
        tw, th = draw.textlength(ln, font=font), 20
        draw.text(((W - tw)//2, y), ln, fill=(255,255,255), font=font)
        y += th + 8
    img.save(save_path)

class Command(BaseCommand):
    help = "Seed categories, products, and generate placeholder images."

    def handle(self, *args, **kwargs):
        media_root = Path(settings.MEDIA_ROOT)
        created_cats = {}
        for name in CATS:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slugify(name)})
            created_cats[name] = cat

        for catname, titles in SAMPLES.items():
            cat = created_cats[catname]
            for title in titles:
                price = random.randint(300, 1600)
                old_price = price + random.randint(50, 400) if random.random() > 0.4 else None
                stock = random.randint(0, 50)
                slug = slugify(title)
                p, created = Product.objects.get_or_create(
                    category=cat, title=title,
                    defaults=dict(
                        slug=slug, price=price, old_price=old_price,
                        stock=stock, short_description=f"{title} — demo product in {catname}",
                        is_active=True
                    )
                )
                # generate image
                if created or not p.image:
                    rel = Path('products') / cat.slug / f"{slug}.jpg"
                    make_image(title, media_root / rel)
                    p.image = str(rel).replace("\\", "/")
                    p.save()

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
