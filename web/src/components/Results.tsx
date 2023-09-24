// @ts-nocheck
import api from '@/lib/api';
import { Icon } from '@/lib/api/types';
import { useAuth } from '@/lib/auth/context';
import React from 'react';
import toast from 'react-hot-toast';
import { ALL_ICONS, getIcons } from '@/lib/icon';
import loadable from '@loadable/component';
import IconLoading from './IconLoading';

function IconComponent({ icon: Icon, name }) {
  function copyClipboard() {
    try {
      navigator.clipboard.writeText(name);
      toast.success('Icon name copied to clipboard');
    } catch (e) {
      toast.error('Failed to copy to clipboard');
    }
  }

  return (
    <button
      onClick={copyClipboard}
      className="bg-brand/20 rounded-md p-2 flex flex-col items-center hover:bg-brand/10"
    >
      <div className="bg-white rounded-md p-1">
        <Icon size={30} />
      </div>
      <p className="font-bold text-sm tracking-wide">{name}</p>
    </button>
  );
}

function SearchIconSet({ icon, iconNames }) {
  const IconSet = loadable.lib(() => getIcons(icon.id));
  iconNames = iconNames.map((v) => v.toLowerCase());

  return (
    <IconSet fallback={<IconLoading />}>
      {({ default: icons }) => {
        const found = Object.keys(icons).filter((name) => {
          return iconNames.includes(name.toLowerCase());
        });
        return (
          <>
            {found.map((name) => (
              <>
                <IconComponent key={name} name={name} icon={icons[name]} />
              </>
            ))}
          </>
        );
      }}
    </IconSet>
  );
}

export default function Results({
  base64Image,
  collectionName,
}: {
  base64Image: string;
  collectionName: string;
}) {
  // @ts-ignore
  const allIcons = ALL_ICONS;

  const auth = useAuth();
  if (auth?.isAuth != true) {
    return <></>;
  }

  if (!base64Image || !collectionName) {
    return (
      <div className="text-center">
        <p>Please draw and choose the available methods</p>
      </div>
    );
  }

  const [Icons, setIcons] = React.useState<'loading' | Icon[] | 'err'>(
    'loading',
  );

  async function fetchIcon() {
    setIcons('loading');
    try {
      const res = await api.post<Icon[]>('/collections/query', undefined, {
        params: {
          token: auth?.token,
          collectionName: collectionName,
          base64Image: base64Image,
          normalizeImage: true,
          invertImage: true,
          limit: 20,
        },
      });
      setIcons(res.data);
    } catch (e) {
      toast.error('Failed to fetch related icon');
      setIcons('err');
    }
  }

  React.useEffect(() => {
    if (!!!auth?.isAuth) return;
    fetchIcon();
  }, [base64Image, collectionName]);

  if (Icons == 'loading') {
    return (
      <div className="flex flex-wrap justify-center gap-4">
        {Array(allIcons.length)
          .fill(0)
          .map((_) => (
            <IconLoading />
          ))}
      </div>
    );
  }

  if (Icons == 'err') {
    return <div className="text-center">Error, please try again</div>;
  }

  const iconNames = Icons.map((v) => v.iconName);

  return (
    <div className="flex flex-wrap gap-4 justify-center">
      {allIcons.map((icon) => (
        <SearchIconSet key={icon.id} icon={icon} iconNames={iconNames} />
      ))}
    </div>
  );
}
