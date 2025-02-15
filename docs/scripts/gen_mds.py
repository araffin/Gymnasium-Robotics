__author__ = "Feng Gu"
__email__ = "contact@fenggu.me"

"""
   isort:skip_file
"""

import os
import re

from tqdm import tqdm
from itertools import chain

pattern = re.compile(r"(?<!^)(?=[A-Z])")

readme_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "README.md",
)

fetch_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "gymnasium_robotics",
    "envs",
    "fetch",
)

hand_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "gymnasium_robotics",
    "envs",
    "hand",
)

output_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "envs",
)

# regex to find the class name
class_p = re.compile(r"class\s([\w]+)\(.*")


# write to file
def generate(name, docstring, type):
    snake_env_name = pattern.sub(" ", name).lower()
    title_env_name = snake_env_name.replace("_", " ").title()
    output = os.path.join(output_path, type, name + ".md")
    front_matter = f"""---

autogenerated:
title: {title_env_name}
---
"""
    title = f"# {title_env_name}"
    if docstring is None:
        docstring = "No information provided"
    all_text = f"""{front_matter}
{title}
{docstring}
                """

    with open(output, "w") as f:
        f.write(all_text)
        f.close()


# generate markdown for envs
for (root, dirs, file) in tqdm(chain(os.walk(fetch_path), os.walk(hand_path))):
    for f in file:
        # skip __init__.py and __pycache__
        if not f.endswith(".py") or f.startswith("__"):
            continue
        else:
            type = "fetch" if "fetch" in root else "hand"
            curr_path = os.path.join(root, f)
            curr_file = open(curr_path)
            lines = curr_file.readlines()
            docstrings = {}
            docstring = ""
            curr_class = ""
            match = False

            for line in lines:
                if line.strip() == "":
                    trimmed = "\n"
                # remove leading whitespace
                else:
                    trimmed = line.lstrip()

                if trimmed.startswith("class"):
                    class_name = re.search(class_p, trimmed).group(1)
                    # ignore Py classes and remove the "Mujoco" suffix
                    if "Py" not in class_name:
                        class_name = class_name[:-3]
                        if class_name.startswith("Mujoco"):
                            curr_class = class_name[6:]

                if trimmed.startswith('"""'):
                    match = not match

                # if we are in a docstring
                if match:
                    if trimmed.startswith('"""'):
                        trimmed = trimmed[3:]
                    docstring += trimmed
                # populating the dict
                else:
                    if len(docstring) > 0:
                        if len(curr_class) > 0:
                            docstrings[curr_class] = docstring
                        docstring = ""
                        curr_class = ""

            # write to file
            for name, docstring in docstrings.items():
                generate(name, docstring, type)
