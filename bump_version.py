import argparse
import json
import os
import re


# Version bump functions
def parse_version(version: str):
    """Parse the version string into components."""
    pattern = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:-([\w]+)\.(\d+))?")
    match = pattern.match(version)
    if not match:
        raise ValueError(f"Invalid version: {version}")

    major, minor, patch, env, build = match.groups()
    return {
        "major": int(major),
        "minor": int(minor),
        "patch": int(patch),
        "env": env if env else "",
        "build": int(build) if build else 0,
    }


def bump_version(version: str, bump_type: str) -> str:
    version_parts = parse_version(version)
    if bump_type == "major":
        version_parts["major"] += 1
        version_parts["minor"] = 0
        version_parts["patch"] = 0
        version_parts["env"] = ""
    elif bump_type == "minor":
        version_parts["minor"] += 1
        version_parts["patch"] = 0
        version_parts["build"] = 1
    elif bump_type == "patch":
        version_parts["patch"] += 1
        version_parts["env"] = ""
    elif bump_type == "build":
        if version_parts["env"]:
            version_parts["build"] += 1
        else:
            raise ValueError("Cannot bump build version of a non-env version")
    elif bump_type == "release":
        version_parts["env"] = "release"
        version_parts["build"] = 1
    elif bump_type == "launch":
        version_parts["env"] = ""
    else:
        raise ValueError(f"Unsupported bump type: {bump_type}")

    new_version = f'{version_parts["major"]}.{version_parts["minor"]}.{version_parts["patch"]}'
    if version_parts["env"]:
        new_version += f'-{version_parts["env"]}.{version_parts["build"]}'
    return new_version


# Update version in package.json
def bump_from_package_json(file_path: str, bump_type: str):
    with open(file_path, "r") as f:
        data = json.load(f)
    old_version = data.get("version", "0.0.0")
    new_version = bump_version(old_version, bump_type)
    data["version"] = new_version
    with open(file_path, "w", encoding="UTF-8") as f:
        json.dump(data, f, indent=2)
    return new_version  # Return the new version


# Update version in build.gradle
def bump_from_build_gradle(file_path: str, bump_type: str):
    with open(file_path, "r") as f:
        data = f.read()
    pattern = re.compile(r"version = '(\d+)\.(\d+)\.(\d+)(?:-([\w]+)\.(\d+))?'")
    matched = pattern.search(data)

    old_version = "0.0.0"
    if matched:
        major, minor, patch, env, build = matched.groups()
        if env:
            old_version = f"{major}.{minor}.{patch}-{env}.{build}"
        else:
            old_version = f"{major}.{minor}.{patch}"

    new_version = bump_version(old_version, bump_type)
    updated_data = pattern.sub(f"version = '{new_version}'", data)

    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(updated_data)

    return new_version  # Return the new version


def main():
    parser = argparse.ArgumentParser(description="Bump version of a package")
    parser.add_argument("--file_path", required=True, type=str, help="The path to the file to bump version")
    parser.add_argument(
        "--type", required=True, type=str, choices=["major", "minor", "patch", "build", "release", "launch"], help="The type of version bump"
    )
    args = parser.parse_args()

    file_path = args.file_path
    bump_type = args.type

    file_name = os.path.basename(file_path)
    if file_name == "package.json":
        new_version = bump_from_package_json(file_path, bump_type)
    elif file_name == "build.gradle":
        new_version = bump_from_build_gradle(file_path, bump_type)
    else:
        raise ValueError("Unsupported file for version bumping.")

    print(new_version)  # Output the new version


if __name__ == "__main__":
    main()