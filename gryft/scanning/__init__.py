# Standard lib
import os
import shutil

HOME = os.getenv("HOME")
GRYFT_DIR = os.path.join(HOME, ".gryft")
GRYPE_CONFIG = os.path.join(GRYFT_DIR, ".grype.yaml")
SYFT_CONFIG = os.path.join(GRYFT_DIR, ".syft.yaml")
CONFIG_TEXT = "default-image-pull-source: registry"

if not os.path.exists(GRYFT_DIR):
    os.makedirs(GRYFT_DIR)
    with open(GRYPE_CONFIG, "w") as f:
        f.write(CONFIG_TEXT)
    with open(SYFT_CONFIG, "w") as f:
        f.write(CONFIG_TEXT)
