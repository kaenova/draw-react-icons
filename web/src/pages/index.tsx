import React from 'react';
import { ReactSketchCanvas, ReactSketchCanvasRef } from 'react-sketch-canvas';
import useDebounce from '../utils/useDebounce';
import HCaptcha from '@hcaptcha/react-hcaptcha';
import { useAuth } from '@/lib/auth/context';
import api from '@/lib/api';
import toast from 'react-hot-toast';
import LoadingWithTitle from '@/components/LoadingWithTitle';
import { InferGetServerSidePropsType } from 'next';
import { Collection } from '@/lib/api/types';
import MainButton from '@/components/MainButton';
import Results from '@/components/Results';
import Header from '@/components/Header';

export default function Home({
  collections,
}: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const debounceDelayMs = 1000;
  const canvasRef = React.useRef<null | ReactSketchCanvasRef>(null);
  const captchaRef = React.useRef<null | HCaptcha>(null);

  const [Base64Data, setBase64Data] = React.useState<string | null>(null);
  const [Collection, setCollection] = React.useState<null | string>(null);
  const debounceBase64Data = useDebounce(Base64Data, debounceDelayMs);
  const debounceCollection = useDebounce(Collection, debounceDelayMs);

  const auth = useAuth();
  const [AuthLoading, setAuthLoading] = React.useState(false);

  async function handleSubmit(): Promise<void> {
    if (!canvasRef.current) return;
    const data = await canvasRef.current.exportImage('jpeg'); // String base64
    setBase64Data(data);
  }

  async function handleReset() {
    if (!canvasRef.current) return;
    canvasRef.current.resetCanvas();
    setCollection(null);
  }

  async function captchaVerification(token: string, ekey: string) {
    setAuthLoading(true);
    try {
      const res = await api.post<string>('/auth/tokens', undefined, {
        params: { hCaptchaToken: token },
      });
      auth?.setToken(res.data);
      toast.success('Successfully authenticated');
    } catch (e) {
      console.error(e);
      toast.error('Failed to authenticate user');
    } finally {
      captchaRef.current?.resetCaptcha();
    }
    setAuthLoading(false);
  }

  if (!!!auth) {
    return <></>;
  }

  if (AuthLoading === null) {
    return (
      <Header>
        <LoadingWithTitle>Authenticating</LoadingWithTitle>
      </Header>
    );
  }

  if (auth?.isAuth === null) {
    return (
      <Header>
        <LoadingWithTitle>Initializing Application</LoadingWithTitle>
      </Header>
    );
  }

  return (
    <Header className="gap-4">
      <div className="relative">
        {!auth?.isAuth && (
          <div className="absolute w-full h-full backdrop-blur-sm bg-white/50 z-10 items-center justify-center flex flex-col space-y-2">
            <p className="text-center font-bold">
              Before you try, we need to authenticate that you're human :D
            </p>
            <HCaptcha
              ref={captchaRef}
              sitekey={process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY || ''}
              onVerify={captchaVerification}
            />
          </div>
        )}
        <div
          style={{
            scale: !auth?.isAuth ? '90%' : '100%',
          }}
          className="items-center justify-center flex flex-col space-y-4"
        >
          <p className="font-bold text-center">Draw Your Icon</p>
          <ReactSketchCanvas
            width="300px"
            height="300px"
            ref={canvasRef}
            strokeWidth={5}
            strokeColor="black"
            onStroke={handleSubmit}
          />
          <div className="flex flex-col items-center space-y-2">
            <p>Available Methods:</p>
            <div className="flex flex-wrap gap-2 justify-center items-center">
              {collections.map((v) => {
                return (
                  <MainButton
                    key={v.collectionName}
                    isActive={v.collectionName == Collection}
                    onClick={() => setCollection(v.collectionName)}
                  >
                    {v.collectionName}
                  </MainButton>
                );
              })}
            </div>
          </div>
          <MainButton
            onClick={handleReset}
            className="px-6 py-2 font-medium tracking-wide text-brand capitalize transition-colors duration-300 transform bg-brand-600 rounded-lg hover:bg-brand-500 focus:outline-none focus:ring focus:ring-brand-300 focus:ring-opacity-80 bg-inherit border border-brand-500 hover:text-white"
          >
            Reset
          </MainButton>
        </div>
      </div>
      <div className="min-h-[300px]">
        <Results
          base64Image={debounceBase64Data || ''}
          collectionName={debounceCollection || ''}
        />
      </div>
    </Header>
  );
}

export const getServerSideProps = async () => {
  const collections = (await api.get<Collection[]>('/collections')).data;
  return { props: { collections } };
};
