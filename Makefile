# Installing all lib
node-lib:
	npm install -g pnpm
	cd icons-image-generator && npm install && cd ..
	cd web && pnpm install && cd ..

python-lib:
	cd embedding-updater && pip install -r requirements.txt && cd ..

lib: node-lib python-lib

# Generate jpg image
image-gen: node-lib
	node icons-image-generator/index.js --size 50 --color black --pad_size 50 

# Update Embedding
update-embed: python-lib
	python embedding-updater/main.py

# Run Web
web: node-lib
	cd web && pnpm run dev