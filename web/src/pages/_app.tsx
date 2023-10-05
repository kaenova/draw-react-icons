import AuthProvider from '@/lib/auth/AuthProvider';
import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';
import { Toaster } from 'react-hot-toast';
import { NextSeo } from 'next-seo';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <NextSeo
        title="Search the Icons you Imagine - Draw React Icons"
        description="Search your most wanted icons with your imagination using Draw React Icons"
        twitter={{
          handle: '@kaenovama',
          site: 'draw-react-icons.kaenova.my.id',
          cardType: 'summary',
        }}
        openGraph={{
          url: 'https://draw-react-icons.kaenova.my.id',
          title: 'Search the Icons you Imagine - Draw React Icons',
          description:
            'Search your most wanted icons with your imagination using Draw React Icons',
          images: [
            {
              url: 'https://draw-react-icons.kaenova.my.id/thumb.jpg',
              alt: 'Thumbnail Image Wide Draw React Icons',
              height: 630,
              width: 1200,
              type: 'image/jpg',
            },
            {
              url: 'https://draw-react-icons.kaenova.my.id/thumb_square.jpg',
              alt: 'Thumbnail Image Square Draw React Icons',
              height: 619,
              width: 619,
              type: 'image/jpg',
            },
            {
              url: 'https://draw-react-icons.kaenova.my.id/thumb_twitter.jpg',
              alt: 'Thumbnail Image Twitter Draw React Icons',
              height: 512,
              width: 1024,
              type: 'image/jpg',
            },
          ],
          siteName: 'DrawReactIcons',
        }}
      />
      <Toaster />
      <Component {...pageProps} />
    </AuthProvider>
  );
}
