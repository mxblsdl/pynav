check=$(poetry check)
if [ "$check" != "All set!" ]; then
    echo $check
    exit 1
fi

# Get version type arg and default
version_type=${1}

if [ "$version_type" != "patch" ] && [ "$version_type" != "minor" ] && [ "$version_type" != "major" ]; then
    >&2 echo "Warning: Invalid version type '$version_type'. Defaulting to 'patch'." 
    >&2 echo "Use one of: 'patch', 'minor', 'major'" 
    version_type="patch"
fi

# Extract version number from pyproject.toml
version=$(grep -oP '^version\s*=\s*"\K[0-9]+\.[0-9]+\.[0-9]+' pyproject.toml)

if [ -z "$version" ]; then
    version="0.0.0"  # Default if no releases exist
fi

# Split the version
major=$(echo "$version" | cut -d. -f1)
minor=$(echo "$version" | cut -d. -f2)
patch=$(echo "$version" | cut -d. -f3)

# Increment based on version type
case "$version_type" in
    "patch")
        patch=$((patch + 1))
        ;;
    "minor")
        minor=$((minor + 1))
        patch=0
        ;;
    "major")
        major=$((major + 1))
        minor=0
        patch=0
        ;;
esac


# Update the version in pyproject.toml
echo "Updating version to $major.$minor.$patch"
sed -i "s/^version = \".*\"/version = \"$major.$minor.$patch\"/" pyproject.toml

poetry build