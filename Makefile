# Installing all lib
node-lib:
	cd icons-image-generator && npm install && cd ..

lib: node-lib

# Generate jpg image
image-gen: node-lib
	node icons-image-generator/index.js --size 50 --color black --pad_size 50 