"""
Generates the pixel-perfect brand icon for Yoink Social matching the frontend SVG:
- Dark cyber glass rounded squircle (#0a0f1d -> #060911)
- Subtle cyan outer glow
- Sleek cyan / glass border
- Frosted glass reflection arc at the top
- Futuristic neon monogram 'Y' (Neon Cyan left arm, Neon Purple right arm, Sky Blue stem)
- Suction pulse arrowhead pointing down
- 3 glowing node circles at endpoints and junction
- Multi-resolution Windows ICO (16, 24, 32, 48, 64, 128, 256)
- High-resolution 512x512 PNG
- Inno Setup Wizard BMPs
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter

def render_yoink_logo(target_size=512):
    # Render on 4x supersampled canvas (2080x2080)
    dim = 2080
    scale = dim / 52.0  # 40 pixels per SVG coordinate unit

    def sc(x, y):
        return (x * scale, y * scale)

    # Master canvas with transparent background
    canvas = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))

    # 1. Soft Outer Neon Glow
    glow_box = [sc(2, 2)[0] - 6 * scale, sc(2, 2)[1] - 6 * scale,
                sc(50, 50)[0] + 6 * scale, sc(50, 50)[1] + 6 * scale]
    glow_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.rounded_rectangle(glow_box, radius=int(17 * scale), fill=(0, 242, 254, 70))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(int(10 * scale)))
    canvas = Image.alpha_composite(canvas, glow_layer)

    # 2. Main Dark Cyber Card (Squircle)
    card_box = [sc(2, 2)[0], sc(2, 2)[1], sc(50, 50)[0], sc(50, 50)[1]]
    radius = int(14 * scale)

    card_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_layer)

    # Render gradient into a temp image
    grad_img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(grad_img)
    y_start, y_end = int(card_box[1]), int(card_box[3])
    for y in range(y_start, y_end + 1):
        t = (y - y_start) / float(y_end - y_start)
        # Deep space dark glass: #101728 to #080c14
        r = int(16 * (1 - t) + 8 * t)
        g = int(23 * (1 - t) + 12 * t)
        b = int(40 * (1 - t) + 20 * t)
        grad_draw.line([(card_box[0], y), (card_box[2], y)], fill=(r, g, b, 255))

    # Mask gradient to squircle
    card_mask = Image.new("L", (dim, dim), 0)
    mask_draw = ImageDraw.Draw(card_mask)
    mask_draw.rounded_rectangle(card_box, radius=radius, fill=255)
    card_layer.paste(grad_img, (0, 0), card_mask)

    # 3. Top Frosted Glass Reflection Arc
    refl_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    refl_draw = ImageDraw.Draw(refl_layer)
    refl_points = []
    steps = 50
    for i in range(steps + 1):
        t = i / float(steps)
        # Quadratic bezier from (4, 16) through (26, 5) to (48, 16)
        x = (1 - t)**2 * 4 + 2 * (1 - t) * t * 26 + t**2 * 48
        y = (1 - t)**2 * 16 + 2 * (1 - t) * t * 5 + t**2 * 16
        refl_points.append(sc(x, y))
    refl_points.append(sc(48, 2))
    refl_points.append(sc(4, 2))
    refl_draw.polygon(refl_points, fill=(255, 255, 255, 38))

    refl_masked = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    refl_masked.paste(refl_layer, (0, 0), card_mask)
    card_layer = Image.alpha_composite(card_layer, refl_masked)

    # 4. Glass Border
    border_draw = ImageDraw.Draw(card_layer)
    border_draw.rounded_rectangle(card_box, radius=radius, outline=(0, 242, 254, 190), width=int(1.6 * scale))

    canvas = Image.alpha_composite(canvas, card_layer)

    # 5. Neon Glow Layer for Y Monogram & Arrow
    stroke_w = int(4.8 * scale)
    p_left = sc(14, 13)
    p_right = sc(38, 13)
    p_center = sc(26, 27)
    p_stem_bottom = sc(26, 36)
    arrow_pts = [sc(26, 44), sc(18, 35), sc(26, 38), sc(34, 35)]

    neon_glow_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    neon_glow_draw = ImageDraw.Draw(neon_glow_layer)

    glow_stroke = stroke_w + int(10 * scale)
    neon_glow_draw.line([p_left, p_center], fill=(0, 242, 254, 220), width=glow_stroke)
    neon_glow_draw.line([p_right, p_center], fill=(192, 132, 252, 220), width=glow_stroke)
    neon_glow_draw.line([p_center, p_stem_bottom], fill=(56, 189, 248, 220), width=glow_stroke)
    neon_glow_draw.polygon(arrow_pts, fill=(0, 242, 254, 220))

    # Blur the neon aura
    neon_glow_layer = neon_glow_layer.filter(ImageFilter.GaussianBlur(int(5 * scale)))
    canvas = Image.alpha_composite(canvas, neon_glow_layer)

    # Sharp Foreground Monogram & Nodes
    fg_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    fg_draw = ImageDraw.Draw(fg_layer)
    half_sw = stroke_w // 2

    # Helper to draw a capsule with smooth gradient
    def draw_gradient_capsule(p1, p2, color1, color2, width):
        # 1. Create solid shape mask
        arm_mask = Image.new("L", (dim, dim), 0)
        m_draw = ImageDraw.Draw(arm_mask)
        hw = width // 2
        m_draw.line([p1, p2], fill=255, width=width)
        m_draw.ellipse([p1[0] - hw, p1[1] - hw, p1[0] + hw, p1[1] + hw], fill=255)
        m_draw.ellipse([p2[0] - hw, p2[1] - hw, p2[0] + hw, p2[1] + hw], fill=255)

        # 2. Render smooth gradient bounding box
        arm_img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        # Vector from p1 to p2
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        len_sq = dx * dx + dy * dy
        if len_sq == 0:
            return

        min_x = max(0, int(min(p1[0], p2[0]) - hw - 2))
        max_x = min(dim, int(max(p1[0], p2[0]) + hw + 2))
        min_y = max(0, int(min(p1[1], p2[1]) - hw - 2))
        max_y = min(dim, int(max(p1[1], p2[1]) + hw + 2))

        # We can draw perpendicular slices along the arm
        steps = int(math.hypot(dx, dy) * 2)
        p_img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(p_img)
        # Normal vector perpendicular to arm
        nx = -dy / math.hypot(dx, dy)
        ny = dx / math.hypot(dx, dy)
        span = hw + 10
        for i in range(steps + 1):
            t = i / float(steps)
            cx = p1[0] + dx * t
            cy = p1[1] + dy * t
            r = int(color1[0] * (1 - t) + color2[0] * t)
            g = int(color1[1] * (1 - t) + color2[1] * t)
            b = int(color1[2] * (1 - t) + color2[2] * t)
            p_draw.line([(cx - nx * span, cy - ny * span), (cx + nx * span, cy + ny * span)], fill=(r, g, b, 255), width=3)

        # Mask exactly to the capsule
        arm_img.paste(p_img, (0, 0), arm_mask)
        return arm_img

    # Left Arm: Neon Cyan (#00f2fe to #38bdf8)
    left_arm = draw_gradient_capsule(p_left, p_center, (0, 242, 254), (56, 189, 248), stroke_w)
    fg_layer = Image.alpha_composite(fg_layer, left_arm)

    # Right Arm: Neon Purple (#c084fc to #818cf8)
    right_arm = draw_gradient_capsule(p_right, p_center, (192, 132, 252), (129, 140, 248), stroke_w)
    fg_layer = Image.alpha_composite(fg_layer, right_arm)

    # Center Stem: Sky Blue (#38bdf8)
    stem_img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(stem_img)
    s_draw.line([p_center, p_stem_bottom], fill=(56, 189, 248, 255), width=stroke_w)
    s_draw.ellipse([p_stem_bottom[0] - half_sw, p_stem_bottom[1] - half_sw, p_stem_bottom[0] + half_sw, p_stem_bottom[1] + half_sw], fill=(56, 189, 248, 255))
    fg_layer = Image.alpha_composite(fg_layer, stem_img)

    # Arrowhead polygon
    arrow_img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    arr_draw = ImageDraw.Draw(arrow_img)
    arr_draw.polygon(arrow_pts, fill=(0, 242, 254, 255))
    fg_layer = Image.alpha_composite(fg_layer, arrow_img)

    # Node Circles Layer
    nodes_layer = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    nodes_draw = ImageDraw.Draw(nodes_layer)

    def draw_node(center, r_outer, r_inner, outer_color):
        cx, cy = center
        nodes_draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=outer_color)
        nodes_draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(255, 255, 255, 255))

    # Left node (14, 13)
    draw_node(p_left, 2.8 * scale, 1.8 * scale, (0, 242, 254, 255))
    # Right node (38, 13)
    draw_node(p_right, 2.8 * scale, 1.8 * scale, (192, 132, 252, 255))
    # Junction node (26, 27)
    draw_node(p_center, 3.2 * scale, 2.1 * scale, (56, 189, 248, 255))

    fg_layer = Image.alpha_composite(fg_layer, nodes_layer)
    canvas = Image.alpha_composite(canvas, fg_layer)

    # Downsample to target_size using high-quality Lanczos resampling
    final_img = canvas.resize((target_size, target_size), Image.Resampling.LANCZOS)
    return final_img

def main():
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    os.makedirs(icons_dir, exist_ok=True)

    print("Rendering high-res Yoink Social brand logo...")
    icon_512 = render_yoink_logo(512)

    # Save 512x512 PNG
    png_path = os.path.join(icons_dir, "app_icon.png")
    icon_512.save(png_path, "PNG")
    print(f"[OK] Saved PNG: {png_path}")

    # Generate multi-resolution Windows ICO (16, 24, 32, 48, 64, 128, 256)
    ico_path = os.path.join(icons_dir, "app_icon.ico")
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_512.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"[OK] Saved Multi-Resolution ICO: {ico_path}")

    # Inno Setup Small Wizard BMP (55x58 standard Inno Setup small icon)
    # Inno Setup BMPs must be 24-bit RGB BMP (not RGBA)
    wiz_icon = render_yoink_logo(55)
    wiz_bmp = Image.new("RGB", (55, 58), (11, 15, 25))
    # Paste centered
    wiz_bmp.paste(wiz_icon, (0, 1), wiz_icon)
    bmp_small_path = os.path.join(icons_dir, "wizard_small.bmp")
    wiz_bmp.save(bmp_small_path, "BMP")
    print(f"[OK] Saved Inno Setup Small BMP: {bmp_small_path}")

if __name__ == "__main__":
    main()
