import { Collection } from '@/lib/api/types';
import React from 'react';
import MainButton from './MainButton';

interface CollectionsPickerProps {
  collections: Collection[];
  initEmbedder?: string;
  initIndexing?: string;
  onChange?: (newCollection: string) => void;
}

interface CollectionData {
  [x: string]: string[];
}

function combineNameIndex(name: string, index: string): string {
  let newNameIndex = `Distance.${index.toUpperCase()}`;
  return `${name}_${newNameIndex}`;
}

function CollectionsPicker(props: CollectionsPickerProps) {
  const collectionData: CollectionData = {};

  props.collections.forEach((collection) => {
    if (collectionData[collection.embedder] === undefined) {
      collectionData[collection.embedder] = [];
    }
    collectionData[collection.embedder].push(
      collection.index.replace('Distance.', '').toLowerCase(),
    );
  });
  const allEmbedderName = Object.keys(collectionData);

  allEmbedderName.forEach((v) => {
    collectionData[v].sort();
  });

  const [Embedder, setEmbedder] = React.useState(
    props.initEmbedder || allEmbedderName.at(0) || '',
  );
  const [Indexing, setIndexing] = React.useState(props.initIndexing || '');
  const [IndexingChoices, setIndexingChoices] = React.useState<string[]>(
    Embedder ? collectionData[Embedder] : [],
  );

  function updateEmbedder(v: string) {
    setEmbedder(v);
    setIndexing('');
    setIndexingChoices(collectionData[v]);
    updateToOnChange(v, Indexing);
  }

  function updateIndexing(v: string) {
    setIndexing(v);
    updateToOnChange(Embedder, v);
  }

  function updateToOnChange(embedder: string, indexing: string) {
    if (!props.onChange) return;
    if (!embedder || !indexing) return;
    const fullName = combineNameIndex(embedder, indexing);
    props.onChange(fullName);
  }

  return (
    <div className="grid grid-flow-rwo grid-row-2 justify-center text-center gap-2">
      <div>
        <p>Available Methods:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {allEmbedderName.map((v) => (
            <MainButton
              key={v}
              isActive={v == Embedder}
              onClick={() => updateEmbedder(v)}
            >
              {v}
            </MainButton>
          ))}
        </div>
      </div>
      {IndexingChoices.length !== 0 && (
        <div>
          <p>Available Indexing:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {IndexingChoices.map((v) => (
              <MainButton
                isActive={v == Indexing}
                key={v}
                onClick={() => updateIndexing(v)}
              >
                {v}
              </MainButton>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CollectionsPicker;
