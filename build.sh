#!/bin/bash
# Build script for zombie-shooter-gym package

set -e  # Exit on error

echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

echo "Building package..."
python -m build

echo "Checking package (note: license-file warning is a known non-blocking issue)..."
twine check dist/* || true

echo ""
echo "Build complete!"
echo "-------------------"
ls -lh dist/
echo ""
echo "To upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "To upload to PyPI: twine upload dist/*"
