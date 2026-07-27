import json

words = json.load(open("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video2/voice_short/words2.json"))

groups = [
    (0, 7),
    (8, 12),
    (13, 19),
    (20, 24),
    (25, 28),
]

def fmt(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Inter,72,&H0056A1C9,&H00E7F1F7,&H00110F0D,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,2,60,60,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = [header]

for gi, (i0, i1) in enumerate(groups):
    seg = words[i0:i1+1]
    start = seg[0]["start"]
    end = seg[-1]["end"]
    parts = []
    prev_end = start
    for w in seg:
        gap = w["start"] - prev_end
        dur = w["end"] - w["start"]
        k_cs = round((gap + dur) * 100)
        if k_cs < 1:
            k_cs = 1
        parts.append(f"{{\\k{k_cs}}}{w['word']}")
        prev_end = w["end"]
    text = " ".join(parts)
    lines.append(f"Dialogue: 0,{fmt(start)},{fmt(end+0.15)},Karaoke,,0,0,0,,{text}\n")

with open("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video2/captions_short.ass", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("saved captions_short.ass with", len(groups), "lines")

scene_word_bounds = [7, 12, 19, 24, 28]
cuts = [0.0]
for idx in scene_word_bounds[:-1]:
    end_a = words[idx]["end"]
    start_b = words[idx + 1]["start"]
    cuts.append(round((end_a + start_b) / 2, 3))
cuts.append(round(words[scene_word_bounds[-1]]["end"] + 0.4, 3))
durations = [round(cuts[i+1] - cuts[i], 3) for i in range(len(cuts)-1)]
print("scene cut points:", cuts)
print("scene durations:", durations)
json.dump({"cuts": cuts, "durations": durations}, open("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video2/scene_timing_short.json", "w"))
