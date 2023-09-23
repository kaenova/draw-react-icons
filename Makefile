PROTOC_GEN_TS_PATH=web\\node_modules\\.bin\\protoc-gen-ts.cmd
RPC_NODE_OUT_DIR="web\\src\\rpc"

# Installing all lib
node-lib:
	npm install -g pnpm
	cd node-script/image-generator && npm install && cd ..
	cd web && pnpm install && cd ..

python-lib:
	cd py-script && pip install -r requirements.txt && cd ..

lib: node-lib python-lib

# Generate jpg image
image-gen: node-lib
	node node-script/image-generator/index.js --size 50 --color black --pad_size 50 

# Update Embedding
update-embed: python-lib
	python py-script/embed-gen.py

# Run Web
web: node-lib
	cd web && pnpm run dev

api:
	cd py-script && uvicorn api:app

# Generate Type for TS axios client (make sure the api is running)
# npm install openapi-typescript-codegen
api-type:
	curl http://127.0.0.1:8000/openapi.json > ./openapi.json
	openapi -i openapi.json -o ./web/src/lib/py-client
	rm ./openapi.json