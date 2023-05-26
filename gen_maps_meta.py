words = [
    "import",
    "civilian",
    "sanctuary",
    "tube",
    "cancer",
    "repeat",
    "photography",
    "stroke",
    "spit",
    "curtain",
    "merit",
    "slump",
    "speculate",
    "care",
    "slam",
    "drink",
    "motorist",
    "braid",
    "density",
    "overview",
    "cheque",
    "habitat",
    "extort",
    "concession",
    "stop",
    "coerce",
    "wardrobe",
    "stake",
    "performer",
    "tough",
    "television",
    "departure",
]

gen_object = {}

#     0: {
#         "title": "soft whisper",
#         "videos": {
#             0: "https://example.com/v0s0",
#             1: "https://example.com/v0s0",
#             2: "https://example.com/v0s2"
#         }
#     },

for map_id in range(16):
    gen_object[map_id] = {
        "title": f"{words[map_id * 2]} {words[map_id * 2 + 1]}",
        "videos": {
            0: f"https://example.com/v{map_id}s0",
            1: f"https://example.com/v{map_id}s0",
            2: f"https://example.com/v{map_id}s2"
        }
    }
print(gen_object)
