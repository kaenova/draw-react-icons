import React from 'react';
import ReactIcon from '../components/ReactIcon';
import { twMerge } from 'tailwind-merge';
import { Caveat } from 'next/font/google';
import { ReactSketchCanvas, ReactSketchCanvasRef } from 'react-sketch-canvas';
import useDebounce from '../utils/useDebounce';

const caveat = Caveat({ subsets: ['latin'] });

function Results({
  base64Image
}: {
  base64Image: string
}) {
  return (
    <div className='break-all'>{base64Image}</div>
  )
}


export default function Home() {
  const debounceDelayMs = 1000
  const canvasRef = React.useRef<null | ReactSketchCanvasRef>(null)

  const [Base64Data, setBase64Data] = React.useState<string | null>(null)
  const debounceBase64Data = useDebounce(Base64Data, debounceDelayMs)

  async function handleSubmit() {
    if (!canvasRef.current) return
    const data = await canvasRef.current.exportImage('jpeg') // String base64
    setBase64Data(data)
  }

  async function handleReset() {
    if (!canvasRef.current) return
    canvasRef.current.resetCanvas()
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-24 gap-5">
      <div className="flex flex-row items-center gap-4">
        <ReactIcon />
        <span className="text-2xl text-brand">
          <span className={twMerge(caveat.className, 'text-4xl')}>draw-</span>
          react-icons
        </span>
      </div>
      <div>
        <p className='font-bold text-center'>Draw Your Icon</p>
        <ReactSketchCanvas
          width="300px"
          height="300px"
          ref={canvasRef}
          strokeWidth={5}
          strokeColor="black"
          onStroke={handleSubmit}
        />
      </div>
      <div className='flex flex-row gap-2'>
        <button onClick={handleReset} className="px-6 py-2 font-medium tracking-wide text-brand capitalize transition-colors duration-300 transform bg-brand-600 rounded-lg hover:bg-brand-500 focus:outline-none focus:ring focus:ring-brand-300 focus:ring-opacity-80 bg-inherit border border-brand-500 hover:text-white">
          Reset
        </button>
      </div>
      <div>
        {
          debounceBase64Data &&
          <Results base64Image={debounceBase64Data || ""} />
        }
      </div>
    </main>
  );
}
