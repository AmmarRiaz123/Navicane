#!/bin/bash

echo "Removing redundant files..."

# Remove redundant download scripts
rm -f download_model_curl.sh
rm -f quick_download_model.sh
rm -f QUICK_MODEL_DOWNLOAD.txt

# Remove redundant setup script
rm -f quick_setup.sh

# Remove merged documentation
rm -f CAMERA_TROUBLESHOOTING.md

echo "✓ Cleanup complete!"
echo ""
echo "Remaining files:"
ls -1 *.sh *.md | sort
