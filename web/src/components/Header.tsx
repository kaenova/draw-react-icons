import cn from '@/lib/cn';
import ReactIcon from './ReactIcon';

function Sponsor() {
  return (
    <div className="flex flex-col text-center space-y-4">
      <p className="text-sm font-bold">This application is powered by</p>
      <div className="flex flex-wrap justify-center gap-4 text-xs">
        <div className="flex flex-col justify-between items-center">
          <img
            className="h-5 object-cover w-min"
            src="/qdrant.png"
            alt="qdrant"
          />
          <p>For easy vector DB APIs</p>
        </div>
        <div className="flex flex-col justify-between items-center">
          <img
            className="h-5 object-cover w-min"
            src="/vercel.png"
            alt="vercel"
          />
          <p>For free frontend serving</p>
        </div>
        <div className="flex flex-col justify-between items-center">
          <img
            className="h-5 object-cover w-min"
            src="/idcloudhost.png"
            alt="idcloudhost"
          />
          <p>For cheap python backend and vector DB hosting</p>
          <p>(reach me out to help me find free python hosting)</p>
        </div>
      </div>
    </div>
  );
}

export default function Header({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <main className="flex min-h-screen flex-col items-center px-4 py-10 gap-4">
      <div
        key="title"
        className="flex flex-row items-center justify-center gap-4"
      >
        <ReactIcon />
        <div>
          <span className="text-xl text-brand">
            <span className={cn('text-4xl', 'font-[Caveat]')}>draw-</span>
            react-icons
          </span>
          <p className="text-sm">Search the Icons you Imagine</p>
        </div>
      </div>
      <div>
        <a href="https://github.com/kaenova/draw-react-icons">
          <img
            src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white"
            alt="github"
          />
        </a>
      </div>
      <div className={cn('flex flex-col max-w-4xl', className)}>{children}</div>
      <Sponsor />
    </main>
  );
}
