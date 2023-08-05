# Installing all lib
node-lib:
	cd icons-image-generator && npm install && cd ..

python-lib:
	cd embedding-updater && pip install -r requirements.txt && cd ..

lib: node-lib python-lib

# Generate jpg image
image-gen: node-lib
	node icons-image-generator/index.js --size 50 --color black --pad_size 50 