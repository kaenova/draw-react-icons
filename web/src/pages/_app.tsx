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
        openGraph={{
          url: 'https://draw-react-icons.kaenova.my.id',
          title: 'Search the Icons you Imagine - Draw React Icons',
          description:
            'Search your most wanted icons with your imagination using Draw React Icons',
          images: [
            {
              url: '/thumb.jpg',
              alt: 'Thumbnail Image Wide Draw React Icons',
              height: 630,
              width: 1200,
              type: 'image/jpeg',
            },
            {
              url: '/thumb_square.jpg',
              alt: 'Thumbnail Image Square Draw React Icons',
              height: 619,
              width: 619,
              type: 'image/jpeg',
            },
            {
              url: '/thumb_square.jpg',
              alt: 'Thumbnail Image Twitter Draw React Icons',
              height: 512,
              width: 1024,
              type: 'image/jpeg',
            },
          ],
          siteName: 'DrawReactIcons',
        }}
        twitter={{
          handle: '@kaenovama',
          cardType: 'summary_large_image',
        }}
      />
      <Toaster />
      <Component {...pageProps} />
    </AuthProvider>
  );
}
