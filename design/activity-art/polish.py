"""Final art-direction tweaks applied at build time, on top of the concept modules."""

# Sea and lake scenes whose water turns brown in the warm "golden" palette and
# reads as desert. Without golden, a Vintage map falls back to coastal (blue
# water). Sunset-at-sea scenes and muddy rivers keep golden on purpose.
NO_GOLDEN = {
    # water_a
    "surf-wave", "sup-paddler", "sup-dog", "sup-aerial", "kayak-paddler", "kayak-fjord", "kayak-orca", "raft-crew",
    "sail-yacht", "sail-lighthouse", "boat-ferry", "boat-dolphins", "island-palms", "island-map", "island-seaplane",
    "cruise-pelican", "jetski-ride", "jetski-wake", "jetski-jump",
    # water_b
    "kite-rider", "kite-board", "kite-beach", "dolphin-leap", "turtle-breath", "shark-boat", "cliff-leap", "cliff-splash",
    "falls-swimmer", "fish-hooked", "fish-boat", "fish-bobber", "beach-parasol",
    # wildlife
    "whale-tail", "whale-boat", "dolphinwatch-leap", "dolphinwatch-pod", "dolphinwatch-bow", "np-mountain-lake", "waterfalls-boat",
    # air_snow
    "parasail-boat", "parasail-beach", "seaplane-floats", "seaplane-lagoon", "seaplane-dock", "heli-island",
    # transport, moments
    "gondola-bridge", "gondola-gondolier", "honeymoon-bungalow",
}


def apply(concept):
    if concept.id in NO_GOLDEN:
        concept.palettes = [p for p in concept.palettes if p != "golden"]
