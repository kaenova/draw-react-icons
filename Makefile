# Installing all lib
lib:
	cd icons-image-generator && npm install

# Generate jpg image
image-gen: lib
	node icons-image-generator/index.js --size 50 --color black --pad_size 100