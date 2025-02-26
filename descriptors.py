import random

# Categorized descriptor lists
mood_emotion = [
    "uplifting", "melancholic", "bittersweet", "intense", "haunting", "joyful", "eerie", "triumphant",
    "sentimental", "sorrowful", "hopeful", "nostalgic", "dreamy", "aggressive", "ominous", "soothing",
    "passionate", "mysterious", "wistful", "serene", "dramatic", "brooding", "contemplative", "warm",
    "playful", "moody", "devastating", "tranquil", "forlorn", "romantic", "cathartic", "tense", "chaotic"
]

tempo_speed = [
    "slow", "fast", "mid-tempo", "driving", "lethargic", "energetic", "rapid", "crawling", "galloping",
    "pulsing", "steady", "fluctuating", "erratic", "brisk", "laid-back", "dragging", "quick-paced",
    "flowing", "sprinting", "urgent", "methodical", "unstable", "dynamic", "frenzied", "choppy",
    "pounding", "swaying", "relentless", "creeping", "rumbling", "unsteady", "subdued"
]

texture_tone = [
    "rich", "airy", "dense", "sparse", "crisp", "resonant", "hollow", "shimmering", "raw", "polished",
    "grungy", "smooth", "sharp", "rough", "muddy", "bright", "warm", "dark", "clean", "distorted",
    "velvety", "brittle", "piercing", "booming", "buzzy", "echoing", "weighty", "lush", "expansive",
    "muted", "soft", "vibrant", "pristine", "crackling", "hazy", "ringing", "silky", "metallic"
]

instrumentation_arrangement = [
    "orchestral", "stripped-down", "layered", "bass-heavy", "drum-driven", "vocal-driven", "minimalist",
    "intricate", "chaotic", "percussive", "swelling", "hypnotic", "dynamic", "plucky", "punchy", "subdued",
    "glitchy", "harmonic", "droning", "whirling", "free-flowing", "melodic", "sharp-edged", "booming",
    "sweeping", "cascading", "bouncy", "staccato", "rolling", "fluid", "abrupt", "fluttering", "resonant"
]

vocal_style_delivery = [
    "whispered", "breathy", "soaring", "guttural", "crooning", "raspy", "delicate", "operatic", "fierce",
    "monotone", "robotic", "ethereal", "strained", "dynamic", "echoing", "hushed", "gritty", "sweet",
    "impassioned", "intense", "nasal", "angelic", "husky", "bold", "throaty", "raw", "emotive", "spoken",
    "yelping", "soulful", "smooth", "ghostly", "commanding", "snarling", "whispery", "smoky", "piercing"
]

lyrical_content_theme = [
    "romantic", "introspective", "poetic", "abstract", "surreal", "cryptic", "rebellious", "tragic",
    "anthemic", "uplifting", "dark", "storytelling", "absurd", "longing", "nostalgic", "confessional",
    "playful", "sarcastic", "philosophical", "metaphorical", "hopeful", "passionate", "reflective",
    "fantastical", "ironic", "humorous", "earnest", "ambiguous", "vivid", "dramatic", "empowering"
]

# Function to generate a song description
def generate_song_description():
    return ", ".join([
        ", ".join(random.sample(mood_emotion, random.randint(1, 2))),
        ", ".join(random.sample(tempo_speed, random.randint(1, 2))),
        ", ".join(random.sample(texture_tone, random.randint(1, 2))),
        ", ".join(random.sample(instrumentation_arrangement, random.randint(1, 2))),
        ", ".join(random.sample(vocal_style_delivery, random.randint(1, 2))),
        ", ".join(random.sample(lyrical_content_theme, random.randint(1, 2)))
    ])


if __name__ == "__main__":
    print(generate_song_description())