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
	cd py-script && python api.py

gen-grpc:
	mkdir py-script/rpc
	touch py-script/rpc/__init__.py
	python -m grpc_tools.protoc -I./proto --python_out=./py-script/rpc --pyi_out=./py-script/rpc --grpc_python_out=./py-script/rpc ./proto/*.proto
	sed -i 's/import \(\w\+\)_pb2 as \(\w\+\)__pb2/from . import \1_pb2 as \2__pb2/' py-script/rpc/*_grpc.py

# You need to install grpcui and reflection on python
# https://github.com/fullstorydev/grpcui
# https://github.com/grpc/grpc/blob/master/doc/python/server_reflection.md
grpc-ui:
	grpcui -plaintext localhost:1323