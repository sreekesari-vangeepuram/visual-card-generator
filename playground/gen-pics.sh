#!/bin/bash

if ! [ -d "visual_cards" ]; then
	mkdir visual_cards
fi

for color in $(cat ./color_codes.txt); do
	python ./example.py ../etc/profile_pic.jpg "$color"
	mv ./visual_card.png "./visual_cards/$color.png"
done
