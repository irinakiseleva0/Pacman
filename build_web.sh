pip install pygbag
python -m pygbag --build --width 800 --height 600 .
python post_build.py
echo "Done. Upload build/web to itch.io (800x600) or push to gh-pages."
